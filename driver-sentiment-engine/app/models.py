from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    driver_id: str
    trip_id: str
    text: str
    external_feedback_id: str | None = None