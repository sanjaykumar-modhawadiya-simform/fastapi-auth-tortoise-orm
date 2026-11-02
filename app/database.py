"""
Registers Tortoise ORM with FastAPI lifecycle.

Database Registration Module.

Utility functions to integrate Tortoise ORM with FastAPI application.
"""

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.config import settings

# Centralized configuration required by Aerich and Tortoise
TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],  # Include aerich model tracking
            "default_connection": "default",
        },
    },
}

def init_db(app: FastAPI) -> None:
    """
    Initializes Tortoise ORM with the given FastAPI application instance.
    Production Grade: generate_schemas is set to False (handled via Aerich migrations).
    """
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        # generate_schemas=True,  # Automatically creates tables if they don't exist. Removed as we are using Aerich for database migration and management
        add_exception_handlers=True,
    )