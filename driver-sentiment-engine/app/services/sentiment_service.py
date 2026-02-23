from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentService:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> dict:
        """
        Analyze text sentiment.
        Returns:
            {
                "score": float,
                "label": str
            }
        """
        result = self.analyzer.polarity_scores(text)
        score = result["compound"]

        if score >= 0.25:
            label = "positive"
        elif score <= -0.25:
            label = "negative"
        else:
            label = "neutral"

        return {
            "score": score,
            "label": label
        }