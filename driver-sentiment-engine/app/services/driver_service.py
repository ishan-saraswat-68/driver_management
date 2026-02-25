from app.repositories.driver_repository import DriverRepository

ALPHA = 0.2  # EMA smoothing factor


class DriverService:

    def __init__(self):
        self.repo = DriverRepository()

    def update_driver_score(self, driver_id: str, new_score: float):
        driver = self.repo.get_driver(driver_id)

        if driver is None:
            self.repo.create_driver(driver_id, new_score)
            return new_score

        old_score   = driver["score"]
        total_count = driver["total_count"]
        updated     = ALPHA * new_score + (1 - ALPHA) * old_score

        self.repo.update_driver(
            driver_id=driver_id,
            new_score=updated,
            total_count=total_count + 1
        )

        return updated