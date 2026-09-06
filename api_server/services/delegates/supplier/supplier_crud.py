"""
CRUD operations for suppliers.
"""

import logging
from typing import Optional, List, Dict, Any

from core.models.api_models import ProductProvider_API, Location_API, ProviderImage_API
from core.models.models import ProductProvider, ProductProviderType, ProviderImage
from core.exceptions.specific.supplier_exceptions import (
    SupplierAlreadyExistsException,
    SupplierInsertFailedException,
    SupplierUpdateFailedException,
    SupplierDeleteFailedException
)
from repositories.supplier_repository import SupplierRepository
from .supplier_validator import SupplierValidator
from .supplier_builder import SupplierBuilder
from .supplier_image import SupplierImageHandler

logger = logging.getLogger(__name__)


class SupplierCrud:
    """CRUD operations for suppliers"""
    
    def __init__(self):
        self.supplier_repo = SupplierRepository()
        self.validator = SupplierValidator()
        self.builder = SupplierBuilder()
        self.image_handler = SupplierImageHandler()
    
    def get_by_id(self, provider_id: str, full: bool = True) -> ProductProvider:
        """
        Get supplier by ID.
        
        Args:
            provider_id: Supplier ID to retrieve
            full: Whether to load all related data eagerly
            
        Returns:
            ProductProvider object
            
        Raises:
            SupplierNotFoundException: If supplier not found
        """
        return self.validator.validate_supplier_exists(provider_id, full)

    def get_suppliers_by_ids(self, provider_ids: List[str], full: bool = True) -> List[ProductProvider]:
        """
        Get suppliers by a list of IDs.
        
        Args:
            provider_ids: List of supplier IDs to retrieve
            full: Whether to load all related data eagerly
            
        Returns:
            List of ProductProvider objects
            
        Raises:
            SupplierNotFoundException: If any supplier not found
        """
        return self.supplier_repo.get_suppliers_by_ids(provider_ids, full)

    
    def get_all(
        self,
        owner_id: int = 0,
        org_id: int = 0,
        offset: int = 0,
        limit: int = 10
    ) -> List[ProductProvider]:
        """
        Get all suppliers with filters.
        
        Args:
            owner_id: Filter by owner ID
            org_id: Filter by organisation ID
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of ProductProvider objects
        """
        logger.debug(f"Fetching suppliers - owner_id:{owner_id}, org_id:{org_id}, offset:{offset}, limit:{limit}")
        return self.supplier_repo.get_all_suppliers(owner_id, org_id, offset, limit)
    
    def get_types(self) -> List[ProductProviderType]:
        """
        Get all supplier types.
        
        Returns:
            List of ProductProviderType objects
        """
        logger.debug("Fetching all supplier types")
        return self.supplier_repo.get_all_supplier_types()
    
    def create(
        self,
        provider: ProductProvider_API,
        location: Location_API,
        image: Optional[ProviderImage_API] = None,
    ) -> ProductProvider:
        """
        Create a new supplier.
        
        Args:
            provider: Supplier details
            location: Location information
            image: Optional supplier image
            
        Returns:
            Created ProductProvider object
            
        Raises:
            SupplierAlreadyExistsException: If supplier already exists
            SupplierInsertFailedException: If creation fails
        """
        logger.info(f"Creating new supplier: {provider.provider_name}")
        
        # Check if supplier already exists
        existing = self.supplier_repo.get_supplier_by_id(
            provider.id_product_provider, eager_load=False
        )
        if existing:
            logger.warning(f"Supplier already exists with ID: {provider.id_product_provider}")
            raise SupplierAlreadyExistsException(
                supplier_id=provider.id_product_provider,
                supplier_name=provider.provider_name
            )
        
        # Build supplier model
        new_supplier = self.builder.build_supplier_model(provider, location)
        
        # Handle image
        if image and image.provider_image_url:
            provider_image = ProviderImage(provider_image_url=image.provider_image_url)
            new_supplier.provider_image = [provider_image]
        
        # Save to database
        try:
            result = self.supplier_repo.create_supplier(new_supplier)
            logger.info(f"Supplier created successfully with ID: {result.id_product_provider}")
            return result
        except Exception as e:
            logger.error(f"Failed to create supplier: {e}")
            raise SupplierInsertFailedException(
                error=str(e),
                supplier_id=provider.id_product_provider,
                supplier_name=provider.provider_name
            )
    
    def update(
        self,
        provider: ProductProvider_API,
        image: Optional[ProviderImage_API] = None,
        location: Optional[Location_API] = None,
        user_id: Optional[int] = 0
    ) -> ProductProvider:
        """
        Update an existing supplier.
        
        Args:
            provider: Updated supplier details
            image: Optional updated image
            location: Optional updated location
            user_id: User ID for ownership validation
            
        Returns:
            Updated ProductProvider object
            
        Raises:
            SupplierNotFoundException: If supplier not found
            SupplierUpdateFailedException: If update fails
        """
        logger.info(f"Updating supplier with ID: {provider.id_product_provider}")
        
        # Validate
        self.validator.validate_supplier_type(provider.id_product_provider_type)
        supplier_old = self.validator.validate_supplier_exists(provider.id_product_provider)
        self.validator.validate_ownership(supplier_old, user_id)
        
        # Update details
        if supplier_old.product_provider_details:
            supplier_old.product_provider_details.provider_name = provider.provider_name
            supplier_old.product_provider_details.provider_contact_info = provider.provider_contact_info
        
        supplier_old.product_provider_type_id = provider.id_product_provider_type
        supplier_old.product_provider_org_id = provider.id_provider_organisation
        
        # Handle image update
        self.image_handler.handle_image(supplier_old, image)
        
        # Handle location update
        if location and location.id_location != 0:
            updated_location = self.builder.location_service.update_location(
                location.id_location, location
            )
            supplier_old.product_provider_location_id = updated_location.id_location
        
        # Save changes
        try:
            result = self.supplier_repo.update_supplier(supplier_old)
            logger.info(f"Supplier updated successfully with ID: {result.id_product_provider}")
            return result
        except Exception as e:
            logger.error(f"Failed to update supplier {provider.id_product_provider}: {e}")
            raise SupplierUpdateFailedException(
                supplier_id=provider.id_product_provider,
                error=str(e)
            )
    
    def delete(self, provider_id: str, user_id: int) -> Dict[str, Any]:
        """
        Delete a supplier and associated images.
        
        Args:
            provider_id: Supplier ID to delete
            user_id: User ID for ownership validation
            
        Returns:
            Dictionary with success message
            
        Raises:
            SupplierNotFoundException: If supplier not found
            SupplierDeleteFailedException: If deletion fails
        """
        logger.info(f"Deleting supplier with ID: {provider_id}")
        
        # Validate
        supplier = self.validator.validate_supplier_exists(provider_id)
        self.validator.validate_ownership(supplier, user_id)
        
        # Delete images
        self.image_handler.delete_images(provider_id)
        
        # Delete supplier
        success = self.supplier_repo.delete_supplier(supplier)
        
        if not success:
            logger.error(f"Failed to delete supplier {provider_id}")
            raise SupplierDeleteFailedException(
                supplier_id=provider_id,
                error="Repository returned False"
            )
        
        logger.info(f"Supplier {provider_id} deleted successfully")
        return {
            "success": True,
            "message": "Supplier deleted successfully",
            "supplier_id": provider_id
        }