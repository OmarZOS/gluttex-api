# services/service_service.py
from typing import List, Optional
from core.api_models import ProvidedService_API, ServiceResourceRequirement_API, ServiceStaffRequirement_API
from core.exceptions.handler import APIException
from core.messages import *
from core.models import ProvidedService, ServiceResourceRequirement, ServiceStaffRequirement
from repositories.cart_repository import ServiceRepository

class ServiceService:
    """Service for service-related business logic"""
    
    def __init__(self):
        self.service_repo = ServiceRepository()
    
    def _build_resource_requirement(self, api_req: ServiceResourceRequirement_API) -> ServiceResourceRequirement:
        """Build resource requirement from API data"""
        req = ServiceResourceRequirement(
            service_resource_requirement_service_id=api_req.resource_requirement_service_id,
            service_resource_requirement_name=api_req.resource_requirement_name,
            service_resource_requirement_type=api_req.resource_requirement_type,
            service_resource_requirement_quantity=api_req.resource_requirement_quantity,
            service_resource_requirement_cost_per_unit=api_req.resource_requirement_cost_per_unit,
            service_resource_requirement_is_consumable=api_req.resource_requirement_is_consumable,
            service_resource_requirement_notes=api_req.resource_requirement_notes,
            service_resource_requirement_product_ref=api_req.resource_requirement_product_ref,
        )
        
        if api_req.resource_requirement_id != 0:
            req.service_resource_requirement_id = api_req.resource_requirement_id
        
        return req
    
    def _build_staff_requirement(self, api_req: ServiceStaffRequirement_API) -> ServiceStaffRequirement:
        """Build staff requirement from API data"""
        req = ServiceStaffRequirement(
            service_staff_requirement_service_id=api_req.service_staff_requirement_service_id,
            service_staff_requirement_role=api_req.service_staff_requirement_role,
            service_staff_requirement_min_count=api_req.service_staff_requirement_min_count,
            service_staff_requirement_max_count=api_req.service_staff_requirement_max_count,
            service_staff_requirement_hourly_rate=api_req.service_staff_requirement_hourly_rate,
            service_staff_requirement_allocated_hours=api_req.service_staff_requirement_allocated_hours,
            service_staff_requirement_notes=api_req.service_staff_requirement_notes,
        )
        
        if api_req.service_staff_requirement_id != 0:
            req.service_staff_requirement_id = api_req.service_staff_requirement_id
        
        return req
    
    def _build_service_model(self, api_service: ProvidedService_API) -> ProvidedService:
        """Build service model from API data"""
        service = ProvidedService(
            provided_service_name=api_service.provided_service_name,
            provided_service_description=api_service.provided_service_description,
            provided_service_category_id=api_service.provided_service_category_id,
            provided_service_product_provider_id=api_service.provided_service_product_provider_id,
            provided_service_base_price=api_service.provided_service_base_price,
            provided_service_final_price=api_service.provided_service_final_price,
            provided_service_actual_duration=api_service.provided_service_actual_duration,
            provided_service_is_active=api_service.provided_service_is_active,
            provided_service_pricing_config=api_service.provided_service_pricing_config,
        )
        
        if api_service.provided_service_id != 0:
            service.provided_service_id = api_service.provided_service_id
        
        return service
    
    def get_service_by_id(self, service_id: int) -> ProvidedService:
        """Get service by ID"""
        service = self.service_repo.get_service_by_id(service_id)
        if not service:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=SERVICE_NOT_FOUND,
                details=f"Service #{service_id} not found"
            )
        return service
    
    def get_services_by_category(self, category_id: int, offset: int = 0, limit: int = 100) -> List[ProvidedService]:
        """Get services by category"""
        return self.service_repo.get_services_by_category(category_id, offset, limit)
    
    def get_services_by_provider(self, provider_id: int, offset: int = 0, limit: int = 100) -> List[ProvidedService]:
        """Get services by provider"""
        return self.service_repo.get_services_by_provider(provider_id, offset, limit)
    
    def get_active_services(self, provider_id: Optional[int] = None) -> List[ProvidedService]:
        """Get active services"""
        return self.service_repo.get_active_services(provider_id)
    
    def create_service(
        self,
        service_data: ProvidedService_API,
        requirements: List[ServiceResourceRequirement_API],
        staff_requirements: List[ServiceStaffRequirement_API]
    ) -> ProvidedService:
        """Create a new service"""
        
        if service_data.provided_service_category_id == 0:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=SERVICE_CATEGORY_NOT_FOUND,
                details=SERVICE_CATEGORY_NOT_FOUND
            )
        
        # Build service
        service = self._build_service_model(service_data)
        
        # Add requirements
        service.resource_requirements = [
            self._build_resource_requirement(req) for req in requirements
        ]
        service.staff_requirements = [
            self._build_staff_requirement(req) for req in staff_requirements
        ]
        
        # Save service
        try:
            return self.service_repo.create_service(service)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=SERVICE_INSERT_FAILED,
                details=f"Failed to create service: {str(e)}"
            )
    
    def update_service(self, service_id: int, service_data: ProvidedService_API) -> ProvidedService:
        """Update an existing service"""
        service = self.get_service_by_id(service_id)
        
        # Update fields
        service.provided_service_name = service_data.provided_service_name
        service.provided_service_description = service_data.provided_service_description
        service.provided_service_category_id = service_data.provided_service_category_id
        service.provided_service_base_price = service_data.provided_service_base_price
        service.provided_service_final_price = service_data.provided_service_final_price
        service.provided_service_actual_duration = service_data.provided_service_actual_duration
        service.provided_service_is_active = service_data.provided_service_is_active
        service.provided_service_pricing_config = service_data.provided_service_pricing_config
        
        try:
            return self.service_repo.update_service(service)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=SERVICE_UPDATE_FAILED,
                details=f"Failed to update service: {str(e)}"
            )
    
    def delete_service(self, service_id: int) -> bool:
        """Delete a service"""
        service = self.get_service_by_id(service_id)
        return self.service_repo.delete_service(service)
    
    def toggle_service_status(self, service_id: int, is_active: bool) -> ProvidedService:
        """Activate or deactivate a service"""
        service = self.get_service_by_id(service_id)
        service.provided_service_is_active = is_active
        return self.service_repo.update_service(service)