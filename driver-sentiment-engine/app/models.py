from pydantic import BaseModel
from typing import Literal


class FeedbackRequest(BaseModel):
    driver_id: str
    trip_id: str
    text: str
    entity_type: Literal["driver", "trip", "app", "marshal"] = "driver"
    external_feedback_id: str | None = None