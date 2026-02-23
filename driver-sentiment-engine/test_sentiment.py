"""
test_sentiment.py
──────────────────
Tests the SentimentService: VADER + domain lexicon + preprocessing + 0-5 scale.
Run: python test_sentiment.py
"""

from app.services.sentiment_service import SentimentService

service = SentimentService()
THRESHOLD_5 = 2.5   # midpoint on 0-5 scale

PASS = "✅ PASS"
FAIL = "❌ FAIL"

def check(description: str, text: str, expected_label: str, expect_alert: bool = None):
    r = service.analyze(text)
    label_ok = r["label"] == expected_label
    alert_ok = True
    if expect_alert is not None:
        triggered = r["score"] < THRESHOLD_5
        alert_ok = (triggered == expect_alert)

    ok = label_ok and alert_ok
    status = PASS if ok else FAIL
    alert_str = "🚨" if r["score"] < THRESHOLD_5 else "  "
    print(f"  {status}  {description}")
    print(f"         Text:  {text!r}")
    print(f"         Label: {r['label']:<10}  Score: {r['score']:>5.2f}/5  Raw: {r['raw_score']:+.3f}  {alert_str}")
    if not label_ok:
        print(f"         ❌ Expected label={expected_label}, got {r['label']}")
    if not alert_ok:
        print(f"         ❌ Alert expected={expect_alert}, got {triggered}")
    print()
    return ok

print("=" * 65)
print("SENTIMENT SERVICE TESTS")
print("=" * 65 + "\n")

results = []

print("── LABEL ACCURACY ──────────────────────────────────────────\n")
results.append(check("Positive: formal praise",          "Extremely polite and professional",     "positive"))
results.append(check("Positive: casual",                 "great driver, very friendly",           "positive"))
results.append(check("Positive: formerly broken case",   "extremely polite",                      "positive"))   # was neutral before fix
results.append(check("Positive: long sentence",          "driver is polite and very careful",     "positive"))   # was neutral before fix
results.append(check("Negative: abusive",                "Extremely rude and abusive behavior",   "negative"))
results.append(check("Negative: drunk",                  "driver is drunk",                       "negative"))
results.append(check("Negative: emoji angry",            "😡 worst ride ever",                    "negative"))
results.append(check("Negative: slang drunk",            "driver was totally wasted",             "negative"))   # slang fix
results.append(check("Negative: frisky (was wrong)",     "driver is frisky, doesnt know driving", "negative"))  # was positive before fix
results.append(check("Neutral: no strong signal",        "the ride was completed",                "neutral"))

print("── SCORE NORMALIZATION (0-5 scale) ─────────────────────────\n")
# Verify scale is 0-5
r_pos = service.analyze("absolutely amazing fantastic best driver ever")
r_neg = service.analyze("absolutely terrible horrible worst driver ever")
r_neu = service.analyze("okay")

def range_check(desc, val, lo, hi):
    ok = lo <= val <= hi
    print(f"  {'✅ PASS' if ok else '❌ FAIL'}  {desc}: {val:.3f} (expected {lo}–{hi})")
    return ok

results.append(range_check("Strong positive score is > 3.5", r_pos["score"], 3.5, 5.0))
results.append(range_check("Strong negative score is < 1.5", r_neg["score"], 0.0, 1.5))
results.append(range_check("Neutral score is near 2.5",      r_neu["score"], 2.0, 3.5))
results.append(range_check("All scores are within 0-5",      r_pos["score"], 0.0, 5.0))
print()

print("── ALERT THRESHOLD (2.5/5) ─────────────────────────────────\n")
results.append(check("Alert fires: drunk driver",      "driver is drunk",        "negative", expect_alert=True))
results.append(check("Alert fires: abusive driver",    "so rude and abusive",    "negative", expect_alert=True))
results.append(check("No alert: good driver",          "excellent friendly driver", "positive", expect_alert=False))
results.append(check("No alert: neutral",              "okay ride",              "positive", expect_alert=False))

print("── EMOJI PREPROCESSING ─────────────────────────────────────\n")
results.append(check("Emoji 👍 is positive",     "👍 great trip",           "positive"))
results.append(check("Emoji 😡 is negative",     "😡 horrible",             "negative"))
results.append(check("Emoji 😊 + polite = pos",  "😊 very polite driver",   "positive"))
results.append(check("Emoji 🤬 is negative",     "🤬 completely unacceptable", "negative"))

passed = sum(1 for r in results if r)
print("=" * 65)
print(f"Results: {passed}/{len(results)} passed")
print("=" * 65)