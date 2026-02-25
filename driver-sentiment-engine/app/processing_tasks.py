import time
import threading
from app.services.sentiment_service import SentimentService
from app.services.driver_service import DriverService
from app.services.alert_service import AlertService
from app.config import supabase
from app.logger import logger

# Service singletons
_sentiment_service = SentimentService()
_driver_service = DriverService()
_alert_service = AlertService()

MAX_RETRIES = 3
RETRY_DELAY = 0.5


def _retry(fn, *args, **kwargs):
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_exc = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
    raise last_exc


def process_feedback(feedback):
    driver_id = feedback.driver_id

    try:
        # 1. Analyze sentiment
        result = _sentiment_service.analyze(feedback.text)
        score = result["score"]
        raw   = result["raw_score"]
        label = result["label"]

        logger.info(f"[{driver_id}] label={label}, score={score:.3f}/5 (raw={raw:+.3f})")

        # 2. Save feedback row
        def _insert():
            supabase.table("feedback").insert({
                "driver_id":            driver_id,
                "trip_id":              feedback.trip_id,
                "text":                 feedback.text,
                "sentiment":            score,
                "sentiment_label":      label,
                "entity_type":          feedback.entity_type,
                "external_feedback_id": feedback.external_feedback_id,
            }).execute()

        _retry(_insert)

        # 3. Update EMA score
        updated_score = _retry(
            _driver_service.update_driver_score,
            driver_id=driver_id,
            new_score=score
        )

        logger.info(f"[{driver_id}] EMA → {updated_score:.3f}/5")

        # 4. Alert if below threshold
        _alert_service.check_and_alert(driver_id=driver_id, score=updated_score)

    except Exception as e:
        logger.error(f"[{driver_id}] Failed: {e}", exc_info=True)