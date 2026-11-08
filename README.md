# AI Student Mentor

**Your Career Journey, Simplified.**

A demonstration platform that helps students discover suitable careers, identify skill gaps, follow learning roadmaps, find practical projects, explore jobs, build and analyze resumes, and get career guidance.

> This repository currently contains the **project foundation** (Batch 1): backend skeleton, demo datasets, integration clients and tests. Module features arrive in later batches.

## 1. Problem statement

Students often don't know which careers fit them, which skills they lack, or what to learn next. Guidance is scattered across many websites. AI Student Mentor brings it into one place, using sample data so it runs anywhere with no paid services.

## 2. Application modules

1. Career Recommendation
2. Skill Gap Analysis
3. Learning Roadmap
4. Project Suggestions
5. Job Recommendations
6. Resume Builder
7. Resume Analyzer
8. Career Assistant

## 3. Technology stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, vanilla JavaScript |
| Backend | Python 3, Flask, Flask-CORS |
| Data | Pandas, NumPy, JSON/CSV demo datasets |
| Machine learning | scikit-learn (spaCy optional) |
| PDF | PyMuPDF (read), ReportLab (write) |
| Tooling | VS Code, Git/GitHub, Jupyter, pytest |
| Deployment | Cloudflare Pages (frontend), Render (backend) |

## 4. Folder structure

```
ai-student-mentor/
├── frontend/              static site (index, login, dashboard, css/, js/, assets/, pages/)
├── backend/
│   ├── app.py             Flask application factory
│   ├── config.py          dev / production / testing configuration
│   ├── routes/            one blueprint per module (system.py for health/info)
│   ├── services/          business logic: career, skills, roadmap, projects, jobs, resume, assistant
│   ├── integrations/      esco, github, youtube, jobs_api, gemini (all optional)
│   └── utils/             data loading/validation, HTTP helper, errors, responses, logging
├── machine_learning/      datasets, notebooks, preprocessing, training, saved_models
├── data/                  demo JSON datasets
├── tests/                 pytest suite
├── render.yaml            Render deployment blueprint
├── pytest.ini  requirements.txt  .env.example  .gitignore
```

## 5. Installation (Windows PowerShell)

Requires Python 3.10+ (developed on 3.12).

```powershell
cd ai-student-mentor

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# If activation is blocked:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create your local environment file
Copy-Item .env.example .env
```

`gunicorn` is for Linux/Render only. If it fails to install on Windows, remove that line locally; `flask run` is used for development.

## 6. Environment configuration

Edit `.env`. All keys are optional; the app works with local fallback data without them. Placeholder values copied from `.env.example` are ignored.

| Variable | Purpose |
|---|---|
| `FLASK_ENV` | `development` (default) or `production` |
| `SECRET_KEY` | Required in production |
| `GEMINI_API_KEY` | Optional AI assistant |
| `YOUTUBE_API_KEY` | Optional video search |
| `GITHUB_TOKEN` | Optional, raises GitHub rate limits |
| `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` | Optional live job search |
| `ESCO_BASE_URL` | ESCO API base URL (default provided) |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins (production default: `https://ai-student-mentor.pages.dev`) |
| `EXTERNAL_APIS_ENABLED` | Set `false` to force offline/fallback mode |
| `HTTP_TIMEOUT_SECONDS` | Outbound request timeout (default 8) |

Keys are read only by the backend and never sent to the browser. `.env` is git-ignored.

## 7. Run the backend

```powershell
flask --app backend.app run --debug
# or
python -m backend.app
```

The API listens on `http://127.0.0.1:5000`.

## 8. Test the health check

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
Invoke-RestMethod http://127.0.0.1:5000/api/info
```

Expected `/api/health` response:

```json
{"status": "success", "application": "AI Student Mentor", "message": "Backend is running"}
```

Run the tests and the dataset validator:

```powershell
pytest
python -m backend.utils.data_loader
```

## 9. Run the frontend

In a second terminal:

```powershell
cd frontend
python -m http.server 5500
```

Open `http://localhost:5500`. The home and dashboard pages show whether the backend is reachable.

## 10. Demo data

All data lives in `data/` and is fictional.

| File | Contents |
|---|---|
| `students.json` | 5 sample student profiles |
| `careers.json` | 14 career paths with required skills and prerequisites |
| `skills.json` | 44 skills with categories and a 3-level proficiency scale |
| `projects.json` | 21 projects with difficulty, technologies and time estimates |
| `jobs.json` | 16 **sample** listings, clearly labelled and **not live vacancies**; URLs are placeholders |
| `roadmap.json` | 9 staged learning roadmaps |
| `learning_resources.json` | 29 public learning resources (verify links before relying on them) |

Records reference each other by id (for example, a career's `required_skills` are ids from `skills.json`). `python -m backend.utils.data_loader` checks structure, unique ids and every cross-reference.

## 11. Optional external APIs

Each client in `backend/integrations/` returns the same result shape (`ok`, `data`, `error`, `source`) where `source` is `live`, `fallback` or `unavailable`.

| Integration | Needs key? | Without it |
|---|---|---|
| ESCO | No | Searches local careers and skills |
| GitHub | No (token optional) | Suggests matching local projects; handles rate limits |
| YouTube | Yes | Returns curated learning resources |
| Jobs (Adzuna, pluggable) | Yes | Returns labelled sample jobs |
| Gemini | Yes | Clear "not configured" response |

To enable one, add its key to `.env` and restart. Set `EXTERNAL_APIS_ENABLED=false` to stay fully offline. New job providers can be added with `JobsAPIClient.register_provider`.

## 12. Deployment architecture

```
Browser ──► Cloudflare Pages (frontend/)  ──fetch──►  Render web service (Flask API)
                                                          │
                                                          ├── data/*.json (bundled)
                                                          └── optional external APIs
```

- **Backend (Render):** `render.yaml` defines the service. Build: `pip install -r requirements.txt`. Start: `gunicorn "backend.app:create_app()"`. Set `SECRET_KEY` (auto-generated), `CORS_ORIGINS` and any optional keys in the Render dashboard.
- **Frontend (Cloudflare Pages):** no build command; set the output directory to `frontend`. Update the production `API_BASE_URL` in `frontend/js/config.js` to your Render URL.
- Free Render instances sleep when idle, so the first request can be slow.
