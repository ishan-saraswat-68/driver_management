from app.services.driver_service import DriverService

service = DriverService()

driver_id = "11111111-1111-1111-1111-111111111111"

# Simulate multiple feedback scores
scores = [0.8, 0.7, -0.6, 0.9, -0.9]

for score in scores:
    updated = service.update_driver_score(driver_id, score)
    print(f"New input: {score} → Updated EMA: {updated}")