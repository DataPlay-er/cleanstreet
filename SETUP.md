# Setup Guide for Development

This guide walks you through setting up the LitterDetect services locally after cloning the repository.

## Before You Push to GitHub

**⚠️ IMPORTANT:** Do not commit files with secrets to Git. The `.gitignore` is configured to exclude:
- `.env` files (environment variables)
- `docker-compose.yml` (with real credentials)
- Virtual environments (`*venv/`)

## Quick Setup

### 1. Set up the Auth Service

```bash
cd services/auth
python -m venv authvenv
source authvenv/Scripts/activate  # On Windows: authvenv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create Environment Configuration

Copy the example file and fill in your values:

```bash
cp .env.example .env
# Edit .env with your actual database, JWT secret, and other credentials
nano .env  # or use your editor
```

**Important values to set:**
- `DATABASE_URL` - your PostgreSQL connection string
- `JWT_SECRET_KEY` - generate a strong secret: `python -c "import secrets; print(secrets.token_hex(64))"`
- `REDIS_URL` - your Redis connection

### 3. Set up Docker Services

Create your local Docker Compose configuration:

```bash
cd ../infra
cp docker-compose.example.yml docker-compose.yml
# Edit docker-compose.yml to add your credentials
nano docker-compose.yml
```

Start the services:

```bash
docker-compose up -d
```

### 4. Run Database Migrations

```bash
cd ../auth
alembic upgrade head
```

### 5. Run Tests

```bash
pytest
```

### 6. Run the Auth Service

```bash
uvicorn app.main:app --reload
```

Access the API at `http://localhost:8000`

---

## Environment Variables Reference

### Auth Service (`.env`)

| Variable | Required | Default | Example |
|----------|----------|---------|---------|
| `ENVIRONMENT` | Yes | - | `development` or `production` |
| `DEBUG` | No | `false` | `true` |
| `DATABASE_URL` | Yes | - | `postgresql://user:pass@localhost:5432/db` |
| `REDIS_URL` | Yes | - | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | Yes | - | 64+ character hex string |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | `15` | Number of minutes |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Number of days |
| `CORS_ORIGINS` | No | - | `["http://localhost:5173"]` |

### Docker Services (`.env` or `docker-compose.yml`)

| Service | Variable | Default | Example |
|---------|----------|---------|---------|
| PostgreSQL | `POSTGRES_PASSWORD` | - | Any secure password |
| MinIO | `MINIO_ROOT_PASSWORD` | - | Any secure password |
| RabbitMQ | `RABBITMQ_DEFAULT_PASS` | - | Any secure password |

---

## What's Safe to Commit

✅ **Safe to commit:**
- `.env.example` - template with placeholder values
- `docker-compose.example.yml` - template with environment variables
- All application source code
- Tests, documentation, and config templates

❌ **Never commit:**
- `.env` - actual environment variables
- `docker-compose.yml` - with real credentials
- `*venv/` directories
- Any file with actual secret keys or passwords

---

## Deploying to Production

1. Generate a strong `JWT_SECRET_KEY`:
   ```bash
   python -c "import secrets; print(secrets.token_hex(64))"
   ```

2. Set all environment variables securely (e.g., in your CI/CD platform or deployment system)

3. Use `ENVIRONMENT=production` and `DEBUG=false`

4. Ensure `CORS_ORIGINS` lists only your actual frontend domain

---

## Troubleshooting

**Cannot connect to PostgreSQL:**
- Verify `DATABASE_URL` is correct
- Check that Docker PostgreSQL service is running: `docker ps`
- Check Docker logs: `docker logs cleansight_postgres`

**JWT token errors:**
- Verify `JWT_SECRET_KEY` is at least 64 characters
- Check that tokens haven't expired

**RabbitMQ connection failed:**
- Verify RabbitMQ credentials in `.env` match `docker-compose.yml`
- Check RabbitMQ is running: `docker ps | grep rabbitmq`

---

For more details, see the main [README.md](../../README.md).
