from app.services.sentiment_service import SentimentService
from app.services.driver_service import DriverService
from app.services.alert_service import AlertService
from app.config import supabase
from app.logger import logger


sentiment_service = SentimentService()
driver_service = DriverService()
alert_service = AlertService()


def process_feedback(feedback):
    """
    Heavy processing logic executed in background.
    """

    try:
        # 1️⃣ Sentiment Analysis
        sentiment_result = sentiment_service.analyze(feedback.text)
        score = sentiment_result["score"]
        label = sentiment_result["label"]

        # 2️⃣ Store Feedback
        supabase.table("feedback").insert({
            "driver_id": feedback.driver_id,
            "trip_id": feedback.trip_id,
            "text": feedback.text,
            "sentiment": score,
            "sentiment_label": label,
            "external_feedback_id": feedback.external_feedback_id
        }).execute()

        # 3️⃣ Update EMA
        updated_score = driver_service.update_driver_score(
            driver_id=feedback.driver_id,
            new_score=score
        )

        # 4️⃣ Check Alerts
        alert_service.check_and_alert(
            driver_id=feedback.driver_id,
            score=updated_score
        )

        logger.info(f"Processed feedback for driver {feedback.driver_id}")

    except Exception as e:
        logger.error(f"Background processing failed: {e}")