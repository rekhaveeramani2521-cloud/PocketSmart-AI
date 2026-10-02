# PocketSmart AI

PocketSmart AI is a FastAPI + Jinja2 web application for budget-aware recommendations across three planners:

- Home Interior Planner
- Party Budget Planner
- Jewelry Budget Planner with optional outfit image input

It includes registration/login/logout, signed cookie sessions, JWT token issuance, recommendation history, SQLite persistence, responsive UI, Gemini integration, and a no-key fallback engine.

## Project structure

```text
PocketSmart-AI/
├── main.py
├── requirements.txt
├── .env.example
├── app/
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── gemini_service.py
│   ├── models.py
│   ├── platforms.py
│   ├── recommendation_service.py
│   ├── routes.py
│   └── schemas.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── home_planner.html
│   ├── party_planner.html
│   ├── jewelry_planner.html
│   ├── recommendations.html
│   ├── recommendation_details.html
│   ├── history.html
│   └── testimonials.html
├── static/
│   ├── css/styles.css
│   └── js/app.js
└── tests/test_app.py
```

## VS Code setup (Windows)

1. Install Python 3.11 or newer and VS Code.
2. Open VS Code, then **File > Open Folder** and select `PocketSmart-AI`.
3. Open **Terminal > New Terminal**.
4. Create a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

5. Install packages:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Create your local environment file:

```powershell
Copy-Item .env.example .env
```

7. Open `.env` and replace `SECRET_KEY` with a long random value. To use Gemini, also set `GEMINI_API_KEY`. The application still works without Gemini by using fallback recommendations.

8. Start the app:

```powershell
uvicorn main:app --reload
```

9. Open `http://127.0.0.1:8000` in your browser.

## Gemini configuration

The code uses Google's current `google-genai` Python SDK through `client.models.generate_content`. The model name is configurable with `GEMINI_MODEL`, so you can change it if your Gemini account exposes a different model.

Example `.env`:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.8-flash
AI_ENABLED=true
```

Do not commit `.env` to GitHub.

## Run tests

```powershell
pytest -q
```

The tests disable Gemini and use the fallback engine, so they do not need an API key.

## Main routes

- `/` - landing page
- `/register`, `/login`, `/logout` - authentication
- `/dashboard` - user dashboard
- `/planner/home`, `/planner/party`, `/planner/jewelry` - planner forms
- `/generate-home`, `/generate-party`, `/generate-jewelry` - planner POST routes
- `/history` - saved recommendation history
- `/recommendations-details/{id}` - saved result details
- `/token` - JWT token endpoint
- `/session-info`, `/session-data` - session metadata
- `/health`, `/startup` - application status
- `/docs` - FastAPI Swagger UI

## Notes about external platforms

The project documentation allows mock/simulated third-party API calls. This implementation does not scrape Amazon, Flipkart, IKEA, Swiggy, Zomato, or OYO and does not pretend to have live price/stock data. Instead, it creates budget estimates and platform search links. For production, integrate official partner/affiliate APIs where available and update the recommendation service to consume verified live data.

## GitHub first commit

```powershell
git init
git add .
git commit -m "Initial PocketSmart AI project"
```
