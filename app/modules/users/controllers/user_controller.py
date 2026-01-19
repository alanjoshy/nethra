from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import require_admin
from app.core.dependencies import get_db
from app.modules.users.schemas.user_schemas import (
    UserCreateRequest,
    UserResponse,
)
from app.modules.users.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    return await UserService.create_user(
        db=db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )
