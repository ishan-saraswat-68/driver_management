from app.config import supabase
from datetime import datetime


class DriverRepository:

    def get_driver(self, driver_id: str):
        """
        Fetch driver sentiment record.
        Returns None if not found.
        """
        response = supabase.table("driver_sentiment") \
            .select("*") \
            .eq("driver_id", driver_id) \
            .execute()

        if response.data:
            return response.data[0]

        return None

    def create_driver(self, driver_id: str, score: float):
        """
        Create new driver sentiment record.
        """
        data = {
            "driver_id": driver_id,
            "score": score,
            "total_count": 1,
            "last_updated": datetime.utcnow().isoformat()
        }

        supabase.table("driver_sentiment").insert(data).execute()

        return data

    def update_driver(self, driver_id: str, new_score: float, total_count: int):
        """
        Update driver sentiment score and count.
        """
        data = {
            "score": new_score,
            "total_count": total_count,
            "last_updated": datetime.utcnow().isoformat()
        }

        supabase.table("driver_sentiment") \
            .update(data) \
            .eq("driver_id", driver_id) \
            .execute()

        return data

    def update_alert_timestamp(self, driver_id: str):
        """
        Update last alert time.
        """
        supabase.table("driver_sentiment") \
            .update({
                "last_alert_at": datetime.utcnow().isoformat()
            }) \
            .eq("driver_id", driver_id) \
            .execute()