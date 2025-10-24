# AI-V2

Minimal FastAPI backend that uses OpenAI's browsing-enabled Responses API to discover Hazen Road-aligned institutional investors and senior contacts. Includes a lightweight HTML page for testing and observing logs.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set OPENAI_API_KEY
python manage.py dev
```

Open <http://localhost:8000> to access the test UI. Submit a prompt + target count; the page displays the collected leads and polls `/logs/{job_id}` for debugging info.

## Testing

```bash
python manage.py test
```

## Project Structure

```
backend/
  app.py            # FastAPI routes
  core/             # settings + logging
  services/
    ai_research.py  # OpenAI integration
    persistence.py  # SQLite storage + logs
  schemas/          # Pydantic models
  utils/            # prompts + validators
frontend/
  index.html        # testing UI
  scripts.js
```
