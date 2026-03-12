# JobRadar — AI Job Matcher

Searches LinkedIn, Indeed, and Glassdoor for jobs and scores each one against your profile using Claude AI.

## Setup & Run

### 1. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the backend server
```bash
python app.py
```
Server runs on http://localhost:5000

### 3. Open the frontend
Open `frontend/index.html` directly in your browser.
That's it — no build step needed.

## How it works

1. You enter a search query (e.g. "full stack developer python") and location
2. The backend uses `jobspy` to scrape LinkedIn, Indeed, and Glassdoor
3. Each job is sent to Claude AI which scores it 0-100 against your profile and writes a short analysis
4. Results are sorted by match score, highest first

## Customizing your profile

Edit the `PROFILE` constant in both:
- `backend/app.py` — used for searches
- `frontend/index.html` (the `PROFILE` const in the `<script>` tag) — used for AI scoring

## Changing search defaults

In `frontend/index.html`, edit the default values in the input fields.
In `backend/app.py`, adjust `hours_old` (how recent jobs are) and `results_wanted`.

## Troubleshooting

- **"Backend offline"** — make sure `python app.py` is running in a terminal
- **No results** — try a broader search term or increase `hours_old` in app.py
- **LinkedIn blocks** — this is common; jobspy rotates but LinkedIn aggressively rate-limits scrapers. Indeed and Glassdoor tend to be more reliable.
# JobhuntBackend
