# Cleansight

An AI-powered litter detection and monitoring system for cleaner streets and public spaces.

## Architecture

Cleansight is built as a microservices architecture with the following components:

### Services

| Service | Technology | Description |
|---------|------------|-------------|
| `services/auth` | Django + DRF | Authentication & user management service |
| `services/ingestion` | FastAPI | Image/video upload and preprocessing service |
| `services/detection` | Python + PyTorch/TensorFlow | AI worker for litter detection in images |
| `services/live` | FastAPI + WebSockets | Real-time monitoring dashboard backend |
| `services/notification` | Python | Email/SMS alert service for detected litter |

### Frontend

| Component | Technology | Description |
|-----------|------------|-------------|
| `frontend` | React + TypeScript | Web dashboard for monitoring and management |

### Infrastructure

| Component | Description |
|-----------|-------------|
| `infra` | Docker Compose configurations, Traefik reverse proxy setup |
| `shared` | Shared Python utilities, common models, and type definitions |

## Development Phases

- **Phase 2**: Django authentication service
- **Phase 4**: Ingestion, detection, live, and notification services
- **Phase 5**: React dashboard
- **Phase 6**: Docker Compose and Traefik configuration

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd cleansight

# Set up virtual environment (for Python services)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for each service
# (See individual service READMEs for details)

# Start all services with Docker Compose
cd infra
docker-compose up -d
```

## Project Structure

```
cleansight/
├── services/
│   ├── auth/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py              # FastAPI app instance, mounts router
│   │   │   ├── config.py            # Settings (secret key, DB url, Redis url)
│   │   │   ├── database.py          # SQLModel engine + get_session dependency
│   │   │   ├── models.py            # User SQLModel (table=True)
│   │   │   ├── schemas.py           # Request/response Pydantic shapes
│   │   │   ├── router.py            # /register, /login, /me, /refresh routes
│   │   │   ├── auth.py              # passlib hashing + python-jose token logic
│   │   │   └── dependencies.py      # get_current_user (JWT guard, reusable)
│   │   ├── migrations/              # Alembic folder (auto-generated)
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/            # One .py file per migration
│   │   ├── tests/
│   │   │   ├── test_register.py
│   │   │   └── test_login.py
│   │   ├── alembic.ini              # Alembic config (points to DB url)
│   │   ├── Dockerfile               # Added in Phase 6, placeholder for now
│   │   └── requirements.txt
│   │
│   ├── ingestion/       # Phase 4
│   ├── detection/       # Phase 3
│   ├── live/            # Phase 4
│   └── notification/    # Phase 4
│
├── frontend/            # Phase 5
├── infra/               # Phase 1 (docker-compose.yml lives here)
├── shared/              # JWT verification dependency (shared in Phase 4)
├── .gitignore
└── README.md
```

## License

MIT License