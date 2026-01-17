# Login Response Flow Analysis

This document explains how the login endpoint responds, including all files involved in the process.

## 📋 Overview

The login flow follows this path:
1. **Request Entry** → `app/api/auth/login.py`
2. **Service Layer** → `app/services/auth.py`
3. **Database Query** → `app/queries/user.py`
4. **Security** → `app/core/security.py`
5. **Response Building** → `app/schemas/auth.py`
6. **Error Handling** → `app/common/exceptions.py` + `app/core/exception_handlers.py`
7. **Constants** → `app/common/constants.py`
8. **Error Definitions** → `app/common/errors.py`

---

## 🔄 Complete Flow Diagram

```
POST /auth/login
    ↓
app/api/auth/login.py (login endpoint)
    ↓
app/services/auth.py (login_user function)
    ↓
    ├─→ app/queries/user.py (get_active_user_by_email)
    ├─→ app/core/security.py (verify_password)
    └─→ app/core/security.py (create_access_token)
    ↓
app/schemas/auth.py (LoginResponse model)
    ↓
Response sent to client
```

---

## 📁 Files Involved

### 1. **Entry Point: Login Endpoint**
**File:** `app/api/auth/login.py`

**What it does:**
- Receives POST request at `/auth/login`
- Validates request using `LoginRequest` schema
- Calls `login_user` service function
- Builds `LoginResponse` with token and user data
- Handles `AuthenticationError` exceptions

**Key Code:**
```python
@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    try:
        access_token, token_type, user = await login_user(...)
        return LoginResponse(access_token=..., token_type=..., user=...)
    except AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
```

**Imports:**
- `LoginRequest`, `LoginResponse`, `UserResponse` from `app.schemas.auth`
- `login_user` from `app.services.auth`
- `AuthenticationError` from `app.common.exceptions`

---

### 2. **Service Layer: Business Logic**
**File:** `app/services/auth.py`

**What it does:**
- Contains `login_user()` - main login orchestration
- Contains `authenticate_user()` - validates credentials
- Contains `generate_auth_token()` - creates JWT token
- Raises `AuthenticationError` on failure

**Key Functions:**

**`authenticate_user()`:**
- Calls `get_active_user_by_email()` from `app/queries/user.py`
- If user not found → raises `AuthenticationError` with message "Invalid email or password"
- Calls `verify_password()` from `app/core/security.py`
- If password invalid → raises `AuthenticationError` with message "Invalid email or password"

**`generate_auth_token()`:**
- Calls `create_access_token()` from `app/core/security.py`
- Uses `Auth.TOKEN_TYPE` constant from `app/common/constants.py`
- Returns dict with `access_token` and `token_type`

**`login_user()`:**
- Orchestrates the full flow
- Returns tuple: `(access_token, token_type, user)`

**Imports:**
- `get_active_user_by_email` from `app.queries.user`
- `verify_password`, `create_access_token` from `app.core.security`
- `AuthenticationError` from `app.common.exceptions`
- `Auth` from `app.common.constants`

---

### 3. **Database Queries**
**File:** `app/queries/user.py`

**What it does:**
- `get_active_user_by_email()` - fetches active user from database
- Returns `User` object or `None` if not found

**Key Code:**
```python
async def get_active_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.email == email, User.is_active == True)
    )
    return result.scalar_one_or_none()
```

---

### 4. **Security Functions**
**File:** `app/core/security.py`

**What it does:**
- `verify_password()` - checks if password matches hash
- `create_access_token()` - generates PASETO token
- Uses `TOKEN_TTL_MINUTES` constant (60 minutes)

**Key Functions:**
- `verify_password(password, password_hash)` → returns `bool`
- `create_access_token(user_id, role)` → returns `str` (token)

---

### 5. **Response Schemas**
**File:** `app/schemas/auth.py`

**What it does:**
- Defines Pydantic models for request/response validation
- `LoginRequest` - validates incoming login data
- `LoginResponse` - structures successful login response
- `UserResponse` - structures user data in response

**Response Structure:**
```python
LoginResponse:
    access_token: str
    token_type: str (default: "bearer")
    user: UserResponse
        id: str
        name: str
        email: str
        role: str
        is_active: bool
        created_at: str (ISO format)
```

---

### 6. **Exception Handling**
**File:** `app/common/exceptions.py`

**What it does:**
- Defines `AuthenticationError` exception class
- Inherits from `NethraException`
- Sets status code to `401`
- Sets error code to `"AUTHENTICATION_ERROR"`

**Key Code:**
```python
class AuthenticationError(NethraException):
    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )
```

**File:** `app/core/exception_handlers.py`

**What it does:**
- `nethra_exception_handler()` - handles all `NethraException` subclasses
- Converts exception to `ErrorResponse` format
- Returns JSON response with proper status code

**Error Response Structure:**
```python
ErrorResponse:
    success: bool (False)
    error: str (error code)
    message: str (human-readable message)
    details: dict (optional additional info)
```

