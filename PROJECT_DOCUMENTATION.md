# Nethra Backend — Project Documentation (Interview)

This document summarizes the **Nethra** backend project for technical interviews. It covers tech stack, architecture, features, data model, security, and future direction (including AI).

---

## 1. Project Overview

**Nethra** is an **AI-driven crime analysis platform (backend)**. It is a technical prototype built for:

- Learning and system design practice  
- Interview-grade backend demonstration  
- Structured crime data ingestion and geospatial analysis  
- **Foundations for future AI-driven analysis** (not yet implemented)

**Disclaimer:** The project does not claim real-world enforcement accuracy or operational use.

---

## 2. Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.11+ |
| **Framework** | FastAPI (async) |
| **API** | REST, JSON |
| **Database** | PostgreSQL |
| **Geospatial** | PostGIS + GeoAlchemy2 |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Driver** | asyncpg |
| **Migrations** | Alembic |
| **Auth** | PASETO (v4 local) + Argon2 password hashing |
| **Validation** | Pydantic 2.x (with email extras) |
| **Config** | pydantic-settings, `.env` |
| **Containerization** | Docker, Docker Compose |
| **Package management** | Poetry |
| **Testing** | pytest (dev) |

**Why these choices (for interview):**

- **FastAPI:** Async, automatic OpenAPI docs, type hints, high performance.  
- **PostgreSQL + PostGIS:** Geospatial from day one (incident locations as points).  
- **SQLAlchemy 2.0 async:** Non-blocking DB access, modern patterns.  
- **PASETO:** Stateless, secure tokens (alternative to JWT).  
- **Argon2:** Strong password hashing (via passlib).  
- **Modular monolith:** Clear boundaries, easy to explain and evolve.

---

## 3. Architecture

### 3.1 Style: Modular Monolith

- **Single deployable** application with **domain modules** that could later become services.  
- Clear **module boundaries** and **public APIs** to avoid spaghetti imports.  
- **Shared** layer only for cross-cutting concerns (DB, security, exceptions, responses).

### 3.2 High-Level Structure

```
app/
├── main.py                    # Entry point, routers, startup
├── core/                      # Config, DB engine, security, dependencies, health
├── common/                    # Constants, exceptions, responses, pagination
├── modules/                   # Domain modules (microservice-ready)
│   ├── auth/                  # Login, PASETO tokens
│   ├── users/                 # User CRUD, admin-only operations
│   ├── cases/                 # Case management (anchored by incident)
│   ├── incidents/             # Incident reporting (with location)
│   └── media/                 # Media evidence linked to cases
└── shared/                    # Cross-cutting
    ├── database/              # Session, models, auto-migrate
    ├── security/              # Re-exports from core (hashing, tokens)
    ├── constants/             # Re-exports (roles, statuses, auth)
    ├── exceptions/            # Re-exports custom exceptions
    ├── middleware/            # Exception handlers
    ├── responses/             # ErrorResponse, etc.
    └── communication/        # Internal Service Bus (inter-module)
```

### 3.3 Per-Module Layout

Each domain module follows the same pattern:

