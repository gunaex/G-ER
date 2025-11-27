@echo off
REM RetroEarthERP - Docker Quick Start Script for Windows
REM This script sets up and starts the entire ERP system using Docker

echo ========================================
echo  RetroEarthERP Docker Deployment
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [OK] Docker is installed
echo.

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not available
    echo Please install Docker Compose or update Docker Desktop
    pause
    exit /b 1
)

echo [OK] Docker Compose is available
echo.

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found
    echo Creating .env from template...
    if exist env.production.example (
        copy env.production.example .env >nul
        echo [OK] Created .env file
        echo.
        echo IMPORTANT: Edit .env file and update:
        echo   - POSTGRES_PASSWORD
        echo   - SECRET_KEY
        echo   - CORS_ORIGINS
        echo.
        pause
    ) else (
        echo [ERROR] env.production.example not found
        pause
        exit /b 1
    )
)

echo ========================================
echo  Starting Docker Containers
echo ========================================
echo.

echo Step 1: Building containers...
docker-compose build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build containers
    pause
    exit /b 1
)

echo [OK] Containers built successfully
echo.

echo Step 2: Starting services...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)

echo [OK] Services started
echo.

echo Step 3: Waiting for database to be ready...
timeout /t 10 /nobreak >nul

echo Step 4: Initializing database...
docker-compose exec backend python seed_data.py
if %errorlevel% neq 0 (
    echo [WARNING] Database initialization may have failed
    echo Check if database already has data
)

echo.
echo ========================================
echo  Deployment Complete!
echo ========================================
echo.
echo Your ERP system is now running:
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000/docs
echo   Database:  localhost:5432
echo.
echo Login credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo To view logs:     docker-compose logs -f
echo To stop:          docker-compose down
echo To restart:       docker-compose restart
echo.

pause

