# AI Intel Bot (Email + Sheets + TTS)
Twice-daily AI intel: fetch → summarize (Gemini if key) → log to Google Sheets → email (with optional MP3).

## Setup (GitHub)
1) Create repo, upload everything from this zip (keep folder structure).
2) Add **Actions → Secrets**:
   - `GCP_SERVICE_ACCOUNT_JSON`  (full JSON; enable Sheets + Drive APIs; share the Sheet with this service account as **Editor**)
   - `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `GMAIL_TO`
   - (Optional) `GEMINI_API_KEY`
3) Edit `config/feeds.yaml` (your 5–15 sources).
4) Actions → **AI Intel Bot (Email+TTS)** → **Run workflow**.

The Sheet ID and tab can be hardcoded or provided via env; this build uses code defaults (see `src/sheets.py`).