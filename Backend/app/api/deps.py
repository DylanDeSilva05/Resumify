"""
API dependencies for authentication, authorization, and database access
"""
from typing import Generator, Optional, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError
from app.core.permissions import Permission, PermissionChecker
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.services.security_service import SecurityService

# Security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user

    Args:
        credentials: HTTP bearer token credentials
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = AuthService.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user

    Args:
        current_user: Current user from token

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# Role-based access dependencies

def get_super_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user if they are Super Admin (platform owner)"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required"
        )
    return current_user


def get_company_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user if they are Company Admin or higher"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company Admin access or higher required"
        )
    return current_user


def get_company_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user if they are Company User or higher"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN, UserRole.COMPANY_USER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company User access or higher required"
        )
    return current_user


def get_recruiter_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user if they have any company role (any authenticated user)"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN, UserRole.COMPANY_USER, UserRole.RECRUITER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company access required"
        )
    return current_user


def require_permission(permission: Permission) -> Callable:
    """
    Dependency factory for permission-based access control

    Args:
        permission: Required permission

    Returns:
        Dependency function that checks permission
    """
    def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        PermissionChecker.require_permission(current_user.role, permission)
        return current_user

    return permission_dependency


def require_any_permission(permissions: List[Permission]) -> Callable:
    """
    Dependency factory for any-permission access control

    Args:
        permissions: List of permissions (user needs any one)

    Returns:
        Dependency function that checks permissions
    """
    def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        PermissionChecker.require_any_permission(current_user.role, permissions)
        return current_user

    return permission_dependency


def require_all_permissions(permissions: List[Permission]) -> Callable:
    """
    Dependency factory for all-permissions access control

    Args:
        permissions: List of permissions (user needs all)

    Returns:
        Dependency function that checks permissions
    """
    def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        PermissionChecker.require_all_permissions(current_user.role, permissions)
        return current_user

    return permission_dependency


# Legacy compatibility (deprecated - for backward compatibility only)
def get_current_hr_manager(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    DEPRECATED: Use get_company_admin_user instead
    Get current user if they are Company Admin or higher
    """
    return get_company_admin_user(current_user)


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise

    Args:
        credentials: Optional HTTP bearer token credentials
        db: Database session

    Returns:
        Optional[User]: Current user or None
    """
    if not credentials:
        return None

    try:
        user_id = verify_token(credentials.credentials)
        if user_id:
            user = AuthService.get_user_by_id(db, int(user_id))
            if user and user.is_active:
                return user
    except Exception:
        pass

    return None