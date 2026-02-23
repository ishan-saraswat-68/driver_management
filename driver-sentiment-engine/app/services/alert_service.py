from datetime import datetime, timedelta
import requests
import os
from app.repositories.driver_repository import DriverRepository
from app.config import THRESHOLD, COOLDOWN_HOURS, SLACK_WEBHOOK_URL

THRESHOLD = -0.5
COOLDOWN_HOURS = 24

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")


class AlertService:

    def __init__(self):
        self.repo = DriverRepository()

    def check_and_alert(self, driver_id: str, score: float):

        if score >= THRESHOLD:
            return

        driver = self.repo.get_driver(driver_id)
        if driver is None:
            return

        last_alert_at = driver.get("last_alert_at")
        now = datetime.utcnow()

        if last_alert_at is None:
            self.send_alert(driver_id, score)
            self.repo.update_alert_timestamp(driver_id)
            return

        last_alert_time = datetime.fromisoformat(last_alert_at.replace("Z", ""))

        if now - last_alert_time > timedelta(hours=COOLDOWN_HOURS):
            self.send_alert(driver_id, score)
            self.repo.update_alert_timestamp(driver_id)

    def send_alert(self, driver_id: str, score: float):
        try:
            if not SLACK_WEBHOOK:
                from app.logger import logger
                logger.warning("Slack webhook not configured")
                return

            message = {
                "text": f"🚨 ALERT: Driver {driver_id} score dropped to {score}"
            }

            response = requests.post(SLACK_WEBHOOK, json=message)

            if response.status_code != 200:
                print("Slack alert failed:", response.text)

        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")