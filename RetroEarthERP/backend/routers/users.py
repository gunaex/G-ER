"""
User Management Router - Full CRUD operations for User Master
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
import models
import schemas
import auth as auth_utils

router = APIRouter()

# Dependency for admin-only operations
def get_current_admin(
    current_user: models.User = Depends(auth_utils.get_current_user)
) -> models.User:
    """Require admin role for user management operations"""
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage users"
        )
    return current_user


# ==================== LIST USERS ====================
@router.get("/", response_model=List[schemas.UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """
    List all users with optional filtering
    - **is_active**: Filter by active status
    - **role**: Filter by role (admin, manager, user)
    - **search**: Search by username, email, or full_name
    """
    query = db.query(models.User)
    
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    
    if role:
        try:
            role_enum = models.UserRole(role.lower())
            query = query.filter(models.User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}. Must be admin, manager, or user"
            )
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.User.username.ilike(search_pattern)) |
            (models.User.email.ilike(search_pattern)) |
            (models.User.full_name.ilike(search_pattern))
        )
    
    users = query.order_by(models.User.id).offset(skip).limit(limit).all()
    return users


# ==================== USER STATISTICS ====================
@router.get("/stats/summary", response_model=dict)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """Get user statistics summary (Admin only)"""
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    inactive_users = total_users - active_users
    
    admin_count = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).count()
    manager_count = db.query(models.User).filter(models.User.role == models.UserRole.MANAGER).count()
    user_count = db.query(models.User).filter(models.User.role == models.UserRole.USER).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "by_role": {
            "admin": admin_count,
            "manager": manager_count,
            "user": user_count
        }
    }


# ==================== GET USER BY ID ====================
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """Get a specific user by ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


# ==================== CREATE USER ====================
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """
    Create a new user (Admin only)
    - **username**: Unique username (required)
    - **email**: Unique email address (required)
    - **password**: Password (required, min 6 characters)
    - **full_name**: Full name (required)
    - **role**: Role (admin, manager, user) - default: user
    """
    # Check if username already exists
    existing_user = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_data.email}' already exists"
        )
    
    # Validate password length
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Validate role
    try:
        role_enum = models.UserRole(user_data.role.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {user_data.role}. Must be admin, manager, or user"
        )
    
    # Create user
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password_hash=auth_utils.get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=role_enum,
        theme_preference=models.ThemePreference.RETRO_EARTH,
        language="en",
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ==================== UPDATE USER ====================
@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """
    Update an existing user (Admin only)
    - Only provided fields will be updated
    - Cannot change your own role or deactivate yourself
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Prevent self-deactivation
    if user_id == current_user.id:
        if user_data.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account"
            )
        if user_data.role and user_data.role.lower() != current_user.role.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot change your own role"
            )
    
    # Check username uniqueness if being updated
    if user_data.username and user_data.username != db_user.username:
        existing = db.query(models.User).filter(
            models.User.username == user_data.username,
            models.User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{user_data.username}' already exists"
            )
        db_user.username = user_data.username
    
    # Check email uniqueness if being updated
    if user_data.email and user_data.email != db_user.email:
        existing = db.query(models.User).filter(
            models.User.email == user_data.email,
            models.User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_data.email}' already exists"
            )
        db_user.email = user_data.email
    
    # Update other fields
    if user_data.full_name:
        db_user.full_name = user_data.full_name
    
    if user_data.role:
        try:
            db_user.role = models.UserRole(user_data.role.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {user_data.role}"
            )
    
    if user_data.theme_preference:
        try:
            db_user.theme_preference = models.ThemePreference(user_data.theme_preference)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid theme: {user_data.theme_preference}"
            )
    
    if user_data.language:
        if user_data.language not in ["en", "th"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language must be 'en' or 'th'"
            )
        db_user.language = user_data.language
    
    if user_data.is_active is not None:
        db_user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ==================== CHANGE PASSWORD ====================
@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
def change_password(
    user_id: int,
    password_data: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """
    Change a user's password (Admin only)
    - **new_password**: New password (min 6 characters)
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    db_user.password_hash = auth_utils.get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": f"Password changed successfully for user '{db_user.username}'"}


# ==================== DELETE USER ====================
@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """
    Delete a user (Admin only)
    - Cannot delete your own account
    - Consider deactivating instead of deleting to preserve audit trail
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    username = db_user.username
    db.delete(db_user)
    db.commit()
    
    return {"message": f"User '{username}' deleted successfully"}


# ==================== TOGGLE USER STATUS ====================
@router.post("/{user_id}/toggle-status", response_model=schemas.UserResponse)
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """
    Toggle user active/inactive status (Admin only)
    - Cannot toggle your own status
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot toggle your own status"
        )
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    db_user.is_active = not db_user.is_active
    db.commit()
    db.refresh(db_user)
    
    status_text = "activated" if db_user.is_active else "deactivated"
    return db_user



