"""
Authentication router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from models import User, LicenseActivation, AppActivation
from schemas import LoginRequest, LoginResponse, UserResponse, UserCreate
import auth_utils
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
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = get_utc_now()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    # Get active license package
    active_license = db.query(LicenseActivation).filter(
        LicenseActivation.is_active == True,
        (LicenseActivation.expires_at == None) | (LicenseActivation.expires_at > get_utc_now())
    ).first()
    
    package_info = None
    if active_license:
        package_info = {
            "package_code": active_license.package.package_code,
            "package_name": active_license.package.package_name,
            "expires_at": active_license.expires_at
        }
        
    # Get active apps
    active_apps = db.query(AppActivation).filter(
        AppActivation.is_active == True,
        (AppActivation.expires_at == None) | (AppActivation.expires_at > get_utc_now())
    ).all()
    
    apps_list = []
    for app in active_apps:
        apps_list.append({
            "app_code": app.app.app_code,
            "app_name": app.app.app_name,
            "expires_at": app.expires_at
        })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "server_time_utc": get_utc_now(),
        "active_package": package_info,
        "active_apps": apps_list
    }
