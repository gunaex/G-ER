# 🐳 Docker Deployment Guide - RetroEarthERP

Complete guide for deploying RetroEarthERP using Docker containers.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Production Deployment](#production-deployment)
4. [Scaling for 20+ Users](#scaling-for-20-users)
5. [Database Management](#database-management)
6. [Monitoring & Logs](#monitoring--logs)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### Required Software

- **Docker**: 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: 2.0+ (usually included with Docker Desktop)

### Verify Installation

```bash
docker --version
# Docker version 24.0.0 or higher

docker-compose --version
# Docker Compose version v2.20.0 or higher
```

---

## 🚀 Quick Start (Development)

### Step 1: Clone Repository

```bash
cd D:\git\G-ERP-New\RetroEarthERP
```

### Step 2: Start All Services

```bash
# Build and start all containers
docker-compose up -d

# Check status
docker-compose ps
```

**Expected Output:**
```
NAME                   STATUS         PORTS
retroerp-postgres      Up (healthy)   5432
retroerp-backend       Up (healthy)   8000
retroerp-frontend      Up             80->3000
```

### Step 3: Initialize Database

```bash
# Run database migrations and seed data
docker-compose exec backend python seed_data.py
```

### Step 4: Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### Step 5: Login

```
Username: admin
Password: admin123
```

---

## 🏭 Production Deployment

### Step 1: Configure Environment

```bash
# Copy environment template
cp env.production.example .env

# Edit with your production values
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

**CRITICAL: Update these values:**

```env
POSTGRES_PASSWORD=your_secure_password_here
SECRET_KEY=generate-with-openssl-rand-hex-32
CORS_ORIGINS=https://yourdomain.com
```

**Generate Secure SECRET_KEY:**

```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
[System.Web.Security.Membership]::GeneratePassword(32,5)
```

### Step 2: Build for Production

```bash
# Build containers with production optimizations
docker-compose build --no-cache

# Verify images
docker images | grep retroerp
```

### Step 3: Deploy

```bash
# Start in detached mode
docker-compose up -d

# Wait for health checks
docker-compose ps

# Initialize database
docker-compose exec backend python seed_data.py
```

### Step 4: Verify Deployment

```bash
# Check all services are healthy
docker-compose ps

# Test backend health
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:3000/health
```

---

## 📈 Scaling for 20+ Users

### Current Capacity

| Setup | Max Users | Configuration |
|-------|-----------|---------------|
| Single Backend | 5-10 | Default `docker-compose up` |
| 2x Backend | 10-15 | `--scale backend=2` |
| 3x Backend | 15-25 | `--scale backend=3` |
| 5x Backend | 25-50 | `--scale backend=5` |

### Scale Backend Instances

```bash
# Scale to 3 backend containers
docker-compose up -d --scale backend=3

# Verify scaling
docker-compose ps backend
```

### Add Load Balancer (Recommended for Production)

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Nginx Load Balancer
  nginx-lb:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    networks:
      - erp-network
    restart: unless-stopped
```

### Deploy with Load Balancer

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3
```

---

## 💾 Database Management

### Connect to PostgreSQL

```bash
# Using docker exec
docker-compose exec postgres psql -U erp_user -d retroearperp

# Using external client
psql -h localhost -p 5432 -U erp_user -d retroearperp
```

### Run Database Queries

```bash
# List all tables
docker-compose exec postgres psql -U erp_user -d retroearperp -c "\dt"

# Count users
docker-compose exec postgres psql -U erp_user -d retroearperp -c "SELECT COUNT(*) FROM users;"
```

### Database Backup

```bash
# Manual backup
docker-compose exec postgres pg_dump -U erp_user retroearperp > backup_$(date +%Y%m%d).sql

# Automated daily backup (cron job)
0 2 * * * cd /path/to/erp && docker-compose exec -T postgres pg_dump -U erp_user retroearperp | gzip > /backups/erp_$(date +\%Y\%m\%d).sql.gz
```

### Database Restore

```bash
# Restore from backup
cat backup_20251126.sql | docker-compose exec -T postgres psql -U erp_user -d retroearperp
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 backend

# Save logs to file
docker-compose logs backend > backend_logs.txt
```

### Real-time Monitoring

```bash
# Resource usage
docker stats

# Container health
docker-compose ps
```

### Check Health Status

```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend health
curl http://localhost:3000/health

# Database health
docker-compose exec postgres pg_isready -U erp_user
```

---

## 🔄 Backup & Recovery

### Complete Backup Strategy

```bash
#!/bin/bash
# backup.sh - Complete system backup

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 1. Database backup
docker-compose exec -T postgres pg_dump -U erp_user retroearperp | gzip > "$BACKUP_DIR/database.sql.gz"

# 2. Docker volumes backup
docker run --rm -v retroearperp_postgres_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/volumes.tar.gz /data

# 3. Configuration backup
cp .env "$BACKUP_DIR/"
cp docker-compose.yml "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
```

### Restore Procedure

```bash
# 1. Stop services
docker-compose down

# 2. Restore volumes
docker run --rm -v retroearperp_postgres_data:/data -v /backups/20251126:/backup alpine tar xzf /backup/volumes.tar.gz -C /

# 3. Start services
docker-compose up -d

# 4. Wait for PostgreSQL
sleep 10

# 5. Restore database
zcat /backups/20251126/database.sql.gz | docker-compose exec -T postgres psql -U erp_user -d retroearperp
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### 2. Database Connection Failed

**Error**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### 3. Backend Health Check Fails

**Error**: Container unhealthy

**Solution**:
```bash
# Check backend logs
docker-compose logs backend

# Check if database is ready
docker-compose exec postgres pg_isready

# Restart backend
docker-compose restart backend
```

#### 4. Frontend Can't Connect to Backend

**Error**: API calls fail with 502

**Solution**:
```bash
# Check nginx configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Verify backend is accessible
docker-compose exec frontend wget -O- http://backend:8000/api/health

# Restart frontend
docker-compose restart frontend
```

#### 5. Out of Memory

**Error**: Container keeps restarting

**Solution**:
```bash
# Check memory usage
docker stats

# Increase Docker memory limit in Docker Desktop:
# Settings -> Resources -> Memory -> Set to 4GB+

# Or add memory limits to docker-compose.yml:
services:
  backend:
    mem_limit: 1g
    mem_reservation: 512m
```

---

## 🔐 Security Best Practices

### 1. Change Default Passwords

```bash
# Never use default passwords in production
POSTGRES_PASSWORD=generate-strong-password
SECRET_KEY=use-openssl-rand-hex-32
```

### 2. Use HTTPS (Production)

```yaml
# Add SSL termination
services:
  nginx-ssl:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./ssl/cert.pem:/etc/nginx/ssl/cert.pem
      - ./ssl/key.pem:/etc/nginx/ssl/key.pem
```

### 3. Restrict Network Access

```yaml
# Only expose frontend to public
services:
  backend:
    ports: []  # Remove public port mapping
    expose:
      - "8000"  # Only internal network
```

### 4. Regular Updates

```bash
# Update base images
docker-compose pull

# Rebuild containers
docker-compose build --no-cache

# Deploy updates
docker-compose up -d
```

---

## 📞 Support

### Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **Check health**: `docker-compose ps`
3. **Check documentation**: See PROGRESS.md, IMPLEMENTATION_SUMMARY.md
4. **Database status**: `docker-compose exec postgres pg_isready`

### Useful Commands Cheat Sheet

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend python seed_data.py

# Scale backend
docker-compose up -d --scale backend=3

# Remove all (including volumes)
docker-compose down -v

# Rebuild
docker-compose build --no-cache

# Check resource usage
docker stats
```

---

## ✅ Success Indicators

Your deployment is successful if:

- ✅ All containers show "Up (healthy)" status
- ✅ Frontend accessible at http://localhost:3000
- ✅ Backend API docs at http://localhost:8000/docs
- ✅ Health check returns `{"status":"healthy"}`
- ✅ Can login with admin/admin123
- ✅ Database has 32 tables
- ✅ No errors in logs

---

## 🎉 You're Ready!

Your RetroEarthERP is now running in production-ready containers!

**Next Steps:**
1. Configure domain name and SSL
2. Set up automated backups
3. Configure monitoring (Prometheus/Grafana)
4. Add CI/CD pipeline
5. Document your specific deployment

---

**Deployment Date**: November 26, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready

