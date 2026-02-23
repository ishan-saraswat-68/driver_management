from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.services.sentiment_service import SentimentService
from app.services.driver_service import DriverService
from app.services.alert_service import AlertService
from app.config import supabase

app = FastAPI()

# Initialize services
sentiment_service = SentimentService()
driver_service = DriverService()
alert_service = AlertService()


# ----------------------
# Health Check Endpoint
# ----------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ----------------------
# Feedback Input Model
# ----------------------
class FeedbackRequest(BaseModel):
    driver_id: str
    trip_id: str
    text: str
    external_feedback_id: str | None = None


# ----------------------
# Feedback Endpoint
# ----------------------
@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    try:
        # 1️⃣ Analyze sentiment
        sentiment_result = sentiment_service.analyze(feedback.text)
        score = sentiment_result["score"]
        label = sentiment_result["label"]

        # 2️⃣ Insert feedback into DB
        supabase.table("feedback").insert({
            "driver_id": feedback.driver_id,
            "trip_id": feedback.trip_id,
            "text": feedback.text,
            "sentiment": score,
            "sentiment_label": label,
            "external_feedback_id": feedback.external_feedback_id
        }).execute()

        # 3️⃣ Update driver's EMA score
        updated_score = driver_service.update_driver_score(
            driver_id=feedback.driver_id,
            new_score=score
        )

        # 4️⃣ Check alert condition
        alert_service.check_and_alert(
            driver_id=feedback.driver_id,
            score=updated_score
        )

        # 5️⃣ Return response
        return {
            "message": "Feedback processed successfully",
            "sentiment_score": score,
            "sentiment_label": label,
            "updated_driver_score": updated_score
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



