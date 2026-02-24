# SentimentIQ

A system that reads passenger feedback, figures out how the driver is doing, and tells a supervisor when things go south — all without any human manually reviewing anything.

---

## Why I built this

The problem with most feedback systems is that they just collect data and show a table. Someone still has to read through 200 reviews to decide if driver `drv_9921` has been having a rough couple of weeks. This project automates that whole chain — from raw text to supervisor notification.

---

## How it works, step by step

Let's say a passenger submits: *"The driver was speeding and very rude. Felt unsafe the whole ride."*

Here's what happens next:

**1. The text gets cleaned up**
Emojis are translated to words. Slang gets normalized. Weird unicode characters are stripped. The cleaner version goes into analysis.

**2. An NLP model reads the sentiment**
We use VADER — a rule-based sentiment analyzer that's fast and works well on short, informal text like ride reviews. But the default VADER doesn't understand driver-specific words particularly well. "Speeding" is kind of neutral to a generic model. So we injected a custom word list straight into VADER at startup:

```python
DRIVER_LEXICON = {
    "speeding":  -2.0,
    "rude":      -2.8,
    "punctual":  +2.0,
    "harassment": -3.5,
    ...
}
```

Now when VADER sees these words it actually knows what to do with them.

**3. The score gets converted to a 0–5 scale**
VADER gives us a number between -1.0 and +1.0. We convert it to 0–5 using this formula:

```
score = (raw + 1) / 2 × 5
```

So a raw score of 0.0 (neutral) becomes 2.5. Anything below 2.5 is concerning.

**4. The driver's running average gets updated**
We don't simply average all scores. We use an Exponential Moving Average (EMA) with α = 0.2:

```
new_score = 0.2 × today's_score  +  0.8 × previous_score
```

Recent feedback matters more than old feedback. A driver who had 100 great trips six months ago but has been getting 2-star reviews lately should have a low score — not a comfortable 4.5 because of their history.

**5. An alert fires if the score drops below 2.5**
If the driver's EMA is below the threshold, the system sends a Slack message to the supervisor. It doesn't spam — there's a 24-hour cooldown per driver, and it's stored in the database so even a server restart won't cause a double-alert.

---

## The alert system deserves its own explanation

The alert code is one of the trickier parts. Here's the issue: feedback processing runs in background threads. If five reviews come in at the same time for the same driver, five threads could all check the score simultaneously, all see it's below 2.5, and all try to send the alert.

I solved this with two layers:

**Layer one — per-driver threading lock**
Each driver gets their own lock. When a thread picks it up, it checks the score, sends the alert (if needed), and updates the `last_alert_at` timestamp — all while holding the lock. By the time the next thread grabs it, the timestamp is already there.

**Layer two — database timestamp**
The `last_alert_at` column lives in Supabase, not in memory. If the server crashes and restarts 10 minutes after an alert, the next check still sees the timestamp and skips. In-memory state wouldn't survive that.

---

## The frontend

Two roles:

- **Employee** — can only submit feedback. That's it.
- **Admin** — can submit feedback *and* see the full insights dashboard (fleet scores, bar chart of lowest performers, searchable driver table).

The role is stored in a `profiles` table in Supabase alongside the user's auth record. New signups always get `employee` by default. An admin promotes them manually from the database.

---

## Project layout

```
driver_management/
├── driver-sentiment-engine/        ← Python backend
│   ├── app/
│   │   ├── main.py                 ← API routes (FastAPI)
│   │   ├── models.py               ← Request shapes (Pydantic)
│   │   ├── processing_tasks.py     ← Background job: analyze → store → alert
│   │   ├── config.py               ← Supabase client, env loading
│   │   ├── logger.py               ← Structured logging
│   │   ├── services/
│   │   │   ├── sentiment_service.py  ← VADER + custom lexicon
│   │   │   ├── driver_service.py     ← EMA calculation
│   │   │   └── alert_service.py      ← Thread-safe Slack alerts
│   │   ├── repositories/
│   │   │   └── driver_repository.py  ← Supabase DB calls
│   │   └── utils/
│   │       └── text_preprocessor.py  ← Emoji → text, slang, unicode
│   └── tests:
│       test_sentiment.py, test_ema.py, test_alert_service.py, test_preprocessor.py
│
└── frontend/                       ← React + Vite
    └── src/
        ├── pages/
        │   ├── Login.jsx           ← Sign in
        │   ├── Signup.jsx          ← Register (email + full name)
        │   ├── Dashboard.jsx       ← Admin view: charts + driver table
        │   └── Feedback.jsx        ← Employee view: submit feedback
        ├── components/
        │   ├── Sidebar.jsx         ← Nav, user info, sign out
        │   └── ProtectedRoute.jsx  ← Redirects if not authenticated/authorized
        ├── context/
        │   └── AuthContext.jsx     ← Session state + role fetching
        └── lib/
            └── supabase.js         ← Supabase client instance
```

