"""
SQLAlchemy Models for Auth Service
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Numeric,
    ForeignKey, Enum as SQLEnum, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class ThemePreference(str, enum.Enum):
    RETRO_EARTH = "RETRO_EARTH"
    MODERN_CLEAN = "MODERN_CLEAN"
    SPACE_FUTURE = "SPACE_FUTURE"


# System Tables
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    theme_preference = Column(SQLEnum(ThemePreference), default=ThemePreference.RETRO_EARTH)
    language = Column(String(5), default="en")  # 'en' or 'th'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)


class LicensePackage(Base):
    __tablename__ = "license_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    package_code = Column(String(50), unique=True, nullable=False)
    package_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LicenseActivation(Base):
    __tablename__ = "license_activations"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("license_packages.id"), nullable=False)
    license_key = Column(String(100), unique=True, nullable=False)
    activated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    activated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    max_users = Column(Integer, default=5)
    
    package = relationship("LicensePackage")
    user = relationship("User")


class AppMarketplace(Base):
    __tablename__ = "app_marketplace"
    
    id = Column(Integer, primary_key=True, index=True)
    app_code = Column(String(50), unique=True, nullable=False)
    app_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    required_package = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    category = Column(String(50), nullable=True)


class AppDependency(Base):
    __tablename__ = "app_dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("app_marketplace.id"), nullable=False)
    required_app_id = Column(Integer, ForeignKey("app_marketplace.id"), nullable=False)
    
    app = relationship("AppMarketplace", foreign_keys=[app_id])
    required_app = relationship("AppMarketplace", foreign_keys=[required_app_id])


class AppActivation(Base):
    __tablename__ = "app_activations"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("app_marketplace.id"), nullable=False)
    license_key = Column(String(100), unique=True, nullable=False)
    activated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    activated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    app = relationship("AppMarketplace")
    user = relationship("User")
