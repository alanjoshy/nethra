"""
Authentication service - Business logic for authentication.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.security import verify_password, create_access_token
from app.shared.exceptions import AuthenticationError
from app.shared.constants import Auth
from app.modules.users.repositories.user_repository import UserRepository


class AuthService:
    """
    Authentication service.
    Handles user authentication and token generation.
    """
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ):
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
        
        Returns:
            Authenticated User object
        
        Raises:
            AuthenticationError: If credentials are invalid or user is inactive
        """
        # Fetch active user by email
        user = await self._user_repository.get_active_user_by_email(db, email)
        
        if not user:
            raise AuthenticationError(
                message="Invalid email or password",
                details={"reason": "user_not_found_or_inactive"}
            )
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthenticationError(
                message="Invalid email or password",
                details={"reason": "invalid_password"}
            )
        
        return user
    
    def generate_auth_token(self, user):
        """
        Generate authentication token for a user.
        
        Args:
            user: User object
        
        Returns:
            Dictionary with access_token and token_type
        """
        token = create_access_token(str(user.id), user.role)
        
        return {
            "access_token": token,
            "token_type": Auth.TOKEN_TYPE
        }
    
    async def login_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ):
        """
        Complete login flow: authenticate and generate token.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
        
        Returns:
            Tuple of (access_token, token_type, user)
        
        Raises:
            AuthenticationError: If authentication fails
        """
        # Authenticate user
        user = await self.authenticate_user(db, email, password)
        
        # Generate token
        token_data = self.generate_auth_token(user)
        
        return token_data["access_token"], token_data["token_type"], user
