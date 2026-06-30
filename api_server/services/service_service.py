# services/service_service.py

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.models.api_models import ProvidedService_API, ServiceResourceRequirement_API, ServiceStaffRequirement_API
from core.exceptions.specific.service_exceptions import (
    ServiceException,
    ServiceNotFoundException,
    ServiceCreationFailedException,
    ServiceUpdateFailedException,
    ServiceDeleteFailedException,
    ServiceCategoryNotFoundException,
    ServiceProviderNotFoundException,
    ServiceToggleStatusException,
    ServiceRequirementCreationException,
    ServiceRequirementNotFoundException,
    ServiceStaffRequirementNotFoundException
)
from core.messages import *
from core.models.models import ProvidedService, ServiceResourceRequirement, ServiceStaffRequirement
from repositories.cart_repository import ServiceRepository
from repositories.supplier_repository import SupplierRepository

logger = logging.getLogger(__name__)


class ServiceService:
    """Service for service-related business logic"""
    
    def __init__(self):
        self.service_repo = ServiceRepository()
        self.provider_repo = SupplierRepository()
        # self.category_repo = CategoryRepository()
    
    # ==================== Private Helper Methods ====================
    
    def _build_service_model(self, api_service: ProvidedService_API) -> ProvidedService:
        """
        Build service model from API data.
        
        Args:
            api_service: API service data
            
        Returns:
            ProvidedService model instance
        """
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
            # provided_service_notes=api_service.provided_service_notes,
            # provided_service_creation=datetime.now(),
            # provided_service_last_updated=datetime.now()
        )
        
        if api_service.provided_service_id != 0:
            service.provided_service_id = api_service.provided_service_id
        
        return service
    
    def _build_resource_requirement(self, api_req: ServiceResourceRequirement_API) -> ServiceResourceRequirement:
        """
        Build resource requirement from API data.
        
        Args:
            api_req: API resource requirement data
            
        Returns:
            ServiceResourceRequirement model instance
        """
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
        """
        Build staff requirement from API data.
        
        Args:
            api_req: API staff requirement data
            
        Returns:
            ServiceStaffRequirement model instance
        """
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
    
    def _validate_provider_exists(self, provider_id: int) -> bool:
        """
        Validate that a provider exists.
        
        Args:
            provider_id: Provider ID to validate
            
        Returns:
            True if provider exists
            
        Raises:
            ServiceProviderNotFoundException: If provider not found
        """
        provider = self.provider_repo.get_supplier_by_id(provider_id)
        if not provider:
            logger.warning(f"Provider not found with ID: {provider_id}")
            raise ServiceProviderNotFoundException(provider_id=provider_id)
        return True
    
    def _validate_category_exists(self, category_id: int) -> bool:
        """
        Validate that a category exists.
        
        Args:
            category_id: Category ID to validate
            
        Returns:
            True if category exists
            
        Raises:
            ServiceCategoryNotFoundException: If category not found
        """
        category = self.service_repo.get_category_by_id(category_id)
        if not category:
            logger.warning(f"Category not found with ID: {category_id}")
            raise ServiceCategoryNotFoundException(category_id=category_id)
        return True
    
    def _check_service_dependencies(self, service_id: int) -> bool:
        """
        Check if service has dependencies.
        
        Args:
            service_id: Service ID to check
            
        Returns:
            True if service has dependencies
        """
        # Check if service is used in any packages
        package_items = self.service_repo.get_package_items_by_service(service_id)
        if package_items:
            logger.debug(f"Service {service_id} has {len(package_items)} package items")
            return True
        
        # Check if service is in any carts
        cart_items = self.service_repo.get_cart_items_by_service(service_id)
        if cart_items:
            logger.debug(f"Service {service_id} has {len(cart_items)} cart items")
            return True
        
        return False
    
    # ==================== Service Retrieval Methods ====================
    
    def get_service_by_id(self, service_id: int) -> ProvidedService:
        """
        Get service by ID.
        
        Args:
            service_id: Service ID to retrieve
            
        Returns:
            ProvidedService object
            
        Raises:
            ServiceNotFoundException: If service not found
        """
        service = self.service_repo.get_service_by_id(service_id)
        if not service:
            logger.warning(f"Service not found with ID: {service_id}")
            raise ServiceNotFoundException(service_id=service_id)
        
        logger.debug(f"Retrieved service with ID: {service_id}")
        return service
    
    def get_services_by_category(self, category_id: int, offset: int = 0, limit: int = 100) -> List[ProvidedService]:
        """
        Get services by category.
        
        Args:
            category_id: Category ID to filter by
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of ProvidedService objects
            
        Raises:
            ServiceCategoryNotFoundException: If category not found
        """
        # Validate category exists
        self._validate_category_exists(category_id)
        
        logger.debug(f"Fetching services for category {category_id}")
        return self.service_repo.get_services_by_category(category_id, offset, limit)
    
    def get_services_by_provider(self, provider_id: int, offset: int = 0, limit: int = 100) -> List[ProvidedService]:
        """
        Get services by provider.
        
        Args:
            provider_id: Provider ID to filter by
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of ProvidedService objects
            
        Raises:
            ServiceProviderNotFoundException: If provider not found
        """
        # Validate provider exists
        self._validate_provider_exists(provider_id)
        
        logger.debug(f"Fetching services for provider {provider_id}")
        return self.service_repo.get_services_by_provider(provider_id, offset, limit)
    
    def get_services(self,  offset: int = 0, limit: int = 100) -> List[ProvidedService]:
        """
        Get services by provider.
        
        Args:
            provider_id: Provider ID to filter by
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of ProvidedService objects
            
        Raises:
            ServiceProviderNotFoundException: If provider not found
        """
        # Validate provider exists
        
        logger.debug(f"Fetching services...")
        return self.service_repo.get_services( offset, limit)
    
    def get_active_services(self, provider_id: Optional[int] = None) -> List[ProvidedService]:
        """
        Get active services.
        
        Args:
            provider_id: Optional provider ID to filter by
            
        Returns:
            List of active ProvidedService objects
            
        Raises:
            ServiceProviderNotFoundException: If provider not found (when provided)
        """
        if provider_id:
            self._validate_provider_exists(provider_id)
        
        logger.debug(f"Fetching active services (provider_id={provider_id})")
        return self.service_repo.get_active_services(provider_id)
    
    def get_service_requirements(self, service_id: int) -> List[ServiceResourceRequirement]:
        """
        Get resource requirements for a service.
        
        Args:
            service_id: Service ID
            
        Returns:
            List of ServiceResourceRequirement objects
            
        Raises:
            ServiceNotFoundException: If service not found
        """
        # Validate service exists
        self.get_service_by_id(service_id)
        
        logger.debug(f"Fetching requirements for service {service_id}")
        return self.service_repo.get_service_resource_requirements(service_id)
    
    def get_service_staff_requirements(self, service_id: int) -> List[ServiceStaffRequirement]:
        """
        Get staff requirements for a service.
        
        Args:
            service_id: Service ID
            
        Returns:
            List of ServiceStaffRequirement objects
            
        Raises:
            ServiceNotFoundException: If service not found
        """
        # Validate service exists
        self.get_service_by_id(service_id)
        
        logger.debug(f"Fetching staff requirements for service {service_id}")
        return self.service_repo.get_service_staff_requirements(service_id)
    
    # ==================== Service Creation Methods ====================
    
    def create_service(
        self,
        service_data: ProvidedService_API,
        requirements: List[ServiceResourceRequirement_API],
        staff_requirements: List[ServiceStaffRequirement_API]
    ) -> ProvidedService:
        """
        Create a new service.
        
        Args:
            service_data: Service details
            requirements: Resource requirements
            staff_requirements: Staff requirements
            
        Returns:
            Created ProvidedService object
            
        Raises:
            ServiceCategoryNotFoundException: If category not found
            ServiceProviderNotFoundException: If provider not found
            ServiceCreationFailedException: If creation fails
            ServiceRequirementCreationException: If requirement creation fails
        """
        logger.info(f"Creating new service: {service_data.provided_service_name}")
        
        # Validate category
        if service_data.provided_service_category_id:
            self._validate_category_exists(service_data.provided_service_category_id)
        
        # Validate provider
        if service_data.provided_service_product_provider_id:
            self._validate_provider_exists(service_data.provided_service_product_provider_id)
        
        # Build service
        service = self._build_service_model(service_data)
        
        # Add resource requirements
        resource_reqs = []
        for req_data in requirements:
            try:
                req = self._build_resource_requirement(req_data)
                resource_reqs.append(req)
            except Exception as e:
                logger.error(f"Failed to build resource requirement: {e}")
                raise ServiceRequirementCreationException(
                    service_id=0,
                    error=f"Failed to build resource requirement: {str(e)}"
                )
        service.resource_requirements = resource_reqs
        
        # Add staff requirements
        staff_reqs = []
        for req_data in staff_requirements:
            try:
                req = self._build_staff_requirement(req_data)
                staff_reqs.append(req)
            except Exception as e:
                logger.error(f"Failed to build staff requirement: {e}")
                raise ServiceRequirementCreationException(
                    service_id=0,
                    error=f"Failed to build staff requirement: {str(e)}"
                )
        service.staff_requirements = staff_reqs
        
        # Save service
        try:
            result = self.service_repo.create_service(service)
            logger.info(f"Service created successfully with ID: {result.provided_service_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create service: {e}")
            raise ServiceCreationFailedException(
                error=str(e),
                service_name=service_data.provided_service_name,
                provider_id=service_data.provided_service_product_provider_id
            )
    
    # ==================== Service Update Methods ====================
    
    def update_service(self, service_id: int, service_data: ProvidedService_API) -> ProvidedService:
        """
        Update an existing service.
        
        Args:
            service_id: Service ID to update
            service_data: Updated service details
            
        Returns:
            Updated ProvidedService object
            
        Raises:
            ServiceNotFoundException: If service not found
            ServiceCategoryNotFoundException: If category not found
            ServiceProviderNotFoundException: If provider not found
            ServiceUpdateFailedException: If update fails
        """
        logger.info(f"Updating service with ID: {service_id}")
        
        # Validate service exists
        service = self.get_service_by_id(service_id)
        
        # Validate category if changed
        if service_data.provided_service_category_id and service_data.provided_service_category_id != service.provided_service_category_id:
            self._validate_category_exists(service_data.provided_service_category_id)
        
        # Validate provider if changed
        if service_data.provided_service_product_provider_id and service_data.provided_service_product_provider_id != service.provided_service_product_provider_id:
            self._validate_provider_exists(service_data.provided_service_product_provider_id)
        
        # Track changes for logging
        changes = []
        if service.provided_service_name != service_data.provided_service_name:
            changes.append(f"name: {service.provided_service_name} -> {service_data.provided_service_name}")
        if service.provided_service_base_price != service_data.provided_service_base_price:
            changes.append(f"price: {service.provided_service_base_price} -> {service_data.provided_service_base_price}")
        if service.provided_service_is_active != service_data.provided_service_is_active:
            changes.append(f"active: {service.provided_service_is_active} -> {service_data.provided_service_is_active}")
        
        # Update fields
        service.provided_service_name = service_data.provided_service_name
        service.provided_service_description = service_data.provided_service_description
        service.provided_service_category_id = service_data.provided_service_category_id
        service.provided_service_base_price = service_data.provided_service_base_price
        service.provided_service_final_price = service_data.provided_service_final_price
        service.provided_service_actual_duration = service_data.provided_service_actual_duration
        service.provided_service_is_active = service_data.provided_service_is_active
        service.provided_service_pricing_config = service_data.provided_service_pricing_config
        # service.provided_service_notes = service_data.provided_service_notes
        # service.provided_service_last_updated = datetime.now()
        
        # Save service
        try:
            updated_service = self.service_repo.update_service(service)
            logger.info(f"Service {service_id} updated successfully. Changes: {changes if changes else 'none'}")
            return updated_service
        except Exception as e:
            logger.error(f"Failed to update service {service_id}: {e}")
            raise ServiceUpdateFailedException(
                service_id=service_id,
                error=str(e)
            )
    
    def toggle_service_status(self, service_id: int, is_active: bool) -> ProvidedService:
        """
        Activate or deactivate a service.
        
        Args:
            service_id: Service ID to toggle
            is_active: New active status
            
        Returns:
            Updated ProvidedService object
            
        Raises:
            ServiceNotFoundException: If service not found
            ServiceToggleStatusException: If already in requested state
            ServiceUpdateFailedException: If update fails
        """
        action = "activate" if is_active else "deactivate"
        logger.info(f"Attempting to {action} service {service_id}")
        
        # Validate service exists
        service = self.get_service_by_id(service_id)
        
        # Check current status
        current_status = service.provided_service_is_active
        if current_status == is_active:
            logger.warning(f"Service {service_id} already {'active' if is_active else 'inactive'}")
            raise ServiceToggleStatusException(
                service_id=service_id,
                current_status=current_status,
                requested_status=is_active,
                error=f"Service already {'active' if is_active else 'inactive'}"
            )
        
        # Toggle status
        service.provided_service_is_active = is_active
        service.provided_service_last_updated = datetime.now()
        
        try:
            updated_service = self.service_repo.update_service(service)
            logger.info(f"Service {service_id} {action}d successfully")
            return updated_service
        except Exception as e:
            logger.error(f"Failed to {action} service {service_id}: {e}")
            raise ServiceToggleStatusException(
                service_id=service_id,
                requested_status=is_active,
                error=str(e)
            )
    
    # ==================== Service Deletion Methods ====================
    
    def delete_service(self, service_id: int, force_delete: bool = False) -> Dict[str, Any]:
        """
        Delete a service and all associated requirements.
        
        Args:
            service_id: Service ID to delete
            force_delete: Force delete even if service has dependencies
            
        Returns:
            Deletion confirmation
            
        Raises:
            ServiceNotFoundException: If service not found
            ServiceDeleteFailedException: If deletion fails
        """
        logger.info(f"Deleting service with ID: {service_id} (force={force_delete})")
        
        # Validate service exists
        service = self.get_service_by_id(service_id)
        
        requirements = self.service_repo.get_service_resource_requirements(service_id)
        staff_requirements = self.service_repo.get_service_staff_requirements(service_id)


        # Check if service has requirements
        has_requirements = len(requirements) > 0
        has_staff_requirements = len(staff_requirements) > 0
        
        if not force_delete:
            # Check if service has dependencies (orders, carts)
            has_dependencies = self._check_service_dependencies(service_id)
            
            if has_dependencies:
                logger.warning(f"Service {service_id} has dependencies, use force_delete=true")
                raise ServiceDeleteFailedException(
                    service_id=service_id,
                    has_dependencies=True,
                    error="Service has existing dependencies (orders, carts)"
                )
            
            if has_requirements or has_staff_requirements:
                logger.warning(f"Service {service_id} has associated requirements, use force_delete=true")
                raise ServiceDeleteFailedException(
                    service_id=service_id,
                    error="Service has associated requirements. Use force_delete=true to delete."
                )
        
        # Delete resource requirements
        if has_requirements:
            try:
                for r in requirements:
                    self.service_repo.delete_service_resource_requirements(r.service_resource_requirement_id)
                logger.debug(f"Deleted resource requirements for service {service_id}")
            except Exception as e:
                logger.error(f"Failed to delete resource requirements: {e}")
                raise ServiceDeleteFailedException(
                    service_id=service_id,
                    error=f"Failed to delete resource requirements: {str(e)}"
                )
        
        # Delete staff requirements
        if has_staff_requirements:
            try:
                for r in staff_requirements:
                    self.service_repo.delete_service_staff_requirements(r)
                logger.debug(f"Deleted staff requirements for service {service_id}")
            except Exception as e:
                logger.error(f"Failed to delete staff requirements: {e}")
                raise ServiceDeleteFailedException(
                    service_id=service_id,
                    error=f"Failed to delete staff requirements: {str(e)}"
                )
        
        # Delete service
        try:
            success = self.service_repo.delete_service(service)
            
            if not success:
                raise ServiceDeleteFailedException(
                    service_id=service_id,
                    error="Repository returned False"
                )
            
            logger.info(f"Service {service_id} deleted successfully")
            return {
                "message": f"Service {service_id} deleted successfully",
                "service_id": service_id
            }
            
        except ServiceDeleteFailedException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete service {service_id}: {e}")
            raise ServiceDeleteFailedException(
                service_id=service_id,
                error=str(e)
            )
    
    # ==================== Requirement Management Methods ====================
    
    def add_resource_requirement(self, service_id: int, requirement_data: ServiceResourceRequirement_API) -> ServiceResourceRequirement:
        """
        Add a resource requirement to a service.
        
        Args:
            service_id: Service ID
            requirement_data: Resource requirement data
            
        Returns:
            Created ServiceResourceRequirement object
            
        Raises:
            ServiceNotFoundException: If service not found
            ServiceRequirementCreationException: If creation fails
        """
        logger.info(f"Adding resource requirement to service {service_id}")
        
        # Validate service exists
        self.get_service_by_id(service_id)
        
        requirement = self._build_resource_requirement(requirement_data)
        requirement.service_resource_requirement_service_id = service_id
        
        try:
            result = self.service_repo.create_resource_requirement(requirement)
            logger.info(f"Resource requirement created with ID: {result.service_resource_requirement_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create resource requirement: {e}")
            raise ServiceRequirementCreationException(
                service_id=service_id,
                error=str(e)
            )
    
    def add_staff_requirement(self, service_id: int, requirement_data: ServiceStaffRequirement_API) -> ServiceStaffRequirement:
        """
        Add a staff requirement to a service.
        
        Args:
            service_id: Service ID
            requirement_data: Staff requirement data
            
        Returns:
            Created ServiceStaffRequirement object
            
        Raises:
            ServiceNotFoundException: If service not found
            ServiceRequirementCreationException: If creation fails
        """
        logger.info(f"Adding staff requirement to service {service_id}")
        
        # Validate service exists
        self.get_service_by_id(service_id)
        
        requirement = self._build_staff_requirement(requirement_data)
        requirement.service_staff_requirement_service_id = service_id
        
        try:
            result = self.service_repo.create_staff_requirement(requirement)
            logger.info(f"Staff requirement created with ID: {result.service_staff_requirement_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create staff requirement: {e}")
            raise ServiceRequirementCreationException(
                service_id=service_id,
                error=str(e)
            )
    
    def remove_resource_requirement(self, requirement_id: int) -> Dict[str, Any]:
        """
        Remove a resource requirement.
        
        Args:
            requirement_id: Requirement ID to remove
            
        Returns:
            Deletion confirmation
            
        Raises:
            ServiceRequirementNotFoundException: If requirement not found
            ServiceDeleteFailedException: If deletion fails
        """
        logger.info(f"Removing resource requirement {requirement_id}")
        
        requirement = self.service_repo.get_resource_requirement_by_id(requirement_id)
        if not requirement:
            raise ServiceRequirementNotFoundException(requirement_id=requirement_id)
        
        try:
            success = self.service_repo.delete_resource_requirement(requirement_id)
            if not success:
                raise ServiceDeleteFailedException(
                    service_id=requirement.service_resource_requirement_service_id,
                    error="Failed to delete resource requirement"
                )
            
            logger.info(f"Resource requirement {requirement_id} deleted successfully")
            return {
                "message": f"Resource requirement {requirement_id} deleted successfully",
                "requirement_id": requirement_id
            }
        except Exception as e:
            logger.error(f"Failed to delete resource requirement {requirement_id}: {e}")
            raise ServiceDeleteFailedException(
                service_id=requirement.service_resource_requirement_service_id,
                error=str(e)
            )
    
    def remove_staff_requirement(self, requirement_id: int) -> Dict[str, Any]:
        """
        Remove a staff requirement.
        
        Args:
            requirement_id: Requirement ID to remove
            
        Returns:
            Deletion confirmation
            
        Raises:
            ServiceStaffRequirementNotFoundException: If requirement not found
            ServiceDeleteFailedException: If deletion fails
        """
        logger.info(f"Removing staff requirement {requirement_id}")
        
        requirement = self.service_repo.get_staff_requirement_by_id(requirement_id)
        if not requirement:
            raise ServiceStaffRequirementNotFoundException(requirement_id=requirement_id)
        
        try:
            success = self.service_repo.delete_staff_requirement(requirement_id)
            if not success:
                raise ServiceDeleteFailedException(
                    service_id=requirement.service_staff_requirement_service_id,
                    error="Failed to delete staff requirement"
                )
            
            logger.info(f"Staff requirement {requirement_id} deleted successfully")
            return {
                "message": f"Staff requirement {requirement_id} deleted successfully",
                "requirement_id": requirement_id
            }
        except Exception as e:
            logger.error(f"Failed to delete staff requirement {requirement_id}: {e}")
            raise ServiceDeleteFailedException(
                service_id=requirement.service_staff_requirement_service_id,
                error=str(e)
            )