- **entities/** — SQLAlchemy domain models (DB mapping).  
- **repositories/** — Data access (queries, CRUD).  
- **services/** — Business logic (orchestration, validation).  
- **controllers/** — HTTP endpoints (request/response only).  
- **schemas/** — Pydantic request/response models.

**Rule:** Other code must import only from the module’s public API (e.g. `from app.modules.auth import auth_router, AuthService`), not from internal paths.

### 3.4 Inter-Module Communication

- **Internal Service Bus** (`app.shared.communication`): modules register services; others obtain them via `get_service_bus().get_service("users")` (or similar).  
- Avoids direct cross-module imports and keeps boundaries clear for a future split into services.

### 3.5 Database and Migrations

- **Single PostgreSQL database** with **PostGIS** enabled.  
- **Alembic** for migrations; initial schema creates `users`, `incidents` (with geography), `cases`, `case_status_history`, `media`.  
- **Auto-migrate** (optional) in development: on startup, compares models to DB and can generate/apply migrations.

---

## 4. Features

### 4.1 Implemented Features

| Feature | Description | Module |
|--------|-------------|--------|
| **Authentication** | Login with email/password; returns PASETO token + user info | auth |
| **User management** | CRUD for users (create, list, get, update, deactivate); admin-only | users |
| **Case model** | Case entity anchored to one primary incident; status, notes | cases |
| **Incident model** | Incident with type, description, time, **location (PostGIS point)** | incidents |
| **Media model** | Media evidence (file path, type, camera, timestamps) linked to case | media |
| **Case status history** | Audit log for status changes (who, when, old/new status) | cases |
| **Health checks** | `/health`, `/health/db` | core |
| **Structured errors** | Custom exceptions (auth, not found, validation, conflict, etc.) and global handlers | common, shared |
| **Admin creation** | Script `create_admin.py` to create an admin user | scripts |

### 4.2 API Endpoints (Current)

- **Auth**
  - `POST /auth/login` — Login; body: `{ "email", "password" }`; returns token + user.
- **Users** (admin-only, token required)
  - `POST /users` — Create user.  
  - `GET /users` — List users.  
  - `GET /users/{user_id}` — Get user.  
  - `PUT /users/{user_id}` — Update user.  
  - `DELETE /users/{user_id}` — Deactivate user.
- **Health**
  - `GET /health` — App ok.  
  - `GET /health/db` — DB connectivity.

**Note:** Cases, incidents, and media have **services and repositories** (and entities) but **no HTTP controllers/schemas yet**; they are ready for you to expose as needed.

---

## 5. Data Model and Domain

### 5.1 Entities and Relationships

- **User** — id, name, email, password_hash, role (admin/officer/analyst), is_active, created_at.  
  - Roles and statuses are centralized in `common.constants` (e.g. `UserRole`, `CaseStatus`, `IncidentType`, `MediaType`).

- **Incident** — id, reported_by (FK → users), incident_type, description, occurred_at, **location (Geography POINT, SRID 4326)**, created_at, notes.  
  - **Geospatial:** PostGIS `Geography(POINT, 4326)` with GIST index for spatial queries.

- **Case** — id, primary_incident_id (FK → incidents, unique), title, status, created_at, notes.  
  - One case per primary incident; case has one primary incident.

- **CaseStatusHistory** — id, case_id, old_status, new_status, changed_by (FK → users), changed_at.  
  - Audit trail for case status changes.

- **Media** — id, case_id, file_path, media_type, camera_type, capture_time, uploaded_at.  
  - Evidence attached to a case.

### 5.2 Geospatial

- **PostGIS** extension enabled in migrations.  
- **GeoAlchemy2** for ORM mapping of `Geography(geometry_type="POINT", srid=4326)`.  
- Migration adds spatial index on `incidents.location` for efficient spatial queries.  
- Ready for future features: “incidents near point”, “incidents in area”, heatmaps, etc.

---

## 6. Security

- **Passwords:** Argon2 via passlib (no plain-text storage).  
- **Tokens:** PASETO v4 local (symmetric); payload includes `sub` (user id), `role`, `iat`, `exp`.  
- **Token TTL:** 60 minutes (configurable via constant).  
- **Auth flow:** Login → validate credentials → issue PASETO → client sends token in `Authorization: Bearer <token>`.  
- **Authorization:** `get_current_user` dependency (decode token, load user, check active); `require_admin` for admin-only routes.  
- **Security utilities** are centralized in `core.security` and re-exported via `shared.security` for use across modules.

---

## 7. AI Models and Future AI Work

- **Current state:** The codebase does **not** yet integrate any AI/ML models (no OpenAI, no embeddings, no inference endpoints).  
- **Stated goal:** The README describes the backend as preparing **foundations for AI-driven analysis (future phases)**.  
- **What’s in place for AI later:**  
  - **Structured data:** Cases, incidents, media with clear types and relationships.  
  - **Geospatial:** Location data ready for spatial analytics or location-aware AI.  
  - **Modular design:** A dedicated “AI” or “insights” module could be added without touching auth/users/cases/incidents.  
  - **Service bus:** AI services could be registered and consumed by other modules in a controlled way.

**For the interview you can say:**  
“The system is designed with clean boundaries and rich domain models (cases, incidents, media, geospatial) so we can plug in AI later—e.g. for pattern detection, risk scoring, or evidence analysis—without rewriting the core. No AI models are integrated yet; that’s the planned next phase.”

---

## 8. Deployment and Run

- **Config:** Environment variables (e.g. `DATABASE_URL`, `AUTO_MIGRATE`, `ENVIRONMENT`) via `.env` and pydantic-settings.  
- **Docker:** Dockerfile (Python 3.11, Poetry, copy app, uvicorn on port 8000).  
- **Docker Compose:** Single service `api` (build from Dockerfile, env_file, host network).  
- **Start:** `uvicorn app.main:app --host 0.0.0.0 --port 8000` (or via Docker).

---

## 9. Summary for Interview Talking Points

1. **What it is:** Backend for an AI-oriented crime analysis platform; currently focused on auth, users, and domain model (cases, incidents, media) with geospatial support.  
2. **Tech stack:** Python 3.11, FastAPI (async), PostgreSQL + PostGIS, SQLAlchemy 2.0 async, PASETO + Argon2, Docker.  
3. **Architecture:** Modular monolith with strict module boundaries, repository/service/controller split, and an internal service bus for inter-module communication.  
4. **Features:** Login, user CRUD (admin), case/incident/media domain model, geospatial incidents, case status history, health checks, structured error handling.  
5. **AI:** No AI models yet; architecture and data model are prepared for future AI-driven analysis (you can describe where you’d plug it in).  
6. **Design decisions:** Async end-to-end, security (PASETO, Argon2), geospatial from day one, and a migration path toward microservices or dedicated AI services.

Use this document as the single source of truth when presenting Nethra in an interview: tech stack, features, data model, security, and AI roadmap.
