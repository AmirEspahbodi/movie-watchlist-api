# Movie Watchlist API

A production-style **FastAPI** backend for managing movies, genres, watchlists, and ratings, built using **layered clean architecture principles** with **ArchiPy**.

This project is designed as a maintainable API service with explicit boundaries between HTTP transport, business rules, and persistence. It includes authentication, role-based authorization (admin/user), async PostgreSQL access, migration support, and both unit/integration-style and behavior-driven tests.

---

## Table of Contents

- [What This Project Does](#what-this-project-does)
- [Key Features](#key-features)
- [Architecture and Design](#architecture-and-design)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [API Surface](#api-surface)
- [Security Model](#security-model)
- [Data Model Overview](#data-model-overview)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Database and Migrations](#database-and-migrations)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Common Improvement Opportunities](#common-improvement-opportunities)
- [License](#license)

---

## What This Project Does

The API supports a complete movie watchlist workflow:

- User registration and login with JWT access + refresh tokens.
- Admin-managed catalogs for genres and movies.
- User watchlist management with explicit watch status.
- User ratings constrained to watched movies and valid score range.

The app is bootstrapped in `manage.py`, where the DI container is wired and route dispatching is centralized.

---

## Key Features

- **FastAPI v1 REST endpoints** under `/api/v1/*`.
- **Dependency injection** via `dependency-injector` container wiring.
- **Layered architecture**:
  - `controllers` (transport)
  - `logics` (application/business rules)
  - `repositories` + DB adapters (persistence)
- **Asynchronous PostgreSQL access** using ArchiPy SQLAlchemy adapters.
- **Alembic migrations** for schema evolution.
- **JWT auth** with separate access and refresh token semantics.
- **Role checks** (superuser/admin) for protected management routes.
- **BDD scenarios** (Behave) for user journeys.
- **Strict code quality setup** (Ruff, Black, MyPy, pre-commit).

---

## Architecture and Design

### Layered Clean Architecture (ArchiPy-oriented)

The codebase follows a layered design that isolates concerns:

1. **Controllers (`src/controllers`)**
   - FastAPI routes and request/response DTO mapping.
   - Authentication/authorization dependencies.
   - No direct SQL/database code.

2. **Logic Layer (`src/logics`)**
   - Core business rules and orchestration.
   - Validates workflows (e.g., auth checks, watch/rating behavior).
   - Transaction boundaries via `@async_postgres_sqlalchemy_atomic_decorator`.

3. **Repositories (`src/repositories`)**
   - Repository façade per aggregate area (`movie`, `genre`, `watch`, `rating`, `user`).
   - Delegates to concrete PostgreSQL adapters.

4. **Adapters (`src/repositories/*/adapters`)**
   - SQLAlchemy query construction and persistence logic.
   - DB exception mapping (e.g., unique violations -> domain errors).

5. **Models (`src/models`)**
   - SQLAlchemy entities and DTO contracts.
   - Typed enums for sort/status routing semantics.

### Design Patterns Used

- **Dependency Injection**
  - `ServiceContainer` binds adapters -> repositories -> logic services.
- **Repository Pattern**
  - Persistence hidden behind repository interfaces/facades.
- **DTO/Contract-First Boundaries**
  - Explicit domain/repository DTOs reduce coupling between layers.
- **Adapter Pattern**
  - PostgreSQL adapters encapsulate SQLAlchemy and DB specifics.
- **Transactional Decorator Pattern**
  - ArchiPy atomic decorators define transaction scope cleanly.

---

## Tech Stack

### Runtime

- **Python** `>=3.13,<4`
- **FastAPI** (via ArchiPy fastapi extras)
- **Uvicorn** ASGI runtime
- **ArchiPy** for architecture helpers, errors, and adapters
- **SQLAlchemy (async)** + **asyncpg** for PostgreSQL I/O
- **Alembic** for migrations
- **python-jose[cryptography]** for JWT handling
- **bcrypt** for password hashing
- **Pydantic** DTO/config validation

### Tooling / Quality

- **Poetry** dependency management
- **Ruff** linting
- **Black** formatting
- **MyPy** static typing
- **pre-commit** hook orchestration
- **Pytest** automated tests
- **Behave** BDD scenarios

### Infrastructure

- **Docker / Docker Compose** for app + PostgreSQL local environment

---

## Repository Structure

```text
.
├── manage.py                    # App bootstrap + uvicorn startup
├── src/
│   ├── configs/                 # Runtime config, DI container, router dispatch
│   ├── controllers/             # FastAPI route handlers by bounded area/version
│   ├── logics/                  # Business logic layer
│   ├── repositories/            # Repository facades + DB adapters
│   ├── models/
│   │   ├── dtos/                # Domain/repository DTO contracts
│   │   ├── entities/            # SQLAlchemy entities
│   │   └── types/               # Enums and typed route metadata
│   └── utils/                   # JWT, auth dependencies, security helpers
├── migrations/                  # Alembic revisions
├── scripts/                     # Operational scripts (e.g., superuser bootstrap)
├── features/                    # Behave BDD features + steps
├── tests/                       # Automated tests
├── docker-compose.yml           # Local stack orchestration
├── Dockerfile                   # Container image build
└── pyproject.toml               # Dependencies + tooling configuration
```

---

## API Surface

Base path groups configured in dispatcher:

- `/api/v1/auth`
  - register, login, refresh token, current user profile (`/me`)
- `/api/v1/users`
  - admin CRUD/search for users
- `/api/v1/genres`
  - admin CRUD/search for genres
- `/api/v1/movies`
  - admin CRUD/search for movies
- `/api/v1/watchlist`
  - user watchlist create/update/search/get/delete
- `/api/v1/ratings`
  - user rating create/update/search/get

Use Swagger UI in local runtime:

- `http://localhost:8100/docs`
- `http://localhost:8100/redoc`

---

## Security Model

- **Password hashing**: bcrypt salted hash (`SecurityUtils`).
- **JWT model**:
  - Access token (`type=access`, 15 min expiry)
  - Refresh token (`type=refresh`, 7 day expiry)
- **Auth guard dependency** validates bearer token and extracts `user_uuid`.
- **Admin guard dependency** ensures `is_super_user = true` for protected routes.
- **Error mapping** uses structured ArchiPy errors (`UnauthenticatedError`, `PermissionDeniedError`, `NotFoundError`, etc.).

---

## Data Model Overview

Core entities:

- `users`
- `genres`
- `movies` (FK -> `genres`)
- `user_watch_movie` (association user <-> movie + status)
- `user_rate_movie` (association user <-> movie + score)

Notable constraints:

- Rating score check: `1 <= score <= 5`.
- Watch status persisted as string enum-like value (avoids PostgreSQL enum migration complexity).

---

## Getting Started

### 1) Prerequisites

- Docker + Docker Compose
- (Optional local tooling) Python 3.13+ and Poetry

### 2) Start services

```bash
docker compose up --build
```

### 3) Run migrations

```bash
docker compose exec web poetry run alembic upgrade head
```

### 4) Initialize first superuser

```bash
docker compose exec web poetry run python scripts/init_superuser.py
```

### 5) Access docs

- Swagger: `http://localhost:8100/docs`
- ReDoc: `http://localhost:8100/redoc`

---

## Configuration

Runtime config is loaded through `RuntimeConfig` (extends ArchiPy `BaseConfig`) and environment variables.

At minimum, define values for:

- **Database** (used by ArchiPy postgres adapter + compose)
  - `POSTGRES_SQLALCHEMY__HOST`
  - `POSTGRES_SQLALCHEMY__PORT`
  - `POSTGRES_SQLALCHEMY__DATABASE`
  - `POSTGRES_SQLALCHEMY__USERNAME`
  - `POSTGRES_SQLALCHEMY__PASSWORD`
- **Auth**
  - `AUTH__SECRET_KEY`
  - `AUTH__HASH_ALGORITHM`
- **Initial superuser bootstrap**
  - `FIRST_SUPERUSER_EMAIL`
  - `FIRST_SUPERUSER_FIRSTNAME`
  - `FIRST_SUPERUSER_LASTNAME`
  - `FIRST_SUPERUSER_USERNAME`
  - `FIRST_SUPERUSER_PASSWORD`

> Recommendation: store secrets in a local `.env` (excluded from VCS).

---

## Database and Migrations

Create a new migration from model changes:

```bash
docker compose exec web poetry run alembic revision --autogenerate -m "your message"
```

Apply migrations:

```bash
docker compose exec web poetry run alembic upgrade head
```

Rollback one revision:

```bash
docker compose exec web poetry run alembic downgrade -1
```

---

## Development Workflow

Install dependencies locally:

```bash
poetry install --with dev --all-extras
```

Useful Make targets:

```bash
make help         # List commands
make format       # Black formatting
make lint         # Ruff + MyPy
make behave       # BDD feature tests
make pre-commit   # Run all hooks
make clean        # Remove caches/artifacts
```

Run app locally (without Docker) if environment variables and DB are configured:

```bash
poetry run python manage.py
```

---

## Testing

### Pytest

```bash
poetry run pytest
```

### Behave (BDD)

```bash
poetry run behave
```

The BDD features currently cover:

- Authentication journeys
- Movie and genre management workflows
- Rating behavior with watch-status preconditions

---

## Common Improvement Opportunities

For production hardening, consider:

- Add API rate limiting and request throttling.
- Add structured JSON logging and trace correlation IDs.
- Add OpenTelemetry metrics/tracing.
- Add CI for migration checks and contract tests.
- Add stricter refresh token revocation strategy (e.g., rotation/blacklist).
- Replace broad exception leakage in adapters with stricter domain mapping.

---

## License

This project is licensed under the terms described in [LICENSE](LICENSE).
