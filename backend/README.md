# Cat Canteen Backend

可白牌化智慧餐飲訂單系統平台 - Backend API

## Tech Stack

- Python 3.11+
- FastAPI 0.109+
- SQLAlchemy 2.x
- PostgreSQL 15+
- Alembic (database migrations)
- UV (package management)

## Development Setup

1. Create virtual environment:
```bash
uv venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
uv pip install -e ".[dev]"
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start development server:
```bash
uvicorn src.api.main:app --reload
```

## Testing

```bash
pytest
```

## Project Structure

```
backend/
├── src/
│   ├── domain/         # Business entities and logic
│   ├── application/    # Use cases
│   ├── infrastructure/ # External services (DB, auth)
│   └── api/           # FastAPI routes and schemas
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
└── migrations/        # Alembic migrations
```
