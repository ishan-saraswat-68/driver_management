"""
test_alert_service.py
──────────────────────
Tests AlertService: threshold, cooldown, and burst-spam protection.
Run: python test_alert_service.py

NOTE: These tests mock the DB to avoid needing a live Supabase connection.
"""

import threading
import time
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from app.services.alert_service import AlertService, THRESHOLD_5, COOLDOWN_HOURS

PASS = "✅ PASS"
FAIL = "❌ FAIL"

def header(title):
    print(f"\n── {title} {'─' * (55 - len(title))}\n")

print("=" * 60)
print("ALERT SERVICE TESTS")
print("=" * 60)


# ─── Test 1: Score above threshold → no alert ──────────────────────────────
header("THRESHOLD: Score above 2.5 → no alert")

service = AlertService()
send_called = []

with patch.object(service, '_send_alert', side_effect=lambda *a, **kw: send_called.append(True)):
    service.repo = MagicMock()
    service.repo.get_driver.return_value = {"last_alert_at": None}
    service.check_and_alert("drv_001", score=3.5)   # 3.5 > 2.5 threshold

ok = len(send_called) == 0
print(f"  {PASS if ok else FAIL}  Score 3.5/5 above threshold {THRESHOLD_5} → alert NOT sent")
print(f"         Alert calls: {len(send_called)} (expected 0)\n")


# ─── Test 2: Score below threshold → alert fires ───────────────────────────
header("THRESHOLD: Score below 2.5 → alert fires")

service2 = AlertService()
calls2 = []

with patch.object(service2, '_send_alert', side_effect=lambda d, s: calls2.append((d, s))):
    service2.repo = MagicMock()
    service2.repo.get_driver.return_value = {"last_alert_at": None}
    service2.repo.update_alert_timestamp = MagicMock()
    service2.check_and_alert("drv_002", score=1.2)  # 1.2 < 2.5

ok = len(calls2) == 1 and calls2[0][0] == "drv_002"
print(f"  {PASS if ok else FAIL}  Score 1.2/5 below threshold {THRESHOLD_5} → alert SENT")
print(f"         Alert calls: {len(calls2)} (expected 1)\n")


# ─── Test 3: Cooldown — recent alert → no repeat ───────────────────────────
header("COOLDOWN: Alert within cooldown period → suppressed")

service3 = AlertService()
calls3 = []
recent_alert = (datetime.utcnow() - timedelta(hours=1)).isoformat()

with patch.object(service3, '_send_alert', side_effect=lambda d, s: calls3.append(d)):
    service3.repo = MagicMock()
    service3.repo.get_driver.return_value = {"last_alert_at": recent_alert}
    service3.repo.update_alert_timestamp = MagicMock()
    service3.check_and_alert("drv_003", score=0.5)

ok = len(calls3) == 0
print(f"  {PASS if ok else FAIL}  Alert 1h ago (cooldown={COOLDOWN_HOURS}h) → NOT sent again")
print(f"         Alert calls: {len(calls3)} (expected 0)\n")


# ─── Test 4: Cooldown expired → alert fires again ──────────────────────────
header("COOLDOWN: Alert after cooldown expires → fires")

service4 = AlertService()
calls4 = []
old_alert = (datetime.utcnow() - timedelta(hours=25)).isoformat()

with patch.object(service4, '_send_alert', side_effect=lambda d, s: calls4.append(d)):
    service4.repo = MagicMock()
    service4.repo.get_driver.return_value = {"last_alert_at": old_alert}
    service4.repo.update_alert_timestamp = MagicMock()
    service4.check_and_alert("drv_004", score=0.5)

ok = len(calls4) == 1
print(f"  {PASS if ok else FAIL}  Alert 25h ago (cooldown={COOLDOWN_HOURS}h) → SENT")
print(f"         Alert calls: {len(calls4)} (expected 1)\n")


# ─── Test 5: Burst spam — 10 threads hit simultaneously → only 1 alert ─────
header("BURST SPAM: 10 concurrent calls → only 1 alert fires")

service5 = AlertService()
concurrent_calls = []
calls_lock = threading.Lock()

# Simulate real DB: after timestamp is written, return it on subsequent reads.
alert_timestamp_store = {"drv_005": None}

def fake_get_driver(driver_id):
    return {"last_alert_at": alert_timestamp_store.get(driver_id)}

def fake_update_timestamp(driver_id):
    # Simulates DB write — all subsequent get_driver calls will see this
    alert_timestamp_store[driver_id] = datetime.utcnow().isoformat()

def mock_send(driver_id, score):
    with calls_lock:
        concurrent_calls.append(driver_id)

service5.repo = MagicMock()
service5.repo.get_driver.side_effect = fake_get_driver
service5.repo.update_alert_timestamp.side_effect = fake_update_timestamp

with patch.object(service5, '_send_alert', side_effect=mock_send):
    threads = [
        threading.Thread(target=service5.check_and_alert, args=("drv_005", 0.8))
        for _ in range(10)
    ]
    for t in threads: t.start()
    for t in threads: t.join()

ok = len(concurrent_calls) == 1
print(f"  {PASS if ok else FAIL}  10 simultaneous bad feedbacks → {len(concurrent_calls)} alert(s) (expected 1)")
print(f"         Calls: {concurrent_calls}\n")


# ─── Summary ────────────────────────────────────────────────────────────────
all_tests = [
    len(send_called) == 0,
    len(calls2) == 1,
    len(calls3) == 0,
    len(calls4) == 1,
    len(concurrent_calls) == 1
]
passed = sum(all_tests)
print("=" * 60)
print(f"Results: {passed}/{len(all_tests)} passed")
print("=" * 60)
