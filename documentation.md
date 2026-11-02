# Employee Management System API Documentation

## 1. Overview & Architecture

The **Employee Management System** is a lightweight, asynchronous, production-ready RESTful API built with **FastAPI** and **Tortoise ORM**. It provides robust Authentication using **OAuth2 with Password Hashing & JWT tokens**, fine-grained **Role-Based Access Control (RBAC)**, and standardized exception handling.

### Key Features
* **Asynchronous ORM**: Tortoise ORM with `aiosqlite` for non-blocking database queries.
* **JWT Authentication**: Powered by `PyJWT` with configurable token expiration.
* **Native Password Hashing**: Utilizes `bcrypt` directly to securely hash and verify user credentials without legacy library dependencies.
* **Role-Based Access Control (RBAC)**: Custom dependencies (`RoleChecker`) to restrict endpoints based on user roles (`employee`, `developer`, `hr`, `manager`, `admin`).
* **Custom Exception Handling**: Standardized error responses for missing entities (`404`) and validation errors (`422`).
* **Auto-Seeding Admin**: Creates a default `admin` account automatically upon initial startup.

---

## 2. Directory Structure

```text
fastapi-auth-tortoise-orm/
├── app/                  # Main application package
│   ├── __init__.py
│   ├── config.py         # App configuration & settings (pydantic-settings)
│   ├── database.py       # Tortoise ORM connection initialization
│   ├── dependencies.py   # Auth parsing & RBAC dependencies
│   ├── exceptions.py     # Custom exception handlers & exceptions
│   ├── models.py         # Tortoise ORM database models & Role Enum
│   ├── schemas.py        # Pydantic v2 schemas for input validation & output serialization
│   ├── security.py       # Cryptographic functions (bcrypt hashing & PyJWT)
│   └── routers/          # API Route Controllers
│       ├── __init__.py
│       ├── auth.py       # Login & JWT issuing routes
│       └── employees.py  # Employee CRUD & profile endpoints
├── .env                  # Environment variables
├── main.py               # FastAPI entry point, exception mapping & startup seeding
├── db.sqlite3            # SQLite database file (generated automatically)
└── requirements.txt      # Project dependencies
```

---

## 3. How the System Works End-to-End

### System Lifecycle & Request Flow
1. **Application Startup (`main.py`)**:
   - Alembic automatically generates/verifies the postgres database schema.
   - Global exception handlers catch validation errors (`422`) and entity-not-found errors (`404`), returning consistent JSON formats.
   - The `@app.on_event("startup")` hook executes `seed_initial_admin()`, checking if an `admin` user exists. If missing, it creates a default account (`username`: `admin`, `password`: `admin123`).
2. **Authentication Flow (`/api/auth/login`)**:
   - The client sends credentials via standard OAuth2 form data (`username` and `password`).
   - The system retrieves the user from the database, verifies the password using native `bcrypt.checkpw()`, and encodes a signed JWT containing claims (`sub` = username, `role` = user role, `exp` = expiration).
3. **Protected Endpoints & RBAC Validation**:
   - The client passes the JWT in the HTTP header: `Authorization: Bearer <token>`.
   - `get_current_user` extracts and decodes the token using `PyJWT`, fetches the current `Employee` model instance, and validates account status (`is_active`).
   - `RoleChecker([Role.HR, Role.MANAGER, ...])` checks if the authenticated user's assigned role is authorized to perform the requested operation.

---

## 4. Role-Based Access Control (RBAC) Matrix

Roles are defined as an Enum inside `app/models.py`: `employee`, `developer`, `hr`, `manager`, `admin`.

| Endpoint | Method | Allowed Roles | Description |
| :--- | :--- | :--- | :--- |
| `POST /api/auth/login` | `POST` | Public | Authenticates credentials and returns a Bearer JWT Token. |
| `GET /api/employees/me` | `GET` | Any Authenticated User | Returns the full profile details of the currently logged-in user. |
| `POST /api/employees/` | `POST` | `HR`, `MANAGER`, `ADMIN` | Creates a new employee record with specified role and hashed password. |
| `GET /api/employees/` | `GET` | `HR`, `MANAGER`, `ADMIN` | Retrieves a list of all registered employees. |
| `GET /api/employees/{id}` | `GET` | `HR`, `MANAGER`, `ADMIN` | Retrieves details for a specific employee by ID. Returns `404` if missing. |

---

## 5. Client ID & Tenant ID Context

### Why were `client_id` and `tenant_id` omitted in this implementation?
This project was built to prioritize simplicity and clarity for a single-organization application.

* **`tenant_id` (Multi-Tenancy)**: Used in Software-as-a-Service (SaaS) platforms to partition data across multiple distinct customer organizations sharing a single system. Excluding `tenant_id` keeps the query layer straightforward without requiring organization-level scoping filters (`WHERE tenant_id = ...`) on every endpoint.
* **`client_id` (OAuth2 Application Tracking)**: Used in enterprise systems to distinguish *which* frontend application (e.g., Mobile App, Web App, Third-party Integration) is interacting with the auth server. Excluding `client_id` keeps the authentication mechanism directly bound to user accounts.

### How to integrate them in the future:
1. **Tenant ID**: Add a `tenant_id` field to the `Employee` model, embed `tenant_id` into the JWT claims during login, and filter database queries in routes/dependencies to ensure users only access records belonging to their specific tenant.
2. **Client ID**: Introduce a client registration model, require `client_id` during `/api/auth/login`, and validate that incoming token requests originate from registered, active clients.

---

## 6. Installation & Execution Guide

### Prerequisites
* Python 3.10+

### Setup Steps
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration (`.env`)**:
   ```env
   APP_NAME="Employee Management System"
   SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
   ALGORITHM="HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   DATABASE_URL="sqlite://db.sqlite3"
   ```

3. **Run Application**:
   ```bash
   fastapi dev main.py
   ```

4. **Access Swagger Interactive API Docs**:
   Navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

5. **Initial Testing Workflow**:
   * Click **Authorize** or invoke `POST /api/auth/login` with `username: admin` and `password: admin123`.
   * Copy the returned token to authorize further calls.
   * Use `POST /api/employees/` to create users with different roles (`developer`, `hr`, `manager`, etc.).
   * Call `GET /api/employees/me` to inspect the logged-in profile.