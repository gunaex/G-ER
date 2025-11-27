"""
Authentication router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from models import User, LicenseActivation, AppActivation
from schemas import LoginRequest, LoginResponse, UserResponse, UserCreate
import auth as auth_utils
from utils.datetime_utils import get_utc_now

router = APIRouter()

# Alias for consistency with other routers
get_current_user = auth_utils.get_current_user
get_current_active_user = auth_utils.get_current_user
verify_password = auth_utils.verify_password
get_password_hash = auth_utils.get_password_hash
create_access_token = auth_utils.create_access_token


def get_current_active_admin(current_user: User = Depends(get_current_user)):
    """Verify current user is an admin"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin or Manager role required."
        )
    return current_user


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login endpoint
    Returns JWT token and user info with active package/apps
    """
    # Find user
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Update last login (UTC with timezone info)
    user.last_login = get_utc_now()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    # Get active package
    active_license = db.query(LicenseActivation).filter(
        LicenseActivation.is_active == True
    ).first()
    
    active_package = None
    if active_license:
        active_package = {
            "package_code": active_license.package.package_code,
            "package_name": active_license.package.package_name
        }
    
    # Get active apps
    active_apps = db.query(AppActivation).filter(
        AppActivation.is_active == True
    ).all()
    
    apps_list = [
        {
            "app_code": app.app.app_code,
            "app_name": app.app.app_name
        }
        for app in active_apps
    ]
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "active_package": active_package,
        "active_apps": apps_list,
        "server_time_utc": get_utc_now()  # Server time in UTC for client sync
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.patch("/me/theme")
def update_theme(
    theme: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user theme preference"""
    valid_themes = ["RETRO_EARTH", "MODERN_CLEAN", "SPACE_FUTURE"]
    if theme not in valid_themes:
        raise HTTPException(status_code=400, detail="Invalid theme")
    
    current_user.theme_preference = theme
    db.commit()
    
    return {"message": "Theme updated successfully", "theme": theme}


@router.patch("/me/language")
def update_language(
    language: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user language preference"""
    valid_languages = ["en", "th"]
    if language not in valid_languages:
        raise HTTPException(status_code=400, detail="Invalid language")
    
    current_user.language = language
    db.commit()
    
    return {"message": "Language updated successfully", "language": language}
