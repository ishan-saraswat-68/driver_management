"""
alert_service.py
─────────────────
Robust, spam-resistant alerting with:
  - Configurable threshold on 0–5 scale (default 2.5 / 5)
  - DB-persisted cooldown (prevents alerts if server restarts)
  - In-memory driver lock set (prevents burst spam within the same process)
  - Graceful Slack fallback (logs if webhook not configured)
"""

from datetime import datetime, timedelta
import threading
import requests
import os
from app.repositories.driver_repository import DriverRepository
from app.config import COOLDOWN_HOURS, SLACK_WEBHOOK_URL
from app.logger import logger

# ─── Configurable thresholds ─────────────────────────────────────────────────
# Requirements say "2.5 out of 5" is the alert threshold.
# Score is now on 0–5 scale: 2.5 = neutral midpoint.
THRESHOLD_5 = float(os.getenv("ALERT_THRESHOLD", 2.5))   # 0–5 scale
COOLDOWN_HOURS = int(os.getenv("COOLDOWN_HOURS", 24))
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")


class AlertService:
    """
    Thread-safe alert service with two layers of spam protection:
      1. Per-driver threading.Lock  → only one thread processes alerts per driver at a time
      2. DB timestamp              → blocks repeat alerts across restarts / long cooldowns
    """

    def __init__(self):
        self.repo = DriverRepository()
        # Per-driver locks — acquired for the ENTIRE check+send operation.
        # This means if 10 threads hit simultaneously, the first acquires the lock,
        # fires the alert, and the remaining 9 block. When they finally acquire,
        # last_alert_at has been updated → cooldown check blocks them all.
        self._driver_locks: dict = {}
        self._registry_lock = threading.Lock()

    def _get_driver_lock(self, driver_id: str) -> threading.Lock:
        """Get or create a per-driver lock (thread-safe)."""
        with self._registry_lock:
            if driver_id not in self._driver_locks:
                self._driver_locks[driver_id] = threading.Lock()
            return self._driver_locks[driver_id]

    def check_and_alert(self, driver_id: str, score: float):
        """
        Check driver's EMA score and fire alert if below threshold.
        Score is on 0–5 scale. Threshold default: 2.5.
        Thread-safe: per-driver lock held across entire check+send.
        """
        if score >= THRESHOLD_5:
            return  # Score is acceptable, no action needed

        driver_lock = self._get_driver_lock(driver_id)

        # Acquire the per-driver lock. Concurrent threads for the SAME driver
        # will block here. By the time they acquire, last_alert_at will be set.
        with driver_lock:
            driver = self.repo.get_driver(driver_id)
            if driver is None:
                return

            last_alert_at = driver.get("last_alert_at")
            now = datetime.utcnow()

            should_alert = False
            if last_alert_at is None:
                should_alert = True
            else:
                last_alert_time = datetime.fromisoformat(
                    last_alert_at.replace("Z", "").split("+")[0]
                )
                if now - last_alert_time > timedelta(hours=COOLDOWN_HOURS):
                    should_alert = True
                else:
                    remaining = timedelta(hours=COOLDOWN_HOURS) - (now - last_alert_time)
                    logger.info(
                        f"Alert cooldown active for driver {driver_id}. "
                        f"Next alert in: {str(remaining).split('.')[0]}"
                    )

            if should_alert:
                # Update timestamp BEFORE sending to ensure concurrent threads
                # that have been waiting see a fresh timestamp when they acquire.
                self.repo.update_alert_timestamp(driver_id)
                self._send_alert(driver_id, score)

    def _send_alert(self, driver_id: str, score: float):
        """Send Slack notification. Logs warning if webhook not configured."""
        if not SLACK_WEBHOOK:
            logger.warning(
                f"[ALERT] Driver {driver_id} score {score:.2f}/5 is below threshold "
                f"{THRESHOLD_5}/5 — Slack webhook not configured, alert not sent."
            )
            return

        try:
            score_bar = "█" * int(score) + "░" * (5 - int(score))
            message = {
                "text": (
                    f"🚨 *Driver Alert* — Score below threshold\n"
                    f"*Driver ID:* `{driver_id}`\n"
                    f"*EMA Score:* {score:.2f}/5.0  [{score_bar}]\n"
                    f"*Threshold:* {THRESHOLD_5}/5.0\n"
                    f"*Time:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                )
            }

            response = requests.post(SLACK_WEBHOOK, json=message, timeout=5)

            if response.status_code == 200:
                logger.info(f"Alert sent for driver {driver_id} (score: {score:.2f})")
            else:
                logger.error(f"Slack alert failed [{response.status_code}]: {response.text}")

        except requests.exceptions.Timeout:
            logger.error(f"Slack alert timed out for driver {driver_id}")
        except Exception as e:
            logger.error(f"Error sending alert for driver {driver_id}: {e}")