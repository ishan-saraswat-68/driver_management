"""
text_preprocessor.py
─────────────────────
Handles: emojis → sentiment hints, slang normalization,
         whitespace cleanup, and basic typo resilience.
"""

import re
import unicodedata

# ─── Emoji → semantic replacement ───────────────────────────────────────────
# Map Unicode emoji chars to descriptive words VADER understands.
EMOJI_MAP = {
    "😊": "happy",
    "😀": "great",
    "😁": "excellent",
    "🙂": "good",
    "😍": "amazing",
    "🥰": "loving",
    "👍": "good",
    "💯": "perfect",
    "🌟": "excellent",
    "⭐": "great",
    "✨": "wonderful",
    "🎉": "fantastic",
    "👏": "well done",
    "🚗": "",        # neutral — just a car
    "😐": "okay",
    "😑": "boring",
    "🤷": "whatever",
    "😤": "frustrated",
    "😠": "angry",
    "😡": "very angry",
    "🤬": "extremely angry",
    "😒": "unhappy",
    "👎": "bad",
    "😩": "terrible",
    "😞": "disappointed",
    "💔": "very bad",
    "🤮": "disgusting",
    "🚨": "emergency",
    "⚠️": "warning",
    "🔥": "amazing",   # ride-hailing context: "🔥 driver" = great
    "❤️": "love",
    "💕": "wonderful",
}

# ─── Common ride-hailing slang → expanded forms ──────────────────────────────
SLANG_MAP = {
    r"\bgr8\b": "great",
    r"\bgo0d\b": "good",
    r"\blate af\b": "very late",
    r"\bwtf\b": "what the hell",
    r"\bomg\b": "oh my god",
    r"\bngl\b": "not gonna lie",
    r"\bfrfr\b": "for real",
    r"\blit\b": "great",
    r"\bslay\b": "excellent",
    r"\bloaded\b": "drunk",
    r"\bstoned\b": "drunk",
    r"\bsmashed\b": "drunk",
    r"\bwasted\b": "drunk",
    r"\bdrunk af\b": "extremely drunk",
    r"\bchill\b": "calm",
    r"\bbro\b": "",       # filler, remove
    r"\bbruh\b": "",
    r"\bfam\b": "",
    r"\bngl\b": "not gonna lie",
    r"\btbh\b": "to be honest",
    r"\bimho\b": "in my opinion",
    r"\bish\b": "somewhat",
    r"\bkinda\b": "somewhat",
    r"\bsrry\b": "sorry",
    r"\bthx\b": "thanks",
    r"\bthnk\b": "thanks",
    r"\bokay\b": "okay",
    r"\bok\b": "okay",
    r"\bnah\b": "no",
    r"\byeah\b": "yes",
    r"\byep\b": "yes",
    r"\bnope\b": "no",
}


def preprocess(text: str) -> str:
    """
    Clean and normalize raw feedback text.
    Steps:
      1. Replace emoji with sentiment-aware words
      2. Normalize unicode (handle accent chars, composed forms)
      3. Expand slang
      4. Clean excessive punctuation / whitespace
      5. Lowercase (VADER is case-aware but normalizing helps consistency)
    """
    if not text or not text.strip():
        return ""

    # 1. Replace emojis
    for emoji_char, replacement in EMOJI_MAP.items():
        text = text.replace(emoji_char, f" {replacement} ")

    # 2. Unicode normalize — NFKC collapses ligatures, fullwidth chars etc.
    text = unicodedata.normalize("NFKC", text)

    # 3. Expand slang (case-insensitive)
    for pattern, replacement in SLANG_MAP.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # 4. Strip excessive punctuation repeats: "!!!!" → "!"
    text = re.sub(r"([!?.]){2,}", r"\1", text)

    # 5. Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
