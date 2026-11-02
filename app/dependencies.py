"""
Handles OAuth2 authentication and Role-Based Access Control (RBAC).

Dependency Injection Module.

Handles authentication parsing and access restriction based on user roles.
"""

"""
Dependency Injection Module.

Handles authentication parsing and access restriction based on user roles using PyJWT.
"""

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt  # Uses PyJWT instead of python-jose

from app.config import settings
from app.models import Employee, Role
from app.schemas import TokenData

# Defines OAuth2 Bearer token URL pointing to auth login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Employee:
    """
    Validates JWT token and extracts the currently logged-in Employee from the database.

    :raises HTTPException: 401 Unauthorized if credentials or token are invalid.
    :return: Authenticated Employee instance.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodes token using PyJWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credentials_exception
        token_data = TokenData(user_name=user_name)
    except jwt.PyJWTError:  # Catches token expiration or signature validation errors in PyJWT
        raise credentials_exception

    user = await Employee.get_or_none(user_name=token_data.user_name)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")

    return user


class RoleChecker:
    """
    Dependency class to enforce role-based access control on routes.
    """

    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Employee = Depends(get_current_user)) -> Employee:
        """
        Verifies if current user has one of the allowed roles.

        :raises HTTPException: 403 Forbidden if user role is unauthorized.
        :return: Authorized Employee instance.
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {[r.value for r in self.allowed_roles]}"
            )
        return current_user