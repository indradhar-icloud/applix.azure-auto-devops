# Azure DevOps Automation

A FastAPI application that automatically creates subtasks in Azure DevOps when you create a user story. Built with clean architecture and event-driven processing.

## What does this do?

Simple: You send a user story to the API, and it automatically creates 5 standard subtasks for you in Azure DevOps:
1. Requirements & Grooming
2. Design & Approach
3. Implementation
4. Testing & QA
5. Deployment & Documentation

The cool part? It all happens in the background. You get an immediate response, and the worker daemon handles the Azure DevOps API calls asynchronously.

---

## How it works

**API Server** → Receives your story, saves it to the database, creates an event  
**Worker Daemon** → Polls for pending events, calls Azure DevOps API, creates tasks  
**Database** → Keeps track of everything (SQLite for now, can switch to PostgreSQL)

The code is organized into layers:
- **API** - Handles HTTP requests
- **Services** - Contains business logic
- **Repositories** - Talks to the database
- **Core** - Database models and configuration

Pretty standard stuff, but keeps things clean and testable.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Azure DevOps account with Personal Access Token (PAT)
- pip

### Installation

1. **Clone and navigate to the project**
```bash
cd /applix-devops
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  
# On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```
Getting Started

### What you need

- Python 3.9 or higher
- An Azure DevOps account with a Personal Access Token (PAT)
- That's it

### Setup

**1. Set up Python environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configure your Azure DevOps credentials**

Copy the example file and add your details:
```bash
cp .env.example .env
```

Edit `.env` and add:
```env
AZURE_DEVOPS_ORG=your-organization-name
AZURE_DEVOPS_PROJECT=your-project-name
AZURE_DEVOPS_PAT=your-personal-access-token

DATABASE_URL=your-postgres-url
```

**3. Start the API server**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**4. Start the worker (in a new terminal)**

```bash
source venv/bin/activate
python3 worker_daemon.py
```

That's it! The API is running on port 8000.

### Try it out

**Check if it's running:**
```bash
curl http://127.0.0.1:8000/health
```

Project Structure

```
src/
├── api/                    # API endpoints and routing
│   ├── routes/            # Your HTTP endpoints live here
│   └── dependencies/      # Dependency injection stuff
│
├── core/                   # Core application components
│   ├── config.py          # Configuration and env variables
│   ├── constants.py       # Constants and enums
│   ├── database.py        # Database setup
│   └── models.py          # Database models
│
├── services/              # Business logic
│   ├── user_story_service.py
│   ├── event_queue_service.py
│   ├── azure_devops_service.py
│   └── event_processor.py
│
├── repositories/          # Database operations
│   ├── base.py
│   ├── event_repository.py
│   └── user_story_repository.py
│
├── schemas/               # Request/response validation
│   ├── user_story.py
│   └── event.py
│
├── utils/                 # Helper functions
│   ├── logger.py
│   └── azure_devops.py
│
└── main.py                # FastAPI app entry point

worker_daemon.py           # Background worker process
```

The structure keeps things organized:
- **Routes** handle HTTP stuff
- **Services** contain the actual logic
- **Repositories** talk to the database
- **Schemas** validate incoming data

If you need to add a new feature, you'll probably touch a route, service, and repository.
## 📡 API Documentation

### Endpoints

#### Health Check
```http
GET /
GET /health
```


POST /userstory/create

Send a user story, get back an event ID. The worker will process it asynchronously.

Example:
```json
{
  "id": 12345,
  "title": "Build login page",
  "area_path": "Devops-Automation",
  "iteration_path": "Devops-Automation"
}
```


Response:
```json
{
  "status": "accepted",
  "message": "Story #12345 received. Subtasks will be created asynchronously.",
  "story_id": 12345,
  "event_id": 1
}
```

**Get User Story**
```bash
GET /userstory/{story_id}
```
Check the status of a story in the database.

### How the flow works

1. You POST a story to the API
2. API saves it and creates an event
3. Worker daemon picks up the event (polls every 3 seconds)
4. Worker calls Azure DevOps API to create 5 subtasks
5. Worker marks event as completed
6. Done!

All the async stuff happens in the background. The API responds immediately

### Database Schema

**Events Table:**
- `id` - Event ID (Primary Key)
- `event_type` - Type of event (`user_story_created`, etc.)
- `data` - Event payload (JSON)
- `status` - Processing status (`pending`, `processing`, `completed`, `failed`)
- `result` - Processing result (JSON, nullable)
- `error` - Error message (nullable)
- `created_at` - Creation timestamp
- `processed_at` - Processing timestamp (nullable)

**User Stories Table:**
- `id` - Internal ID (Primary Key)
- `azure_story_id` - Azure DevOps story ID (Unique)
- `title` - Story title
- `Configuration

All configuration is in the `.env` file. Here's what you need:

**Required:**
- `AZURE_DEVOPS_ORG` - Your Azure DevOps organization name
- `AZURE_DEVOPS_PROJECT` - Your project name
- `AZURE_DEVOPS_PAT` - Personal Access Token (get this from Azure DevOps settings)
- `DATABASE_URL` - Defaults to SQLite. For production, use PostgreSQL

**Optional:**

- `ENVIRONMENT` - Set to `production` when deploying
- `DEBUG` - Set to `True` for more verbose logging


**Run multiple workers** for better throughput
   ```bash
   python3 worker_daemon.py &
   python3 worker_daemon.py &
   python3 worker_daemon.py &
   ```

That's about it. The app is pretty straightforward to deploy.

---

## Development

**Running in dev mode:**
```bash
uvicorn src.main:app --reload
```

The `--reload` flag auto-restarts when you change code. Pretty handy.

---