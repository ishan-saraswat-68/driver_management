# driver-sentiment-engine

The backend for SentimentIQ. It's a Python API that takes in passenger feedback, figures out the driver's sentiment score using NLP, keeps a rolling performance average, and fires a Slack alert when someone's score drops too low.

---

## What lives here

```
app/
├── main.py                 ← API routes (FastAPI)
├── models.py               ← Request body shape (Pydantic)
├── config.py               ← Supabase connection, env vars
├── processing_tasks.py     ← Background pipeline: analyze → store → update score → alert
├── logger.py               ← Logging setup
├── services/
│   ├── sentiment_service.py  ← NLP: VADER + custom driver word list
│   ├── driver_service.py     ← EMA score tracking per driver
│   └── alert_service.py      ← Thread-safe cooldown-protected Slack alerts
├── repositories/
│   └── driver_repository.py  ← All Supabase DB operations
└── utils/
    └── text_preprocessor.py  ← Cleans raw text before analysis
```

---

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Fill in SUPABASE_URL, SUPABASE_KEY, SLACK_WEBHOOK_URL
```

`.env` variables:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...   # optional
ALERT_THRESHOLD=2.5      # default, scores below this trigger an alert
COOLDOWN_HOURS=24        # how long before the same driver can be alerted again
```

Then start it:

```bash
uvicorn app.main:app --reload
```

Runs at `http://127.0.0.1:8000`. Hot reload is on so code changes apply instantly.

---

## API

### `POST /feedback`

Takes feedback for a driver and responds right away with `202 Accepted`. The actual analysis happens in a background thread — caller doesn't wait for it.

```json
{
  "driver_id": "drv_9921",
  "trip_id": "trip_8820",
  "text": "Driver was rude and driving way too fast.",
  "entity_type": "driver",
  "external_feedback_id": "abc-unique-id"
}
```

Pass `external_feedback_id` if you want idempotency — submitting the same ID twice is a no-op. No double score updates, no double alerts.

---

### `GET /drivers`

All drivers sorted by score (lowest first). Used by the admin dashboard.

---

### `GET /driver/{driver_id}`

One driver's current score, total feedback count, and last alert timestamp.

---

### `GET /health`

Returns `{ "status": "ok" }`. Use this to check if the service is up.

---

## How the processing pipeline works

When feedback comes in, a background job runs four things in order:

1. **Preprocess** — strips emojis (translates them to words actually), slang, weird unicode
2. **Analyze** — VADER computes a compound score (-1 to +1), which we convert to 0–5 using `(raw + 1) / 2 × 5`
3. **Store** — saves the raw feedback text and computed score to Supabase
4. **Update + Alert** — updates the driver's EMA score, then checks if it's below threshold

Each DB step retries up to 3 times with short delays in case of transient Supabase errors.

---

## The NLP part

VADER is good at short informal text but doesn't understand ride-specific vocabulary out of the box. Words like `"speeding"` or `"harassment"` have weak or neutral weights by default. We fixed that by injecting a custom lexicon at startup:

```python
DRIVER_LEXICON = {
    "speeding": -2.0,  "rude": -2.8,  "harassment": -3.5,
    "punctual": +2.0,  "polite": +2.5, "professional": +2.2,
    ...
}
analyzer.lexicon.update(DRIVER_LEXICON)
```

This happens once when the service starts. No overhead at request time.

---

## EMA scoring

Drivers don't get a simple average — they get an Exponential Moving Average with α = 0.2:

```
new_score = 0.2 × incoming + 0.8 × existing
```

This means recent behavior matters more than old history. A driver with a strong past will still see their score drop if the last few weeks have been bad.

First-time drivers get their first score as-is (nothing to blend with yet).

---

## Alert behavior

An alert fires to Slack when a driver's EMA drops below `ALERT_THRESHOLD` (default 2.5/5).

Two things prevent spam:

- **Per-driver thread lock** — if multiple threads process the same driver simultaneously, only one can run the check-and-send block at a time. The others see the freshly written timestamp when they finally get through.
- **DB-persisted cooldown** — `last_alert_at` is saved in Supabase, not in memory. Restarts don't reset it.

If `SLACK_WEBHOOK_URL` isn't set, the alert still runs but just logs a warning instead of crashing.

---

## Tests

```bash
python -m pytest -v

# Or one at a time:
python -m pytest test_sentiment.py -v
python -m pytest test_ema.py -v
python -m pytest test_alert_service.py -v
python -m pytest test_preprocessor.py -v
```

Tests check: NLP label accuracy, EMA math, alert cooldown blocking repeat fires, preprocessor edge cases (empty string, pure emoji, unicode-only input).
