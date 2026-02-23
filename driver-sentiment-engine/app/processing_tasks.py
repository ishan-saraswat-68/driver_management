"""
processing_tasks.py
────────────────────
Background task worker. Runs in FastAPI's BackgroundTasks thread pool.
Thread-safe: services are stateless/DB-backed; only AlertService uses a lock.
Retry logic wraps DB operations to handle transient Supabase errors.
"""

import time
import threading
from app.services.sentiment_service import SentimentService
from app.services.driver_service import DriverService
from app.services.alert_service import AlertService
from app.config import supabase
from app.logger import logger

# ─── Service singletons ───────────────────────────────────────────────────────
# These are safe to share: SentimentService is read-only (VADER),
# DriverService & AlertService use only DB calls (no shared in-memory state
# except AlertService's internal lock which is already thread-safe).
_sentiment_service = SentimentService()
_driver_service = DriverService()
_alert_service = AlertService()

# ─── Retry config ─────────────────────────────────────────────────────────────
MAX_RETRIES = 3
RETRY_DELAY = 0.5   # seconds between retries


def _retry(fn, *args, **kwargs):
    """Call fn(*args, **kwargs) with up to MAX_RETRIES attempts."""
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_exc = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)   # exponential back-off
    raise last_exc


def process_feedback(feedback):
    """
    Background worker: called by FastAPI BackgroundTasks after API responds.
    Thread-safe — each invocation is independent except for AlertService lock.

    Flow:
      1. Preprocess + analyze sentiment
      2. Persist feedback row (with retry)
      3. Update driver's EMA score (with retry)
      4. Check and fire alerts (spam-protected internally)
    """
    driver_id = feedback.driver_id

    try:
        # ── 1. Sentiment Analysis ─────────────────────────────────────────
        sentiment_result = _sentiment_service.analyze(feedback.text)
        score   = sentiment_result["score"]        # 0–5 normalized
        raw     = sentiment_result["raw_score"]    # VADER -1..+1
        label   = sentiment_result["label"]

        logger.info(
            f"[{driver_id}] Sentiment — label={label}, "
            f"score={score:.3f}/5 (raw={raw:+.3f})"
        )

        # ── 2. Store feedback row (retry on transient DB error) ───────────
        def _insert_feedback():
            supabase.table("feedback").insert({
                "driver_id":            driver_id,
                "trip_id":              feedback.trip_id,
                "text":                 feedback.text,
                "sentiment":            score,       # normalized 0–5
                "sentiment_label":      label,
                "entity_type":          feedback.entity_type,
                "external_feedback_id": feedback.external_feedback_id,
            }).execute()

        _retry(_insert_feedback)

        # ── 3. Update driver EMA (retry on transient DB error) ────────────
        updated_score = _retry(
            _driver_service.update_driver_score,
            driver_id=driver_id,
            new_score=score
        )

        logger.info(f"[{driver_id}] EMA score updated → {updated_score:.3f}/5")

        # ── 4. Alert check (spam-protected by AlertService) ───────────────
        _alert_service.check_and_alert(
            driver_id=driver_id,
            score=updated_score
        )

    except Exception as e:
        logger.error(
            f"[{driver_id}] Background processing failed after {MAX_RETRIES} retries: {e}",
            exc_info=True
        )