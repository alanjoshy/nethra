"""
Authentication controller - Transport layer (API endpoints).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.dependencies import get_db
from app.shared.exceptions import AuthenticationError
from app.modules.auth.schemas import LoginRequest, LoginResponse, UserResponse
from app.modules.auth.services.auth_service import AuthService
from app.modules.users.repositories.user_repository import UserRepository


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service() -> AuthService:
    """
    Dependency to get AuthService instance.
    """
    user_repository = UserRepository()
    return AuthService(user_repository=user_repository)


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """
    Login endpoint.
    
    Authenticates user and returns access token.
    """
    try:
        # Use service layer for authentication
        access_token, token_type, user = await auth_service.login_user(
            db=db,
            email=data.email,
            password=data.password
        )
        
        # Build response
        return LoginResponse(
            access_token=access_token,
            token_type=token_type,
            user=UserResponse(
                id=str(user.id),
                name=user.name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at.isoformat()
            )
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
