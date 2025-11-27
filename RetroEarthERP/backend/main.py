"""
RetroEarthERP - Main FastAPI Application
Multi-language ERP platform with Windows 3.11 retro UI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from database import engine, Base
from routers import auth, items, partners, warehouses, inventory, wms, planning, qms, users, bom, workorder, machines, sales, accounting

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="RetroEarthERP API",
    description="Manufacturing ERP with retro Windows 3.11 interface",
    version="1.0.0"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["User Management"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(partners.router, prefix="/api/partners", tags=["Partners"])
app.include_router(warehouses.router, prefix="/api/warehouses", tags=["Warehouses"])
app.include_router(inventory.router)
app.include_router(wms.router)
app.include_router(planning.router)
app.include_router(qms.router)
app.include_router(bom.router, prefix="/api/bom", tags=["Bill of Materials"])
app.include_router(workorder.router, prefix="/api/workorders", tags=["Work Orders"])
app.include_router(machines.router)
app.include_router(sales.router)
app.include_router(accounting.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to RetroEarthERP API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
