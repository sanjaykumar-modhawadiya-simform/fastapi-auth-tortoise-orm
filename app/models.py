"""
Database Models Definition Module.

Defines the Tortoise ORM models and Role Enums used across the application.
"""

from enum import Enum
from tortoise import fields
from tortoise.models import Model

class Role(str, Enum):
    """
    Enumeration representing distinct roles within the system.
    """
    EMPLOYEE = "employee"
    DEVELOPER = "developer"
    HR = "hr"
    MANAGER = "manager"
    ADMIN = "admin"


class Employee(Model):
    """
    Employee database model representing system users and employees.
    """
    id = fields.IntField(pk=True, source_field="user_id")
    user_name = fields.CharField(max_length=50, unique=True, index=True)
    user_password = fields.CharField(max_length=255)
    role = fields.CharEnumField(Role, default=Role.EMPLOYEE)
    salary = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "employees"

    def __str__(self) -> str:
        return f"Employee({self.user_name}, Role: {self.role})"