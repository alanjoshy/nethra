from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.security import verify_password, create_access_token
from app.shared.exceptions import AuthenticationError
from app.shared.constants import Auth
from app.modules.auth.repositories.auth_user_repository import AuthUserRepository


class AuthService:
    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ):
        user = await AuthUserRepository.get_active_user_by_email(db, email)

        if not user:
            raise AuthenticationError(
                message="Invalid email or password",
                details={"reason": "user_not_found_or_inactive"},
            )

        if not verify_password(password, user.password_hash):
            raise AuthenticationError(
                message="Invalid email or password",
                details={"reason": "invalid_password"},
            )

        return user

    def generate_auth_token(self, user):
        token = create_access_token(
            user_id=str(user.id),
            role=user.role,
        )

        return {
            "access_token": token,
            "token_type": Auth.TOKEN_TYPE,
        }

    async def login_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ):
        user = await self.authenticate_user(db, email, password)
        token_data = self.generate_auth_token(user)

        return token_data["access_token"], token_data["token_type"], user
