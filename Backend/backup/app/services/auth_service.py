"""
Authentication service for user management and JWT operations
"""
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
import logging

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    track_login_attempt,
    is_account_locked,
    validate_password_strength
)
from app.core.exceptions import AuthenticationError, NotFoundError, ConflictError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication operations"""

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password

        Args:
            db: Database session
            username: Username
            password: Plain text password

        Returns:
            User: Authenticated user or None
        """
        # Check if account is locked first
        if is_account_locked(username):
            logger.warning(f"Authentication failed: Account '{username}' is locked due to too many failed attempts")
            raise AuthenticationError("Account is temporarily locked due to too many failed login attempts. Please try again later.")

        user = db.query(User).filter(User.username == username).first()

        if not user:
            logger.warning(f"Authentication failed: User '{username}' not found")
            # Track failed attempt even for non-existent users to prevent enumeration
            track_login_attempt(username, success=False)
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: User '{username}' is inactive")
            track_login_attempt(username, success=False)
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for user '{username}'")
            # Track failed login attempt
            track_login_attempt(username, success=False)
            return None

        logger.info(f"User '{username}' authenticated successfully")
        # Track successful login attempt (clears failed attempts)
        track_login_attempt(username, success=True)
        return user

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """
        Create a new user

        Args:
            db: Database session
            user_create: User creation data

        Returns:
            User: Created user

        Raises:
            ConflictError: If username or email already exists
        """
        # Check if username exists
        if db.query(User).filter(User.username == user_create.username).first():
            raise ConflictError(f"Username '{user_create.username}' already exists")

        # Check if email exists
        if db.query(User).filter(User.email == user_create.email).first():
            raise ConflictError(f"Email '{user_create.email}' already exists")

        # Validate password strength
        password_validation = validate_password_strength(user_create.password)
        if not password_validation["is_valid"]:
            raise ConflictError(f"Password does not meet security requirements: {', '.join(password_validation['errors'])}")

        # Create user
        hashed_password = get_password_hash(user_create.password)
        user = User(
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            role=user_create.role,
            is_active=user_create.is_active,
            hashed_password=hashed_password
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"User created: {user.username} ({user.email})")
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User: User or None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username

        Args:
            db: Database session
            username: Username

        Returns:
            User: User or None
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        """
        Get list of users with pagination

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[User]: List of users
        """
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """
        Update user information

        Args:
            db: Database session
            user_id: User ID to update
            user_update: Update data

        Returns:
            User: Updated user

        Raises:
            NotFoundError: If user not found
            ConflictError: If email already exists
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        # Check email uniqueness if being updated
        if user_update.email and user_update.email != user.email:
            existing_user = db.query(User).filter(User.email == user_update.email).first()
            if existing_user:
                raise ConflictError(f"Email '{user_update.email}' already exists")

        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        logger.info(f"User updated: {user.username}")
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Delete user by ID

        Args:
            db: Database session
            user_id: User ID to delete

        Returns:
            bool: True if deleted, False if not found

        Raises:
            NotFoundError: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        db.delete(user)
        db.commit()

        logger.info(f"User deleted: {user.username}")
        return True

    @staticmethod
    def login_user(db: Session, username: str, password: str, totp_code: Optional[str] = None) -> dict:
        """
        Login user and return token

        Args:
            db: Database session
            username: Username
            password: Password
            totp_code: Optional 2FA code

        Returns:
            dict: Token data

        Raises:
            AuthenticationError: If authentication fails
        """
        user = AuthService.authenticate_user(db, username, password)
        if not user:
            raise AuthenticationError("Incorrect username or password")

        # Check 2FA if enabled
        if user.two_fa_enabled:
            if not totp_code:
                raise AuthenticationError("2FA code is required")

            # Import here to avoid circular imports
            from app.services.two_fa_service import TwoFAService
            two_fa_service = TwoFAService()

            if not two_fa_service.verify_totp_code(user.two_fa_secret, totp_code):
                logger.warning(f"2FA verification failed for user '{username}'")
                raise AuthenticationError("Invalid 2FA code")

            logger.info(f"2FA verification successful for user '{username}'")

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }