from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.dependencies import get_db
from app.shared.exceptions import AuthenticationError
from app.modules.auth.schemas import LoginRequest, LoginResponse
from app.modules.auth.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service() -> AuthService:
    return AuthService()


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    try:
        access_token, token_type, user = await auth_service.login_user(
            db=db,
            email=data.email,
            password=data.password,
        )

        return LoginResponse(
            access_token=access_token,
            token_type=token_type,
            user=user,
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
