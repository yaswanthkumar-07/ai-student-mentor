# AI Student Mentor — Lean Edition

**Your Career Journey, Simplified.**

A fast, lightweight, and offline-ready mentorship platform designed for students. The Lean Edition compares student skills against target engineering careers, pinpoints exact proficiency gaps, and constructs personalized stage-by-stage learning curricula with interactive progress tracking.

Runs entirely on local demo datasets with **zero required external API dependencies** or paid cloud services.

---

## 1. Core Modules (Lean Edition)

The Lean Edition focuses on four tightly integrated core modules:

1. **Student Dashboard:** Persona selection and comprehensive academic profile review, displaying degree details, verified skills proficiency matrix (Beginner, Intermediate, Advanced), and career interests.
2. **Career Explorer:** Search and filter across 14 industry career paths (AI, Cloud, Frontend, Backend, Data, Mobile, Security, etc.) with prerequisites, core competencies, and target career setting.
3. **Skill Gap Analysis:** Deterministic diagnostic comparing the student's current skills against target career prerequisites. Categorizes skills into *Already Acquired*, *Needs Improvement*, *Missing Skills*, and *Recommended Additional Skills* with coverage readiness percentages and action items.
4. **Personalized Learning Roadmap:** Stage-by-stage learning curriculum dynamically tailored to closing student skill gaps. Features interactive task tracking (`Not Started`, `In Progress`, `Completed`), progress persistence in localStorage, and curated verified learning resources.

---

## 2. Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla ES6 JavaScript | Zero build step, lightweight, accessible SaaS design system |
| **Backend** | Python 3.10+, Flask 3+, Flask-CORS | Modular blueprint architecture, lightweight RESTful API |
| **Data** | Bundled JSON Datasets (`data/`) | Deterministic mock profiles, careers, skills, roadmaps, resources |
| **Testing** | pytest, node -c | 56+ comprehensive unit and integration tests |
| **Deployment** | Cloudflare Pages (Frontend) & Render (Backend) | Static edge hosting + containerized Python web service |

> **Design Constraint:** No React, Vue, Angular, Node.js backend, Express, MongoDB, or paid APIs. Fully functional on low-spec hardware.

---

## 3. Folder Structure

```
ai-student-mentor/
├── frontend/                     # Static client application
│   ├── index.html                # Platform overview & landing page
│   ├── login.html                # Demo persona selector
│   ├── dashboard.html            # Student profile & skills matrix
│   ├── css/
│   │   └── main.css              # Unified SaaS CSS design system
│   ├── js/
│   │   ├── config.js             # API base URL configuration (Render / Localhost)
│   │   ├── utils.js              # HTML escaping & string format utilities
│   │   ├── api.js                # Fetch wrapper with error handling
│   │   ├── status.js             # Live backend status indicator & user pill
│   │   ├── login.js              # Persona selection logic
│   │   ├── dashboard.js          # Student profile view controller
│   │   ├── career-explorer.js    # Career search, filter, and modal controller
│   │   ├── skill-gap.js          # Skill gap analysis & readiness calculations
│   │   └── learning-roadmap.js   # Dynamic roadmap & task progress tracker
│   ├── pages/
│   │   ├── career-explorer.html  # Career Explorer view
│   │   ├── skill-gap.html        # Skill Gap Analysis view
│   │   └── learning-roadmap.html # Personalized Roadmap view
│   └── assets/                   # SVG icons and visual assets
├── backend/                      # Python Flask API backend
│   ├── app.py                    # Flask application factory
│   ├── config.py                 # Dev, testing, and production configuration
│   ├── routes/
│   │   ├── system.py             # Health check & system info endpoints
│   │   ├── students.py           # Student profile API routes
│   │   ├── careers.py            # Career catalog API routes
│   │   ├── skill_gap.py          # Skill gap diagnostic API routes
│   │   └── roadmap.py            # Personalized roadmap API routes
│   ├── services/
│   │   ├── students/             # Student lookup and filtering logic
│   │   ├── career/               # Career catalog search and detail enrichment
│   │   ├── skills/               # Skill gap calculation and classification logic
│   │   └── roadmap/              # Roadmap builder and dynamic fallback stages
│   ├── integrations/             # Local fallback clients (ESCO, GitHub, YouTube, etc.)
│   └── utils/                    # Data loader, validation, HTTP helpers, error handling
├── data/                         # Local JSON mock databases
│   ├── students.json             # 5 student personas
│   ├── careers.json              # 14 industry career paths
│   ├── skills.json               # 44 technical competencies
│   ├── roadmap.json              # Curated career learning stages
│   └── learning_resources.json   # 29 HTTPS learning materials
├── tests/                        # 56 automated pytest test suites
│   ├── test_health.py            # System & CORS tests
│   ├── test_config.py            # Environment configuration tests
│   ├── test_datasets.py          # Dataset schema and relation integrity tests
│   ├── test_students.py          # Student API and service tests
│   ├── test_careers.py           # Career API and service tests
│   ├── test_skill_gap.py         # Skill gap classification & coverage tests
│   ├── test_roadmap.py           # Roadmap curriculum generation tests
│   └── test_integrations.py      # Resilient fallback client tests
├── render.yaml                   # Infrastructure-as-code for Render deployment
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Python production & development dependencies
└── README.md                     # Project documentation
```

