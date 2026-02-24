# frontend

The React app for SentimentIQ. Two types of users can log in: employees who submit driver feedback, and admins who see the full insights dashboard.

---

## What lives here

```
src/
├── pages/
│   ├── Login.jsx           ← Sign in page
│   ├── Signup.jsx          ← Registration (email + full name, employee by default)
│   ├── Dashboard.jsx       ← Admin only: fleet scores, chart, searchable driver table
│   └── Feedback.jsx        ← Employee: submit feedback for a driver/trip
├── components/
│   ├── Sidebar.jsx         ← Navigation, user info, sign out button
│   └── ProtectedRoute.jsx  ← Blocks routes if not authenticated or wrong role
├── context/
│   └── AuthContext.jsx     ← Holds session state, user email, and role
└── lib/
    └── supabase.js         ← Supabase client (reads from .env)
```

---

## Setup

```bash
npm install
```

Create a `.env` file in this folder:

```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

Then run it:

```bash
npm run dev
# Starts at http://localhost:5173
```

---

## How auth and roles work

Sign up is open — anyone can create an account. All new accounts get the `employee` role automatically.

The role comes from a `profiles` table in Supabase, not from the JWT itself. After login, `AuthContext` fetches the role and stores it in React state. Then `ProtectedRoute` uses that to decide what the user can see.

Admins are promoted manually in the database (update the `role` column in `profiles` for that user's ID to `"admin"`).

If the `profiles` table doesn't exist yet (maybe migrations haven't run), the app doesn't crash — it just defaults everyone to `employee`.

---

## Pages

### Login
Standard email + password form. After login, navigates to `/` which is the feedback page (or dashboard, depending on role).

### Signup
Collects full name, email, and password. Runs some client-side validation before calling Supabase. Password fields can be toggled visible. On success, shows a confirmation screen asking the user to check their email.

### Feedback (`/`)
The only page employees see. They fill in a driver ID, trip ID, and their feedback text. That gets posted to `http://127.0.0.1:8000/feedback` — the Python backend handles everything from there.

### Dashboard (`/dashboard`)
Admin only. Shows:
- Four stat cards: total drivers, average fleet EMA score, at-risk driver count, total feedback processed
- Bar chart of the 15 lowest-scoring drivers (colored red/yellow/green based on score)
- A full searchable table of every driver with their score bar, classification badge, and last signal timestamp

---

## Design system

Everything visual lives in `src/index.css`. It's a standalone CSS file — no Tailwind, no CSS modules. Colors are all CSS variables:

```css
--accent:        #f97316;   /* warm amber */
--bg:            #0c0a09;   /* near-black, warm undertone */
--text-primary:  #fafaf9;
--text-muted:    #78716c;
```

Fonts: **Bricolage Grotesque** for headings, **DM Sans** for body text — both loaded from Google Fonts.

---

## Backend dependency

The dashboard and feedback form both talk to the Python backend running on port 8000. Make sure the backend is running before using either of those pages. The backend README has setup instructions.
