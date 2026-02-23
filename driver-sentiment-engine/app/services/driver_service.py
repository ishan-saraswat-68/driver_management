from app.repositories.driver_repository import DriverRepository

ALPHA = 0.2


class DriverService:

    def __init__(self):
        self.repo = DriverRepository()

    def update_driver_score(self, driver_id: str, new_score: float):
        """
        Update driver's EMA score.
        If driver does not exist → create.
        If exists → apply EMA formula.
        """

        driver = self.repo.get_driver(driver_id)

        # Case 1: Driver does not exist
        if driver is None:
            self.repo.create_driver(driver_id, new_score)
            return new_score

        # Case 2: Driver exists
        old_score = driver["score"]
        total_count = driver["total_count"]

        # Apply EMA formula
        updated_score = ALPHA * new_score + (1 - ALPHA) * old_score

        self.repo.update_driver(
            driver_id=driver_id,
            new_score=updated_score,
            total_count=total_count + 1
        )

        return updated_score