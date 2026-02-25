from app.config import supabase
from datetime import datetime


class DriverRepository:

    def get_driver(self, driver_id: str):
        res = supabase.table("driver_sentiment") \
            .select("*") \
            .eq("driver_id", driver_id) \
            .execute()
        return res.data[0] if res.data else None

    def create_driver(self, driver_id: str, score: float):
        data = {
            "driver_id":    driver_id,
            "score":        score,
            "total_count":  1,
            "last_updated": datetime.utcnow().isoformat()
        }
        supabase.table("driver_sentiment").insert(data).execute()
        return data

    def update_driver(self, driver_id: str, new_score: float, total_count: int):
        data = {
            "score":        new_score,
            "total_count":  total_count,
            "last_updated": datetime.utcnow().isoformat()
        }
        supabase.table("driver_sentiment") \
            .update(data) \
            .eq("driver_id", driver_id) \
            .execute()
        return data

    def update_alert_timestamp(self, driver_id: str):
        supabase.table("driver_sentiment") \
            .update({"last_alert_at": datetime.utcnow().isoformat()}) \
            .eq("driver_id", driver_id) \
            .execute()