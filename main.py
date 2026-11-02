"""
Main Application Entrypoint.

Initializes FastAPI app instance, binds routers, sets up database connection,
and registers global exception handlers.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.exceptions import (
    EntityNotFoundException,
    validation_exception_handler,
    entity_not_found_exception_handler
)
from app.models import Employee, Role
from app.routers import auth, employees, reports
from app.security import hash_password

app = FastAPI(title=settings.APP_NAME)

# ---------------------------------------------------------
# Configure CORS Middleware for Frontend Access (React Vite)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React Vite default development URL
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(EntityNotFoundException, entity_not_found_exception_handler)

# Include Routers
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(reports.router)

# Register Tortoise ORM
init_db(app)


@app.on_event("startup")
async def seed_initial_admin():
    """
    Startup event hook to automatically create an initial Admin user if none exists.
    """
    admin_exists = await Employee.filter(role=Role.ADMIN).exists()
    if not admin_exists:
        await Employee.create(
            user_name="admin",
            user_password=hash_password("admin123"),
            role=Role.ADMIN,
            salary=100000.00
        )
        print("-> Default initial admin created: username='admin', password='admin123'")


@app.get("/", tags=["Health Check"])
async def root():
    """Root health check endpoint."""
    return {"status": "ok", "message": "Employee Management System API running"}