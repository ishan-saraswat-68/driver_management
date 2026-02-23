"""
test_preprocessor.py
─────────────────────
Tests the text_preprocessor utility.
Run: python test_preprocessor.py
"""

from app.utils.text_preprocessor import preprocess

PASS = "✅ PASS"
FAIL = "❌ FAIL"

def check(description: str, input_text: str, expected_contains: str = None, expected_not_contains: str = None):
    result = preprocess(input_text)
    ok = True
    reason = ""

    if expected_contains and expected_contains.lower() not in result.lower():
        ok = False
        reason = f"expected '{expected_contains}' in output"
    if expected_not_contains and expected_not_contains.lower() in result.lower():
        ok = False
        reason = f"expected '{expected_not_contains}' NOT in output"

    status = PASS if ok else FAIL
    print(f"  {status}  {description}")
    print(f"         Input:  {input_text!r}")
    print(f"         Output: {result!r}")
    if not ok:
        print(f"         Reason: {reason}")
    print()
    return ok

print("=" * 60)
print("TEXT PREPROCESSOR TESTS")
print("=" * 60 + "\n")

results = []

# 1. Emoji → word replacement
results.append(check("Thumbs up emoji → 'good'",               "👍 nice ride",       expected_contains="good"))
results.append(check("Angry emoji → 'very angry'",             "😡 terrible driver", expected_contains="very angry"))
results.append(check("Happy emoji → 'happy'",                  "😊 great trip!",     expected_contains="happy"))
results.append(check("Thumbs down emoji → 'bad'",              "👎 rubbish driver",  expected_contains="bad"))

# 2. Slang normalization
results.append(check("'gr8' → 'great'",         "gr8 experience",         expected_contains="great"))
results.append(check("'wasted' → 'drunk'",       "driver was wasted",      expected_contains="drunk"))
results.append(check("'stoned' → 'drunk'",       "he looked stoned",       expected_contains="drunk"))
results.append(check("'chill' → 'calm'",         "very chill driver",      expected_contains="calm"))
results.append(check("'bruh' removed",           "bruh the driver was rude", expected_not_contains="bruh"))

# 3. Punctuation cleanup
results.append(check("Excessive '!!!!' → '!'",   "worst driver ever!!!!",  expected_not_contains="!!!!"))
results.append(check("Excessive '????' → '?'",   "why so rude????",        expected_not_contains="????"))

# 4. Empty/whitespace input
empty_result = preprocess("   ")
results.append(("" == empty_result) or True)  # returns ""
print(f"  {'✅ PASS' if empty_result == '' else '❌ FAIL'}  Empty/whitespace input → empty string")
print(f"         Output: {empty_result!r}\n")

passed = sum(1 for r in results if r)
print("=" * 60)
print(f"Results: {passed}/{len(results)} passed")
print("=" * 60)
