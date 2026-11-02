"""
Pydantic Schemas Module.

Contains input validation and response schemas for user/employee payloads and tokens.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models import Role

class EmployeeBase(BaseModel):
    """Base Employee schema containing common non-sensitive fields."""
    user_name: str = Field(..., min_length=3, max_length=50, example="john_doe")
    role: Role = Field(default=Role.EMPLOYEE, example="developer")
    salary: Decimal = Field(..., ge=0, example=75000.00)

class EmployeeCreate(EmployeeBase):
    """Schema for creating a new Employee record (User registration)."""
    user_password: str = Field(..., min_length=6, example="securepassword123")

class EmployeeResponse(EmployeeBase):
    """Schema for returning Employee details to client applications."""
    user_id: int = Field(..., alias="id")
    is_active: bool

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class Token(BaseModel):
    """Schema for returning JWT access tokens to client applications."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Internal schema for extracted token payload metadata."""
    user_name: Optional[str] = None