---

## 4. API Documentation

| Endpoint | Method | Parameters | Description |
|---|---|---|---|
| `/api/health` | `GET` | None | Returns backend service operational status |
| `/api/info` | `GET` | None | Returns version, environment, and module status |
| `/api/students` | `GET` | None | Returns list of all demo student personas |
| `/api/students/<student_id>` | `GET` | `student_id` | Returns complete profile with education and skills |
| `/api/careers` | `GET` | `category`, `search` | Lists all career paths with optional filtering |
| `/api/careers/<career_id>` | `GET` | `career_id` | Returns enriched career details and prerequisites |
| `/api/careers/categories` | `GET` | None | Returns list of unique career categories |
| `/api/skill-gap/<student_id>` | `GET` | `student_id` | Analyzes gaps using student's default target career |
| `/api/skill-gap/<student_id>/<career_id>` | `GET` | `student_id`, `career_id` | Analyzes gaps against a specific target career |
| `/api/roadmap/<student_id>` | `GET` | `student_id` | Generates roadmap using default target career |
| `/api/roadmap/<student_id>/<career_id>` | `GET` | `student_id`, `career_id` | Generates personalized stage curriculum |

---

## 5. Local Setup Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.11 and 3.12)
- Any modern web browser (Chrome, Edge, Firefox)

### Backend Setup (PowerShell / Bash)
```powershell
# 1. Navigate to project root
cd ai-student-mentor

# 2. (Optional) Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Flask API server
python -m backend.app
# Backend runs at http://127.0.0.1:5000
```

### Frontend Setup
In a second terminal:
```powershell
# Navigate to the frontend directory and serve static files
cd frontend
python -m http.server 5500
```
Open `http://127.0.0.1:5500` in your web browser.

---

## 6. Testing & Quality Assurance

Run the complete test suite:
```powershell
pytest -v
```
All 56 tests execute in under 1 second.

Validate frontend JavaScript syntax:
```powershell
Get-ChildItem -Path frontend\js\*.js | ForEach-Object { node -c $_.FullName }
```

Validate JSON dataset consistency:
```powershell
python -m backend.utils.data_loader
```

---

## 7. Client-Side Persistence Architecture

The frontend uses standard `localStorage` with explicit namespacing:
- `ai-student-mentor.studentId`: Currently selected student persona ID (`student_001` - `student_005`).
- `ai-student-mentor.targetCareerId`: Selected target career ID (`data_scientist`, `cloud_architect`, etc.).
- `ai-student-mentor.roadmapProgress`: Nested dictionary storing user task status keyed by student and career:
  ```json
  {
    "student_001": {
      "data_scientist": {
        "stage_1_task_1": "completed",
        "stage_1_task_2": "in_progress"
      }
    }
  }
  ```
  Switching personas or careers maintains isolated progress states without accidental data loss.

---

## 8. Deployment Preparation

### Frontend: Cloudflare Pages
1. Push repository to GitHub or upload `frontend/` folder.
2. In Cloudflare Pages, set the **Build output directory** to `frontend`.
3. Set **Build command** to empty (none required).
4. Update `frontend/js/config.js` to point `API_BASE_URL` to your production Render URL.

### Backend: Render
1. The included `render.yaml` automatically sets up the web service:
   - **Environment:** `python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn "backend.app:create_app()"`
2. Set environment variables in Render:
   - `FLASK_ENV=production`
   - `CORS_ORIGINS=https://<your-project>.pages.dev`
   - `SECRET_KEY=<generate-strong-key>`
