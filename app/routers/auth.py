"""
Handles login and token generation.

Authentication Router Module.

Exposes endpoints for user authentication and access token retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models import Employee
from app.schemas import Token
from app.security import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates user credentials and returns a Bearer JWT Token.

    :param form_data: OAuth2 form containing username and password.
    """
    user = await Employee.get_or_none(user_name=form_data.username)
    if not user or not verify_password(form_data.password, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.user_name, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}