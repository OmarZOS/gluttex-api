# routers/service_router.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from core.exception_handler import APIException
from core.messages import HTTP_404_NOT_FOUND, SERVICE_NOT_FOUND
from core.api_models import ProvidedService_API, ServiceResourceRequirement_API, ServiceStaffRequirement_API
from services.service_service import ServiceService

service_router = APIRouter()

def get_service_service() -> ServiceService:
    return ServiceService()

@service_router.get("/")
def get_services(
    category_id: int = Query(0, description="Filter by category ID"),
    provider_id: int = Query(0, description="Filter by provider ID"),
    active_only: bool = Query(False, description="Show only active services"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service_service: ServiceService = Depends(get_service_service)
):
    """Get services with filters"""
    if active_only:
        return service_service.get_active_services(provider_id if provider_id > 0 else None)
    elif category_id > 0:
        return service_service.get_services_by_category(category_id, offset, limit)
    elif provider_id > 0:
        return service_service.get_services_by_provider(provider_id, offset, limit)
    else:
        # Return all services (paginated)
        return service_service.get_services_by_provider(0, offset, limit)

@service_router.get("/{service_id}")
def get_service(
    service_id: int,
    service_service: ServiceService = Depends(get_service_service)
):
    """Get service by ID"""
    return service_service.get_service_by_id(service_id)

@service_router.post("/")
def create_service(
    service: ProvidedService_API,
    requirements: List[ServiceResourceRequirement_API],
    staff_requirements: List[ServiceStaffRequirement_API],
    service_service: ServiceService = Depends(get_service_service)
):
    """Create a new service"""
    return service_service.create_service(service, requirements, staff_requirements)

@service_router.put("/{service_id}")
def update_service(
    service_id: int,
    service: ProvidedService_API,
    service_service: ServiceService = Depends(get_service_service)
):
    """Update an existing service"""
    return service_service.update_service(service_id, service)

@service_router.patch("/{service_id}/toggle")
def toggle_service(
    service_id: int,
    is_active: bool,
    service_service: ServiceService = Depends(get_service_service)
):
    """Activate or deactivate a service"""
    return service_service.toggle_service_status(service_id, is_active)

@service_router.delete("/{service_id}")
def delete_service(
    service_id: int,
    service_service: ServiceService = Depends(get_service_service)
):
    """Delete a service"""
    success = service_service.delete_service(service_id)
    if not success:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=SERVICE_NOT_FOUND,
            details=f"Service #{service_id} not found"
        )
    return {"message": f"Service #{service_id} deleted successfully"}