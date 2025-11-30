"""
API Gateway
Routes requests to appropriate microservices
"""
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RetroEarthERP API Gateway",
    description="Gateway for RetroEarthERP Microservices",
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

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8001")
# For now, route everything else to the legacy backend or other services as they are built
LEGACY_BACKEND_URL = os.getenv("LEGACY_BACKEND_URL", "http://backend:8000")

async def proxy_request(url: str, request: Request):
    async with httpx.AsyncClient() as client:
        try:
            # Forward headers, excluding host
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("content-length", None) # Let httpx handle content-length
            
            content = await request.body()
            
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=content,
                params=request.query_params,
                timeout=60.0
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.RequestError as exc:
            return Response(
                content=f"Service unavailable: {str(exc)}",
                status_code=503
            )

@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def auth_proxy(path: str, request: Request):
    url = f"{AUTH_SERVICE_URL}/api/auth/{path}"
    return await proxy_request(url, request)

@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def users_proxy(path: str, request: Request):
    url = f"{AUTH_SERVICE_URL}/api/users/{path}"
    return await proxy_request(url, request)

# Catch-all for other routes (to be migrated)
# In a real migration, you might route specific paths to specific services
# and default to the legacy backend.
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def default_proxy(path: str, request: Request):
    # Avoid infinite loop if this matches the above routes (it shouldn't due to order, but good to be safe)
    if path.startswith("api/auth") or path.startswith("api/users"):
        # This should have been caught by specific routes, but just in case
        if path.startswith("api/auth"):
             url = f"{AUTH_SERVICE_URL}/{path}"
        else:
             url = f"{AUTH_SERVICE_URL}/{path}"
    else:
        url = f"{LEGACY_BACKEND_URL}/{path}"
        
    return await proxy_request(url, request)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "gateway"}
