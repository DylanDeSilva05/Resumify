"""
User management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ConflictError
from app.api.deps import get_current_user, get_current_hr_manager
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=dict)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for debugging
):
    """
    Get list of users

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        dict: Users list with pagination info
    """
    users = AuthService.get_users(db, skip=skip, limit=limit)
    total = db.query(User).count()

    # Convert User objects to UserResponse schemas
    users_response = [UserResponse.from_orm(user) for user in users]

    return {
        "users": users_response,
        "total": total,
        "page": (skip // limit) + 1,
        "pages": (total + limit - 1) // limit
    }


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager)
):
    """
    Create a new user

    Args:
        user_create: User creation data
        db: Database session
        current_user: Current HR manager user

    Returns:
        UserResponse: Created user information
    """
    try:
        user = AuthService.create_user(db, user_create)
        return user
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID

    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserResponse: User information
    """
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager)
):
    """
    Update user by ID

    Args:
        user_id: User ID to update
        user_update: Update data
        db: Database session
        current_user: Current HR manager user

    Returns:
        UserResponse: Updated user information
    """
    try:
        user = AuthService.update_user(db, user_id, user_update)
        return user
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager)
):
    """
    Delete user by ID

    Args:
        user_id: User ID to delete
        db: Database session
        current_user: Current HR manager user
    """
    try:
        AuthService.delete_user(db, user_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse: Current user information
    """
    return current_user


@router.get("/debug", response_model=dict)
async def debug_users(db: Session = Depends(get_db)):
    """
    DEBUG ENDPOINT: Get users without authentication (for testing only)

    Returns:
        dict: Debug information about users
    """
    users = AuthService.get_users(db)
    total = db.query(User).count()

    # Convert users to dict format for JSON response
    users_data = []
    for user in users:
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": str(user.role),
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })

    return {
        "debug_mode": True,
        "total_users": total,
        "users": users_data,
        "message": "This endpoint should be removed in production"
    }