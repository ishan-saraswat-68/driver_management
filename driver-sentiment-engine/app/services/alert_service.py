import os
from app.repositories.driver_repository import DriverRepository
from app.config import COOLDOWN_HOURS, SLACK_WEBHOOK_URL
from app.logger import logger
from datetime import datetime, timedelta
import threading
import requests

THRESHOLD_5  = float(os.getenv("ALERT_THRESHOLD", 2.5))
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")


class AlertService:

    def __init__(self):
        self.repo = DriverRepository()
        self._driver_locks: dict = {}
        self._registry_lock = threading.Lock()

    def _get_driver_lock(self, driver_id: str) -> threading.Lock:
        with self._registry_lock:
            if driver_id not in self._driver_locks:
                self._driver_locks[driver_id] = threading.Lock()
            return self._driver_locks[driver_id]

    def check_and_alert(self, driver_id: str, score: float):
        if score >= THRESHOLD_5:
            return

        with self._get_driver_lock(driver_id):
            driver = self.repo.get_driver(driver_id)
            if driver is None:
                return

            last_alert_at = driver.get("last_alert_at")
            now = datetime.utcnow()

            if last_alert_at is None:
                should_alert = True
            else:
                last_time = datetime.fromisoformat(
                    last_alert_at.replace("Z", "").split("+")[0]
                )
                should_alert = (now - last_time) > timedelta(hours=COOLDOWN_HOURS)
                if not should_alert:
                    remaining = timedelta(hours=COOLDOWN_HOURS) - (now - last_time)
                    logger.info(f"Alert cooldown for {driver_id}. Next in: {str(remaining).split('.')[0]}")

            if should_alert:
                self.repo.update_alert_timestamp(driver_id)
                self._send_alert(driver_id, score)

    def _send_alert(self, driver_id: str, score: float):
        if not SLACK_WEBHOOK:
            logger.warning(f"[ALERT] {driver_id} score {score:.2f}/5 below threshold {THRESHOLD_5}/5")
            return

        try:
            bar = "█" * int(score) + "░" * (5 - int(score))
            payload = {"text": (
                f"🚨 *Driver Alert* — Score below threshold\n"
                f"*Driver:* `{driver_id}`\n"
                f"*Score:* {score:.2f}/5  [{bar}]\n"
                f"*Threshold:* {THRESHOLD_5}/5\n"
                f"*Time:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
            )}
            res = requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
            if res.status_code == 200:
                logger.info(f"Alert sent for {driver_id}")
            else:
                logger.error(f"Slack alert failed [{res.status_code}]: {res.text}")
        except requests.exceptions.Timeout:
            logger.error(f"Slack alert timed out for {driver_id}")
        except Exception as e:
            logger.error(f"Alert error for {driver_id}: {e}")