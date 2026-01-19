from fastapi import Depends, HTTPException, status
from app.modules.users.entities.user_entity import User
from app.core.dependencies import get_current_user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
