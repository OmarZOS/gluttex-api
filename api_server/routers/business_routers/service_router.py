# routers/business_routers/service_router.py
"""
Service router for managing provided services, requirements, and staff assignments.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
import logging

from core.api_models import (
    ProvidedService_API, 
    ServiceResourceRequirement_API, 
    ServiceStaffRequirement_API
)
from core.exceptions.specific.service_exceptions import (
    ServiceException,
    ServiceNotFoundException,
    ServiceCreationFailedException,
    ServiceUpdateFailedException,
    ServiceDeleteFailedException,
    ServiceCategoryNotFoundException,
    ServiceProviderNotFoundException,
    ServiceToggleStatusException,
    ServiceRequirementCreationException
)
from services.service_service import ServiceService

logger = logging.getLogger(__name__)

# Create router with tags and prefix
service_router = APIRouter(
    # tags=["business-services"],
    # prefix="/business"
)


def get_service_service() -> ServiceService:
    """Dependency to get ServiceService instance"""
    return ServiceService()


# ==================== Service Listing Endpoints ====================

@service_router.get(
    "/services",
    summary="Get services with filters",
    description="Retrieve services filtered by category, provider, or active status"
)
def get_services(
    category_id: int = Query(0, description="Filter by category ID"),
    provider_id: int = Query(0, description="Filter by provider ID"),
    active_only: bool = Query(False, description="Show only active services"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Get services with various filters.
    
    Args:
        category_id: Filter by service category ID
        provider_id: Filter by provider ID
        active_only: Show only active services
        offset: Pagination offset
        limit: Maximum number of records
        service_service: Injected service service
        
    Returns:
        List of services matching the filters
    """
    logger.info(f"Fetching services with filters - category:{category_id}, provider:{provider_id}, active_only:{active_only}")
    
    try:
        if active_only:
            result = service_service.get_active_services(provider_id if provider_id > 0 else None)
            filter_description = "active services"
            if provider_id > 0:
                filter_description += f" for provider {provider_id}"
        
        elif category_id > 0:
            result = service_service.get_services_by_category(category_id, offset, limit)
            filter_description = f"category {category_id}"
        
        elif provider_id > 0:
            result = service_service.get_services_by_provider(provider_id, offset, limit)
            filter_description = f"provider {provider_id}"
        
        else:
            # Return all services (paginated)
            result = service_service.get_services_by_provider(0, offset, limit)
            filter_description = "all services"
        
        logger.info(f"Found {len(result)} {filter_description}")
        
        return {
            "success": True,
            "data": result,
            "filters": {
                "category_id": category_id if category_id > 0 else None,
                "provider_id": provider_id if provider_id > 0 else None,
                "active_only": active_only
            },
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": len(result)
            }
        }
        
    except (ServiceCategoryNotFoundException, ServiceProviderNotFoundException) as e:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch services: {e}")
        raise ServiceException(
            message="Failed to retrieve services",
            details={"error": str(e)}
        )


# ==================== Single Service Operations ====================

