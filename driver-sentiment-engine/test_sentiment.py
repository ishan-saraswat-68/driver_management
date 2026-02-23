from app.services.sentiment_service import SentimentService

service = SentimentService()

samples = [
    "Driver was 🔥",
    "Very rude and late",
    "pathetic service "
]

for text in samples:
    result = service.analyze(text)
    print(f"Text: {text}")
    print(f"Score: {result['score']}")
    print(f"Label: {result['label']}")
    print("-" * 40)