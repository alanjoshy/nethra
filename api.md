Perfect. Below is your **production-ready `README.md`** document — clean, structured, and suitable for GitHub.

You can copy-paste this directly into your project root as `README.md`.

---

# 🛡️ Nethra Backend API

AI-Driven Crime Analysis & Case Management Backend System

---

## 📌 Overview

Nethra Backend is a production-grade, modular FastAPI application designed for:

* Secure authentication (PASETO-based)
* Role-based access control (RBAC)
* Incident management
* Case lifecycle management
* Media handling
* Geospatial data support (PostGIS)
* Clean architecture with domain separation

---

## 🏗 Architecture

* **Framework**: FastAPI
* **ORM**: SQLAlchemy 2.0 (Async)
* **Database**: PostgreSQL 16 + PostGIS
* **Auth**: PASETO (v4.local)
* **Migrations**: Alembic
* **Background Jobs**: Celery + Redis (planned)
* **Containerization**: Docker

---

## 🚀 Getting Started

### 1️⃣ Clone Repository

```bash
git clone <repo_url>
cd nethraBackend
```

---

### 2️⃣ Setup Environment Variables

Create `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/nethra
SECRET_KEY=your_secret_key
TOKEN_EXPIRE_MINUTES=60
```

---

### 3️⃣ Run Using Docker

```bash
docker-compose up --build
```

Application will be available at:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## 🔐 Authentication

Nethra uses **PASETO v4.local tokens**.

### Login

```
POST /auth/login
```

#### Request

```json
{
  "email": "admin@gmail.com",
  "password": "password123"
}
```

#### Response

```json
{
  "access_token": "v4.local.xxxxxx",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "Admin",
    "email": "admin@gmail.com",
    "role": "admin",
    "is_active": true,
    "created_at": "timestamp"
  }
}
```

### Using Token

Send header:

```
Authorization: Bearer <access_token>
```

---

# 📡 API Modules

---

# 👤 Users Module (Admin Only)

Base: `/users`

| Method | Endpoint           | Description     |
| ------ | ------------------ | --------------- |
| POST   | `/users`           | Create user     |
| GET    | `/users`           | List users      |
| GET    | `/users/{user_id}` | Get user        |
| PUT    | `/users/{user_id}` | Update user     |
| DELETE | `/users/{user_id}` | Deactivate user |

---

# 🚨 Incidents Module

Base: `/incidents`

| Method | Endpoint          | Description     |
| ------ | ----------------- | --------------- |
| POST   | `/incidents`      | Create incident |
| GET    | `/incidents`      | List incidents  |
| GET    | `/incidents/{id}` | Get incident    |
| PUT    | `/incidents/{id}` | Update incident |
| DELETE | `/incidents/{id}` | Delete incident |

Supports PostGIS geography (`POINT(long lat)`).

---

# 📁 Cases Module

Base: `/cases`

| Method | Endpoint             | Description        |
| ------ | -------------------- | ------------------ |
| POST   | `/cases`             | Create case        |
| GET    | `/cases`             | List cases         |
| GET    | `/cases/{id}`        | Get case           |
| PUT    | `/cases/{id}`        | Update case        |
| PATCH  | `/cases/{id}/status` | Update case status |
| DELETE | `/cases/{id}`        | Delete case        |

Status updates are recorded in `case_status_history`.

---

# 📷 Media Module

Base: `/media`

| Method | Endpoint          | Description  |
| ------ | ----------------- | ------------ |
| POST   | `/media`          | Upload media |
| GET    | `/media?case_id=` | List media   |
| GET    | `/media/{id}`     | Get media    |
| DELETE | `/media/{id}`     | Delete media |

---

# 🩺 Health Endpoints

| Method | Endpoint     | Description                 |
| ------ | ------------ | --------------------------- |
| GET    | `/health`    | Basic health check          |
| GET    | `/health/db` | Database connectivity check |

Database health includes automatic retry mechanism.

---

# 🛑 Standard Error Format

All errors follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

---

# 🔐 Role-Based Access Control

| Role    | Permissions                |
| ------- | -------------------------- |
| admin   | Full access                |
| officer | Incident & case management |
| analyst | Read-only access           |

Permissions are validated from database, not token claims alone.

---

# 🧾 HTTP Status Codes

| Code | Meaning          |
| ---- | ---------------- |
| 200  | Success          |
| 201  | Created          |
| 204  | Deleted          |
| 400  | Validation error |
| 401  | Unauthorized     |
| 403  | Forbidden        |
| 404  | Not found        |
| 409  | Conflict         |
| 500  | Internal error   |

---

# 🛡 Security Features

* Password hashing (bcrypt)
* PASETO token authentication
* Token expiration enforcement
* Role-based authorization
* Soft deletes for user safety
* Structured exception handling

---

# 🧩 Project Structure

```
app/
 ├── modules/
 │   ├── auth/
 │   ├── users/
 │   ├── incidents/
 │   ├── cases/
 │   └── media/
 ├── core/
 ├── shared/
 └── main.py
```

Clean separation:

* Controllers
* Services
* Repositories
* Entities
* Schemas

---

# 📊 API Coverage

| Module    | API Count   |
| --------- | ----------- |
| Auth      | 1           |
| Users     | 5           |
| Incidents | 5           |
| Cases     | 6           |
| Media     | 4           |
| Health    | 2           |
| **Total** | **23 APIs** |

---

# 🧠 Future Enhancements

* Pagination & filtering
* Search endpoints
* Audit logging
* API versioning (`/api/v1`)
* Refresh token flow
* Rate limiting
* Background AI analysis

---

# 👨‍💻 Development Notes

* Async-first design
* SQLAlchemy 2.0 style
* Modular monolith architecture
* Production-ready patterns

---

# 📜 License

Internal / Proprietary

---

If you'd like, I can next:

* Add **API versioning structure**
* Create a **Postman collection export**
* Generate a **backend architecture diagram**
* Add **deployment guide (production server)**

Just tell me what you want next.
