"""
sentiment_service.py
─────────────────────
VADER-based sentiment engine with:
  - Domain-specific driver lexicon
  - Text preprocessing (emojis, slang, unicode)
  - Score normalization: VADER -1..+1  →  0..5 (per requirements)
  - OOP interface for future ML model plug-in
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from abc import ABC, abstractmethod
from app.utils.text_preprocessor import preprocess


# ─── Interface (OOP contract — swap in any ML model later) ──────────────────
class ISentimentProvider(ABC):

    @abstractmethod
    def analyze(self, text: str) -> dict:
        """
        Returns:
            {
              "score":      float  # normalized 0–5
              "raw_score":  float  # VADER compound -1..+1
              "label":      str    # positive | neutral | negative
            }
        """
        pass


# ─── Domain-specific lexicon entries for VADER ───────────────────────────────
# Scale: -4 (very negative) to +4 (very positive)
DRIVER_LEXICON = {
    # Positive driver traits
    "polite": 2.5, "courteous": 2.5, "careful": 1.8, "professional": 2.2,
    "punctual": 2.0, "helpful": 2.0, "friendly": 2.5, "safe": 1.5,
    "smooth": 1.5, "clean": 1.5, "comfortable": 1.8, "calm": 1.5,
    "cooperative": 1.8, "attentive": 1.8, "kind": 2.2, "skilled": 2.0,
    "expert": 2.0, "reliable": 2.0, "on-time": 2.0, "wellbehaved": 2.5,

    # Negative driver traits
    "rude": -2.8, "drunk": -3.5, "abusive": -3.5, "aggressive": -2.5,
    "irresponsible": -3.0, "unsafe": -3.0, "careless": -2.5,
    "unprofessional": -2.5, "late": -1.5, "speeding": -2.0,
    "dirty": -1.8, "misbehaved": -2.8, "dishonest": -2.5,
    "overcharged": -2.2, "yelling": -2.5, "smoking": -2.0,
    "distracted": -2.2, "frisky": -1.5, "inappropriate": -2.5,
    "harassment": -3.5, "threatening": -3.5,
}

# VADER recommended threshold: ±0.05. Using ±0.08 to reduce noise.
POS_THRESHOLD = 0.08
NEG_THRESHOLD = -0.08


def _normalize_to_five(raw_score: float) -> float:
    """
    Convert VADER compound score (-1..+1) to a 0–5 scale.
    Formula: (raw + 1) / 2 * 5
    Examples:
      -1.0 → 0.0   (worst)
      -0.5 → 1.25
       0.0 → 2.5   (neutral midpoint)
      +0.5 → 3.75
      +1.0 → 5.0   (best)
    """
    return round((raw_score + 1) / 2 * 5, 4)


# ─── Concrete VADER-backed implementation ────────────────────────────────────
class SentimentService(ISentimentProvider):

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        # inject domain vocabulary into VADER's live lexicon
        self.analyzer.lexicon.update(DRIVER_LEXICON)

    def analyze(self, text: str) -> dict:
        # Step 1: preprocess (emojis → words, slang, unicode cleanup)
        clean_text = preprocess(text)

        # Fallback to original if preprocessing strips everything
        if not clean_text:
            clean_text = text

        # Step 2: VADER scoring
        result = self.analyzer.polarity_scores(clean_text)
        raw_score = result["compound"]   # -1.0 to +1.0

        # Step 3: Label using VADER-recommended thresholds
        if raw_score >= POS_THRESHOLD:
            label = "positive"
        elif raw_score <= NEG_THRESHOLD:
            label = "negative"
        else:
            label = "neutral"

        # Step 4: Normalize to 0-5 scale (as per requirements: "2.5 out of 5")
        score_5 = _normalize_to_five(raw_score)

        return {
            "score": score_5,          # 0–5, stored in DB and used for EMA
            "raw_score": raw_score,    # -1 to +1, for transparency
            "label": label
        }