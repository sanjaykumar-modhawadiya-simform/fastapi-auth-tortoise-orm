"""
Provides employee creation, role-restricted listing, and the logged-in /me endpoint.

Employee Management Router Module.

Exposes CRUD and profile endpoints for employee administration and self-service.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, RoleChecker
from app.exceptions import EntityNotFoundException
from app.models import Employee, Role
from app.schemas import EmployeeCreate, EmployeeResponse
from app.security import hash_password

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker([Role.HR, Role.MANAGER, Role.ADMIN]))]
)
async def create_employee(employee_data: EmployeeCreate):
    """
    Creates a new employee record with specified role.

    Access Restricted: HR, Manager, Admin only.
    """
    existing_user = await Employee.get_or_none(user_name=employee_data.user_name)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{employee_data.user_name}' is already taken."
        )

    hashed_pwd = hash_password(employee_data.user_password)

    employee = await Employee.create(
        user_name=employee_data.user_name,
        user_password=hashed_pwd,
        role=employee_data.role,
        salary=employee_data.salary
    )
    return employee


@router.get("/me", response_model=EmployeeResponse)
async def get_logged_in_user_profile(current_user: Employee = Depends(get_current_user)):
    """
    Retrieves full profile details of the currently authenticated logged-in user.
    """
    return current_user


@router.get(
    "/",
    response_model=List[EmployeeResponse],
    dependencies=[Depends(RoleChecker([Role.HR, Role.MANAGER, Role.ADMIN]))]
)
async def list_all_employees():
    """
    Lists all employees registered in the system.

    Access Restricted: HR, Manager, Admin only.
    """
    return await Employee.all()


@router.get(
    "/{user_id}",
    response_model=EmployeeResponse,
    dependencies=[Depends(RoleChecker([Role.HR, Role.MANAGER, Role.ADMIN]))]
)
async def get_employee_by_id(user_id: int):
    """
    Retrieves employee details by user ID.

    Access Restricted: HR, Manager, Admin only.
    """
    employee = await Employee.get_or_none(id=user_id)
    if not employee:
        raise EntityNotFoundException(entity_name="Employee", identifier=user_id)
    return employee