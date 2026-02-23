"""
test_ema.py
────────────
Tests DriverService EMA (Exponential Moving Average) on the 0-5 scale.
Run: python test_ema.py

Uses a mock repository — no live DB required.
"""

from unittest.mock import MagicMock
from app.services.driver_service import DriverService, ALPHA

PASS = "✅ PASS"
FAIL = "❌ FAIL"

print("=" * 60)
print("EMA SCORE TESTS (0-5 scale)")
print("=" * 60 + "\n")

results = []

def make_service(existing_score=None, existing_count=None):
    svc = DriverService()
    svc.repo = MagicMock()
    if existing_score is None:
        svc.repo.get_driver.return_value = None   # new driver
    else:
        svc.repo.get_driver.return_value = {
            "score": existing_score,
            "total_count": existing_count
        }
    svc.repo.create_driver = MagicMock()
    svc.repo.update_driver = MagicMock()
    return svc


# ─── Test 1: New driver → score = first feedback ────────────────────────────
svc = make_service()
result = svc.update_driver_score("drv_new", new_score=4.0)
ok = abs(result - 4.0) < 0.001
print(f"  {PASS if ok else FAIL}  New driver → first score is stored directly")
print(f"         Expected: 4.0, Got: {result:.4f}\n")
results.append(ok)


# ─── Test 2: EMA formula (ALPHA=0.2) ────────────────────────────────────────
# new_ema = 0.2 * new + 0.8 * old
svc2 = make_service(existing_score=3.0, existing_count=5)
result2 = svc2.update_driver_score("drv_002", new_score=1.0)
expected2 = ALPHA * 1.0 + (1 - ALPHA) * 3.0   # 0.2*1 + 0.8*3 = 2.6
ok2 = abs(result2 - expected2) < 0.001
print(f"  {PASS if ok2 else FAIL}  EMA: old=3.0, new=1.0 → 0.2×1.0 + 0.8×3.0 = {expected2:.2f}")
print(f"         Expected: {expected2:.4f}, Got: {result2:.4f}\n")
results.append(ok2)


# ─── Test 3: Multiple consecutive feedbacks decay correctly ─────────────────
svc3 = make_service()
scores = [5.0, 5.0, 5.0, 0.0, 0.0, 0.0]  # good then suddenly bad
ema = None
for i, s in enumerate(scores):
    if i == 0:
        svc3.repo.get_driver.return_value = None
    else:
        svc3.repo.get_driver.return_value = {"score": ema, "total_count": i}
    ema = svc3.update_driver_score("drv_003", new_score=s)
    print(f"  Feedback {i+1}: input={s:.1f}  →  EMA={ema:.4f}/5")

ok3 = 2.0 < ema < 3.5  # should still be between the two extremes after decay
print(f"  {PASS if ok3 else FAIL}  EMA after 3 good + 3 bad feedbacks is between 2.0–3.5 (got {ema:.4f})\n")
results.append(ok3)


# ─── Test 4: Score stays in 0-5 range ───────────────────────────────────────
# All edge case scores on 0-5 scale
edge_scores = [0.0, 5.0, 2.5, 0.001, 4.999]
in_range = True
svc4 = make_service(existing_score=2.5, existing_count=10)
for s in edge_scores:
    svc4.repo.get_driver.return_value = {"score": 2.5, "total_count": 10}
    r = svc4.update_driver_score("drv_edge", new_score=s)
    if not (0.0 <= r <= 5.0):
        in_range = False
        print(f"  ❌ Out of range for input {s}: got {r}")

print(f"  {PASS if in_range else FAIL}  EMA always stays within 0.0–5.0 range for all inputs\n")
results.append(in_range)


passed = sum(results)
print("=" * 60)
print(f"Results: {passed}/{len(results)} passed")
print("=" * 60)