**Note:** In `login.py`, `AuthenticationError` is caught and converted to `HTTPException` directly, so the exception handler may not be used for login errors. However, it's available for other endpoints.

---

### 7. **Constants**
**File:** `app/common/constants.py`

**What it does:**
- Defines `Auth` class with authentication constants
- `Auth.TOKEN_TYPE = "bearer"` - used in token generation
- `Auth.TOKEN_TTL_MINUTES = 60` - token expiration time

**Usage:**
- Used in `app/services/auth.py` → `generate_auth_token()` function

---

### 8. **Error Definitions (Reference)**
**File:** `app/common/errors.py`

**What it does:**
- Defines standardized error codes and messages
- Contains `AUTH_ERRORS` dictionary with error details
- **Note:** This file defines error structures but is NOT directly used in the login flow
- The login flow uses `AuthenticationError` exception class instead

**Available Auth Errors:**
- `INVALID_CREDENTIALS`
- `TOKEN_EXPIRED`
- `TOKEN_INVALID`
- `MISSING_TOKEN`

---

### 9. **Application Setup**
**File:** `app/main.py`

**What it does:**
- Registers the auth router
- Sets up global exception handlers
- Initializes FastAPI application

**Key Code:**
```python
app.add_exception_handler(NethraException, nethra_exception_handler)
app.include_router(auth_router)
```

---

## ✅ Success Response Flow

1. **Request** → `POST /auth/login` with `{email, password}`
2. **Validation** → `LoginRequest` schema validates input
3. **Service Call** → `login_user()` in `app/services/auth.py`
4. **User Lookup** → `get_active_user_by_email()` in `app/queries/user.py`
5. **Password Check** → `verify_password()` in `app/core/security.py`
6. **Token Generation** → `create_access_token()` in `app/core/security.py`
7. **Response Building** → `LoginResponse` in `app/schemas/auth.py`
8. **Return** → JSON response with token and user data

**Success Response:**
```json
{
  "access_token": "v4.local.xxx...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

---

## ❌ Error Response Flow

### Scenario 1: User Not Found or Inactive
1. `get_active_user_by_email()` returns `None`
2. `authenticate_user()` raises `AuthenticationError("Invalid email or password")`
3. `login()` endpoint catches exception
4. Raises `HTTPException(status_code=401, detail="Invalid email or password")`

**Error Response:**
```json
{
  "detail": "Invalid email or password"
}
```

### Scenario 2: Invalid Password
1. `verify_password()` returns `False`
2. `authenticate_user()` raises `AuthenticationError("Invalid email or password")`
3. `login()` endpoint catches exception
4. Raises `HTTPException(status_code=401, detail="Invalid email or password")`

**Error Response:**
```json
{
  "detail": "Invalid email or password"
}
```

### Scenario 3: Validation Error (Invalid Request Format)
1. Pydantic validation fails on `LoginRequest`
2. FastAPI automatically raises `RequestValidationError`
3. `validation_exception_handler()` in `app/core/exception_handlers.py` handles it
4. Returns `ErrorResponse` with status `422`

**Error Response:**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Invalid request data",
  "details": {
    "errors": [...]
  }
}
```

---

## 🔗 File Dependency Graph

```
app/main.py
    ├─→ app/api/auth/login.py
    │       ├─→ app/services/auth.py
    │       │       ├─→ app/queries/user.py
    │       │       ├─→ app/core/security.py
    │       │       ├─→ app/common/exceptions.py
    │       │       └─→ app/common/constants.py
    │       ├─→ app/schemas/auth.py
    │       └─→ app/common/exceptions.py
    └─→ app/core/exception_handlers.py
            └─→ app/common/responses.py
```

---

## 📝 Summary

**Files Directly Used in Login Response:**
1. ✅ `app/api/auth/login.py` - Entry point
2. ✅ `app/services/auth.py` - Business logic
3. ✅ `app/queries/user.py` - Database access
4. ✅ `app/core/security.py` - Password & token operations
5. ✅ `app/schemas/auth.py` - Request/response models
6. ✅ `app/common/exceptions.py` - Error classes
7. ✅ `app/common/constants.py` - Constants (TOKEN_TYPE)
8. ✅ `app/core/exception_handlers.py` - Error formatting (for validation errors)
9. ✅ `app/common/responses.py` - ErrorResponse model (used by handlers)

**Files NOT Directly Used (but related):**
- ⚠️ `app/common/errors.py` - Defines error codes but not used in login flow
- ✅ `app/main.py` - Registers router and handlers

---

## 🎯 Key Takeaways

1. **Login endpoint** (`login.py`) is the entry point
2. **Service layer** (`auth.py`) orchestrates authentication
3. **Exceptions** (`exceptions.py`) define error types
4. **Constants** (`constants.py`) provide token type
5. **Schemas** (`auth.py`) structure responses
6. **Exception handlers** format errors consistently
7. **Error messages** come from exception classes, not `errors.py` dictionary