@service_router.get(
    "/services/{service_id}",
    summary="Get service by ID",
    description="Retrieve a specific service by its ID"
)
def get_service(
    service_id: int,
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Get service by ID.
    
    Args:
        service_id: Service ID to fetch
        service_service: Injected service service
        
    Returns:
        Service object if found
    """
    logger.info(f"Fetching service with ID: {service_id}")
    
    try:
        service = service_service.get_service_by_id(service_id)
        
        if not service:
            logger.warning(f"Service with ID {service_id} not found")
            raise ServiceNotFoundException(service_id=service_id)
        
        logger.info(f"Successfully retrieved service {service_id}")
        return {
            "success": True,
            "data": service,
            "service_id": service_id
        }
        
    except ServiceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch service {service_id}: {e}")
        raise ServiceNotFoundException(
            service_id=service_id,
            details={"error": str(e)}
        )


@service_router.post(
    "/services",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service",
    description="Creates a new service with resource and staff requirements"
)
def create_service(
    service: ProvidedService_API,
    requirements: List[ServiceResourceRequirement_API],
    staff_requirements: List[ServiceStaffRequirement_API],
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Create a new service.
    
    Args:
        service: Service details
        requirements: Resource requirements for the service
        staff_requirements: Staff requirements for the service
        service_service: Injected service service
        
    Returns:
        Created service object
    """
    logger.info(f"Creating new service: {service.provided_service_name}")
    
    # Validate service has required fields
    if not service.provided_service_name:
        raise ServiceCreationFailedException(
            error="Service name is required",
            service_name=service.provided_service_name,
            provider_id=service.provided_service_product_provider_id
        )
    
    try:
        created_service = service_service.create_service(
            service, requirements, staff_requirements
        )
        
        logger.info(f"Service created successfully with ID: {getattr(created_service, 'provided_service_id', 'unknown')}")
        
        return {
            "success": True,
            "message": "Service created successfully",
            "data": created_service,
            "summary": {
                "service_name": service.provided_service_name,
                "requirements_count": len(requirements),
                "staff_requirements_count": len(staff_requirements),
                "is_active": service.provided_service_is_active
            }
        }
        
    except (ServiceCreationFailedException, ServiceRequirementCreationException) as e:
        raise
    except Exception as e:
        logger.error(f"Failed to create service: {e}")
        raise ServiceCreationFailedException(
            error=str(e),
            service_name=service.provided_service_name,
            provider_id=service.provided_service_product_provider_id
        )


@service_router.put(
    "/services/{service_id}",
    summary="Update a service",
    description="Update an existing service's details"
)
def update_service(
    service_id: int,
    service: ProvidedService_API,
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Update an existing service.
    
    Args:
        service_id: Service ID to update
        service: Updated service details
        service_service: Injected service service
        
    Returns:
        Updated service object
    """
    logger.info(f"Updating service with ID: {service_id}")
    
    try:
        # Check if service exists
        existing_service = service_service.get_service_by_id(service_id)
        if not existing_service:
            raise ServiceNotFoundException(service_id=service_id)
        
        # Set the service ID
        if hasattr(service, 'provided_service_id'):
            service.provided_service_id = service_id
        
        updated_service = service_service.update_service(service_id, service)
        
        logger.info(f"Service {service_id} updated successfully")
        return {
            "success": True,
            "message": "Service updated successfully",
            "data": updated_service,
            "service_id": service_id,
            "updated_fields": {
                "name_changed": service.provided_service_name != getattr(existing_service, 'provided_service_name', None),
                "price_changed": service.provided_service_base_price != getattr(existing_service, 'provided_service_base_price', None),
                "active_status_changed": service.provided_service_is_active != getattr(existing_service, 'provided_service_is_active', None)
            }
        }
        
    except (ServiceNotFoundException, ServiceUpdateFailedException):
        raise
    except Exception as e:
        logger.error(f"Failed to update service {service_id}: {e}")
        raise ServiceUpdateFailedException(
            service_id=service_id,
            error=str(e),
            fields_attempted=["service_details"]
        )


@service_router.patch(
    "/services/{service_id}/toggle",
    summary="Toggle service status",
    description="Activate or deactivate a service"
)
def toggle_service(
    service_id: int,
    is_active: bool = Query(..., description="True to activate, False to deactivate"),
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Activate or deactivate a service.
    
    Args:
        service_id: Service ID to toggle
        is_active: Desired active status
        service_service: Injected service service
        
    Returns:
        Updated service with new status
    """
    action = "activate" if is_active else "deactivate"
    logger.info(f"Attempting to {action} service {service_id}")
    
    try:
        # Check if service exists
        existing_service = service_service.get_service_by_id(service_id)
        if not existing_service:
            raise ServiceNotFoundException(service_id=service_id)
        
        # Check if already in desired state
        current_status = getattr(existing_service, 'provided_service_is_active', False)
        if current_status == is_active:
            logger.info(f"Service {service_id} is already {'active' if is_active else 'inactive'}")
            raise ServiceToggleStatusException(
                service_id=service_id,
                current_status=current_status,
                requested_status=is_active,
                error="Service already in requested state"
            )
        
        # Toggle status
        updated_service = service_service.toggle_service_status(service_id, is_active)
        
        logger.info(f"Service {service_id} {action}d successfully")
        return {
            "success": True,
            "message": f"Service {action}d successfully",
            "data": updated_service,
            "service_id": service_id,
            "is_active": is_active,
            "previous_status": current_status
        }
        
    except (ServiceNotFoundException, ServiceToggleStatusException, ServiceUpdateFailedException):
        raise
    except Exception as e:
        logger.error(f"Failed to toggle service {service_id} status: {e}")
        raise ServiceToggleStatusException(
            service_id=service_id,
            requested_status=is_active,
            error=str(e)
        )


@service_router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a service",
    description="Deletes a service and all its associated requirements"
)
def delete_service(
    service_id: int,
    force_delete: bool = Query(False, description="Force delete even if service has requirements"),
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Delete a service.
    
    Args:
        service_id: Service ID to delete
        force_delete: Whether to force delete even if service has requirements
        service_service: Injected service service
        
    Returns:
        Success message
    """
    logger.info(f"Deleting service with ID: {service_id} (force={force_delete})")
    
    try:
        # Check if service exists
        existing_service = service_service.get_service_by_id(service_id)
        if not existing_service:
            logger.warning(f"Service with ID {service_id} not found")
            raise ServiceNotFoundException(service_id=service_id)
        
        # Check for associated requirements
        has_requirements = hasattr(existing_service, 'requirements') and existing_service.requirements
        has_staff_requirements = hasattr(existing_service, 'staff_requirements') and existing_service.staff_requirements
        
        if (has_requirements or has_staff_requirements) and not force_delete:
            logger.warning(f"Service {service_id} has requirements. Use force_delete=true to delete.")
            return {
                "success": False,
                "message": "Service has associated requirements. Use force_delete=true to delete anyway.",
                "service_id": service_id,
                "has_resource_requirements": bool(has_requirements),
                "has_staff_requirements": bool(has_staff_requirements)
            }
        
        # Delete service
        success = service_service.delete_service(service_id)
        
        if not success:
            raise ServiceDeleteFailedException(
                service_id=service_id,
                error="Service returned False"
            )
        
        logger.info(f"Service {service_id} deleted successfully")
        return {
            "success": True,
            "message": f"Service #{service_id} deleted successfully",
            "service_id": service_id,
            "force_deleted": force_delete,
            "deleted_requirements": {
                "resource_requirements": bool(has_requirements),
                "staff_requirements": bool(has_staff_requirements)
            }
        }
        
    except (ServiceNotFoundException, ServiceDeleteFailedException):
        raise
    except Exception as e:
        logger.error(f"Failed to delete service {service_id}: {e}")
        raise ServiceDeleteFailedException(
            service_id=service_id,
            error=str(e)
        )


# ==================== Additional Service Endpoints ====================

@service_router.get(
    "/services/category/{category_id}",
    summary="Get services by category",
    description="Retrieve all services in a specific category"
)
def get_services_by_category(
    category_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Get all services in a specific category.
    
    Args:
        category_id: Category ID to filter by
        offset: Pagination offset
        limit: Maximum number of records
        service_service: Injected service service
        
    Returns:
        List of services in the category
    """
    logger.info(f"Fetching services for category {category_id}")
    
    try:
        services = service_service.get_services_by_category(category_id, offset, limit)
        
        return {
            "success": True,
            "data": services,
            "category_id": category_id,
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": len(services)
            }
        }
        
    except ServiceCategoryNotFoundException as e:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch services for category {category_id}: {e}")
        raise ServiceCategoryNotFoundException(
            category_id=category_id,
            details={"error": str(e)}
        )


@service_router.get(
    "/services/provider/{provider_id}",
    summary="Get services by provider",
    description="Retrieve all services offered by a specific provider"
)
def get_services_by_provider(
    provider_id: int,
    active_only: bool = Query(False, description="Show only active services"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Get all services offered by a specific provider.
    
    Args:
        provider_id: Provider ID to filter by
        active_only: Show only active services
        offset: Pagination offset
        limit: Maximum number of records
        service_service: Injected service service
        
    Returns:
        List of services from the provider
    """
    logger.info(f"Fetching services for provider {provider_id} (active_only={active_only})")
    
    try:
        if active_only:
            services = service_service.get_active_services(provider_id)
        else:
            services = service_service.get_services_by_provider(provider_id, offset, limit)
        
        return {
            "success": True,
            "data": services,
            "provider_id": provider_id,
            "active_only": active_only,
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": len(services)
            }
        }
        
    except ServiceProviderNotFoundException as e:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch services for provider {provider_id}: {e}")
        raise ServiceProviderNotFoundException(
            provider_id=provider_id,
            details={"error": str(e)}
        )


@service_router.get(
    "/services/{service_id}/requirements",
    summary="Get service requirements",
    description="Retrieve all resource requirements for a service"
)
def get_service_requirements(
    service_id: int,
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Get all resource requirements for a service.
    
    Args:
        service_id: Service ID to fetch requirements for
        service_service: Injected service service
        
    Returns:
        List of resource requirements
    """
    logger.info(f"Fetching requirements for service {service_id}")
    
    try:
        # Check if service exists
        service = service_service.get_service_by_id(service_id)
        if not service:
            raise ServiceNotFoundException(service_id=service_id)
        
        requirements = service_service.get_service_requirements(service_id)
        
        return {
            "success": True,
            "data": requirements,
            "service_id": service_id,
            "service_name": getattr(service, 'provided_service_name', None),
            "total_requirements": len(requirements)
        }
        
    except ServiceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch requirements for service {service_id}: {e}")
        raise ServiceException(
            message="Failed to retrieve service requirements",
            details={"service_id": service_id, "error": str(e)}
        )


@service_router.get(
    "/services/{service_id}/staff-requirements",
    summary="Get service staff requirements",
    description="Retrieve all staff requirements for a service"
)
def get_service_staff_requirements(
    service_id: int,
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Get all staff requirements for a service.
    
    Args:
        service_id: Service ID to fetch staff requirements for
        service_service: Injected service service
        
    Returns:
        List of staff requirements
    """
    logger.info(f"Fetching staff requirements for service {service_id}")
    
    try:
        # Check if service exists
        service = service_service.get_service_by_id(service_id)
        if not service:
            raise ServiceNotFoundException(service_id=service_id)
        
        staff_requirements = service_service.get_service_staff_requirements(service_id)
        
        return {
            "success": True,
            "data": staff_requirements,
            "service_id": service_id,
            "service_name": getattr(service, 'provided_service_name', None),
            "total_staff_requirements": len(staff_requirements)
        }
        
    except ServiceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch staff requirements for service {service_id}: {e}")
        raise ServiceException(
            message="Failed to retrieve staff requirements",
            details={"service_id": service_id, "error": str(e)}
        )