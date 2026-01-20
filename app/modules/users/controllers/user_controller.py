from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import require_admin
from app.core.dependencies import get_db
from app.modules.users.schemas.user_schemas import (
    UserCreateRequest,
    UserResponse,UserUpdateRequest
)
from app.modules.users.services.user_service import UserService
from uuid import UUID

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("",response_model=UserResponse,status_code=status.HTTP_201_CREATED,
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

@router.get("", response_model=list[UserResponse],status_code=status.HTTP_200_OK)
async def list_users(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    return await UserService.list_users(db)


@router.get("/{user_id}", response_model=UserResponse,status_code=status.HTTP_200_OK)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    return await UserService.get_user(db, user_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    return await UserService.create_user(
        db=db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    payload: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    return await UserService.update_user(
        db=db,
        user_id=user_id,
        name=payload.name,
        role=payload.role,
        is_active=payload.is_active,
    )


@router.delete("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    return await UserService.deactivate_user(db, user_id)