---

## Database tables

### `feedback` — every submitted review

| Column | What it holds |
|---|---|
| `driver_id` | Which driver this is about |
| `trip_id` | Which trip |
| `text` | What the passenger actually wrote |
| `sentiment` | Normalized score after NLP (0–5) |
| `sentiment_label` | positive, neutral, or negative |
| `entity_type` | Could be driver, trip, app, or marshal |
| `external_feedback_id` | Used to prevent duplicate processing |

### `driver_sentiment` — one row per driver, always current

| Column | What it holds |
|---|---|
| `driver_id` | The driver's identifier |
| `score` | Current EMA score (0–5) |
| `total_count` | How many reviews processed so far |
| `last_updated` | When the score last changed |
| `last_alert_at` | When the last Slack alert went out |

### `profiles` — ties auth users to roles

| Column | What it holds |
|---|---|
| `id` | Same UUID as the Supabase auth user |
| `role` | `"admin"` or `"employee"` |

---

## Running it locally

### Backend

```bash
cd driver-sentiment-engine

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Copy and fill in the .env file
cp .env.example .env

uvicorn app.main:app --reload
# Now live at http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Now live at http://localhost:5173
```

### Environment variables

**Backend `.env`:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...  # leave blank to skip alerts
ALERT_THRESHOLD=2.5
COOLDOWN_HOURS=24
```

**Frontend `.env`:**
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

---

## API endpoints

### `POST /feedback`
You submit feedback here. The endpoint responds right away with `202` — the actual NLP and DB work happens in the background so you're not waiting for it.

```json
{
  "driver_id": "drv_9921",
  "trip_id": "trip_8820",
  "text": "Driver was rude and speeding the entire time.",
  "entity_type": "driver",
  "external_feedback_id": "some-unique-id"
}
```

If you send the same `external_feedback_id` twice, the second one is silently ignored. No duplicate scores, no double alerts.

---

### `GET /drivers`
Returns every driver sorted by score, lowest first. This is what the admin dashboard reads.

```json
{
  "success": true,
  "data": [
    { "driver_id": "drv_3310", "score": 1.43, "total_count": 12 },
    { "driver_id": "drv_9921", "score": 3.71, "total_count": 47 }
  ]
}
```

---

### `GET /driver/{driver_id}`
Stats for one specific driver.

```json
{
  "success": true,
  "data": {
    "driver_id": "drv_9921",
    "score": 3.71,
    "total_feedback_count": 47,
    "last_updated": "2026-02-24T02:14:00Z",
    "last_alert_at": null
  }
}
```

---

### `GET /health`
```json
{ "status": "ok" }
```

---

## Running the tests

```bash
cd driver-sentiment-engine
source venv/bin/activate

python -m pytest -v
```

The tests cover: whether VADER correctly labels positive/negative text, whether the EMA formula gives the right numbers, whether the alert cooldown actually blocks repeated notifications, and whether the preprocessor handles edge cases like pure emoji input or empty strings.

---

## Tech used

| | |
|---|---|
| Backend | FastAPI, Python |
| NLP | vaderSentiment |
| Database | Supabase (Postgres) |
| Auth | Supabase Auth |
| Alerting | Slack Incoming Webhooks |
| Frontend | React 18, Vite |
| Charts | Recharts |
| Icons | Lucide React |

---

## A few decisions I want to explain

**Why VADER and not something like BERT?**
VADER runs in microseconds — no GPU, no model loading time, no memory overhead. For 1–3 sentence ride reviews, it's accurate enough in practice. The sentiment service is also behind an abstract interface (`ISentimentProvider`) so swapping in a transformer model later is a one-class change.

**Why EMA instead of a normal average?**
A regular average buries recent behavior under months of history. EMA with α = 0.2 means roughly the last 5 ratings carry more weight than everything before them. That's actually what you want — if a driver has been great for a year but terrible for the last two weeks, you want the score to reflect the recent pattern, not the full career.

**Why save `last_alert_at` to the database?**
If I stored the cooldown in memory, it would reset every time the server restarts. A driver could get alerted, the server restarts 20 minutes later, and they get alerted again. Saving to Supabase means the cooldown survives restarts.