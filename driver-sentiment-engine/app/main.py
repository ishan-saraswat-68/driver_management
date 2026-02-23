from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.services.sentiment_service import SentimentService
from app.services.driver_service import DriverService
from app.services.alert_service import AlertService
from app.processing_tasks import process_feedback
from app.models import FeedbackRequest
from app.config import supabase

app = FastAPI(title="Driver Sentiment Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
sentiment_service = SentimentService()
driver_service = DriverService()
alert_service = AlertService()


# ----------------------
# Health Check
# ----------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ----------------------
# Submit Feedback (Async)
# ----------------------
@app.post("/feedback", status_code=202)
def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks
):
    # 🔐 Idempotency Check — prevent duplicate feedback processing
    if feedback.external_feedback_id:
        existing = supabase.table("feedback") \
            .select("id") \
            .eq("external_feedback_id", feedback.external_feedback_id) \
            .execute()

        if existing.data:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Duplicate feedback ignored",
                    "data": None,
                    "error": None
                }
            )

    # 🚀 Queue background job — respond immediately to caller
    background_tasks.add_task(process_feedback, feedback)

    return {
        "success": True,
        "message": "Feedback accepted for processing",
        "data": None,
        "error": None
    }


# ----------------------
# Get Driver Stats
# ----------------------
@app.get("/driver/{driver_id}")
def get_driver(driver_id: str):
    try:
        driver = driver_service.repo.get_driver(driver_id)

        if driver is None:
            raise HTTPException(status_code=404, detail="Driver not found")

        return {
            "success": True,
            "data": {
                "driver_id": driver["driver_id"],
                "score": driver["score"],
                "total_feedback_count": driver["total_count"],
                "last_updated": driver["last_updated"],
                "last_alert_at": driver.get("last_alert_at")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------
# Get All Drivers (for Dashboard)
# ----------------------
@app.get("/drivers")
def get_all_drivers():
    try:
        response = supabase.table("driver_sentiment") \
            .select("*") \
            .order("score", desc=False) \
            .execute()

        return {
            "success": True,
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
