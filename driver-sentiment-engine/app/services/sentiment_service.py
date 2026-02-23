from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from abc import ABC, abstractmethod


# ─────────────────────────────────────────────
# Interface (OOP contract for plug-in models)
# ─────────────────────────────────────────────
class ISentimentProvider(ABC):

    @abstractmethod
    def analyze(self, text: str) -> dict:
        pass


# ─────────────────────────────────────────────
# Domain-specific lexicon additions for VADER
# These words are common in ride-sharing feedback
# but are weak or absent in VADER's default dict.
# Values are in VADER's sentiment scale: -4 to +4
# ─────────────────────────────────────────────
DRIVER_LEXICON = {
    # Positive driver traits
    "polite": 2.5,
    "courteous": 2.5,
    "careful": 1.8,
    "professional": 2.2,
    "punctual": 2.0,
    "helpful": 2.0,
    "friendly": 2.5,
    "safe": 1.5,
    "smooth": 1.5,
    "clean": 1.5,
    "comfortable": 1.8,
    "calm": 1.5,
    "cooperative": 1.8,
    "attentive": 1.8,
    "kind": 2.2,
    "skilled": 2.0,
    "expert": 2.0,
    "reliable": 2.0,

    # Negative driver traits
    "rude": -2.8,
    "drunk": -3.5,
    "abusive": -3.5,
    "aggressive": -2.5,
    "irresponsible": -3.0,
    "unsafe": -3.0,
    "careless": -2.5,
    "unprofessional": -2.5,
    "late": -1.5,
    "speeding": -2.0,
    "dirty": -1.8,
    "misbehaved": -2.8,
    "dishonest": -2.5,
    "overcharged": -2.2,
    "yelling": -2.5,
    "smoking": -2.0,
    "distracted": -2.2,
    "frisky": -1.5,       # In driver context = inappropriate
    "inappropriate": -2.5,
}

# VADER compound thresholds (official recommendation: ±0.05)
# Widened slightly to reduce false positives: ±0.08
POS_THRESHOLD = 0.08
NEG_THRESHOLD = -0.08


# ─────────────────────────────────────────────
# VADER-based Sentiment Service
# ─────────────────────────────────────────────
class SentimentService(ISentimentProvider):

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        # Inject domain-specific words into VADER's lexicon
        self.analyzer.lexicon.update(DRIVER_LEXICON)

    def analyze(self, text: str) -> dict:
        """
        Analyze text sentiment using VADER + domain lexicon.

        Returns:
            {
                "score": float,   # VADER compound score: -1.0 to +1.0
                "label": str      # "positive" | "neutral" | "negative"
            }
        """
        result = self.analyzer.polarity_scores(text)
        score = result["compound"]

        if score >= POS_THRESHOLD:
            label = "positive"
        elif score <= NEG_THRESHOLD:
            label = "negative"
        else:
            label = "neutral"

        return {
            "score": score,
            "label": label
        }