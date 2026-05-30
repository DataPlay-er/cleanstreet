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
│   ├── auth/            # Django auth service
│   ├── ingestion/       # FastAPI upload service
│   ├── detection/       # AI worker
│   ├── live/            # WebSocket service
│   └── notification/    # Email/SMS alerts
├── frontend/            # React dashboard
├── infra/               # Docker Compose, Traefik config
├── shared/              # Shared Python utilities
├── .gitignore
└── README.md
```

## License

MIT License