# Microservices Architecture

This directory contains the microservices for the RetroEarthERP application.

## Services

- **auth**: User authentication and management.
- **inventory**: Warehouse management, items, and inventory tracking.
- **production**: Manufacturing planning, BOM, work orders, and machines.
- **sales**: Customer management and sales orders.
- **finance**: Accounting, chart of accounts, and tax.
- **gateway**: API Gateway to route requests to the appropriate service.

## Migration Plan

1.  **Extract Code**: Move relevant models, routers, and logic from the monolithic `backend` to each service.
2.  **Database**: Each service should ideally have its own database or schema.
3.  **Docker**: Update `docker-compose.yml` to run each service as a separate container.
4.  **Communication**: Implement inter-service communication (HTTP/REST or Message Queue).

## Current Status

- **Auth Service**: Implemented. Handles authentication and user management. Running on port 8001 (internal).
- **Gateway**: Implemented. Routes requests to Auth Service or Legacy Backend. Running on port 8000.
- **Legacy Backend**: Renamed from `backend`. Handles all other requests. Running on port 8002 (internal).

## Next Steps

- Migrate **Inventory** service.
- Migrate **Production** service.
- Migrate **Sales** service.
- Migrate **Finance** service.

