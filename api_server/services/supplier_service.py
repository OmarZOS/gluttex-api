# services/supplier_service.py
"""
Supplier service for managing providers, their details, locations, and images.
"""

import logging
from typing import Optional, List, Dict, Any

from core.exceptions.specific.supplier_exceptions import *
from core.models.api_models import (
    Location_API, ProductProvider_API, ProviderImage_API,
    ProviderOrganisation_API, OrganisationImage_API
)
from core.models.models import (
    ProductProvider, ProductProviderType, ProviderDetails,
    ProviderImage, ProviderOrganisation, OrganisationImage
)
from repositories.supplier_repository import SupplierRepository, OrganisationRepository
from services.location_service import LocationService

logger = logging.getLogger(__name__)


class SupplierService:
    """Service for supplier/provider-related business logic"""
    
    def __init__(self):
        self.supplier_repo = SupplierRepository()
        self.org_repo = OrganisationRepository()
        self.location_service = LocationService()
    
    # ==================== Private Helper Methods ====================
    
    def _build_supplier_details(self, provider: ProductProvider_API) -> ProviderDetails:
        """Build ProviderDetails from API data"""
        details = ProviderDetails(
            provider_name=provider.provider_name,
            provider_contact_info=provider.provider_contact_info,
        )
        if provider.idprovider_details_id != 0:
            details.idprovider_details_id = provider.idprovider_details_id
        return details
    
    def _validate_supplier_type(self, supplier_type_id: int) -> ProductProviderType:
        """Validate that supplier type exists"""
        supplier_type = self.supplier_repo.get_supplier_type_by_id(supplier_type_id)
        if not supplier_type:
            logger.warning(f"Supplier type not found with ID: {supplier_type_id}")
            raise SupplierTypeNotFoundException(supplier_type_id=supplier_type_id)
        return supplier_type
    
    def _build_supplier_model(
        self,
        provider: ProductProvider_API,
        location: Optional[Location_API] = None
    ) -> ProductProvider:
        """Build ProductProvider model from API data"""
        
        # Validate supplier type
        supplier_type = self._validate_supplier_type(provider.id_product_provider_type)
        
        new_supplier = ProductProvider()
        new_supplier.product_provider_type_id = supplier_type.id_product_provider_type
        new_supplier.product_provider_owner = provider.id_provider_owner
        new_supplier.product_provider_details = self._build_supplier_details(provider)
        
        # Handle location
        if location:
            location_obj = self.location_service.build_location_model(location)
            new_supplier.product_provider_location = location_obj
        
        # Handle organisation
        if provider.id_provider_organisation == 0:
            new_supplier.product_provider_org = ProviderOrganisation(
                provider_organisation_name=provider.provider_organisation_name,
                provider_organisation_desc=provider.provider_organisation_desc
            )
        else:
            new_supplier.product_provider_org_id = provider.id_provider_organisation
        
        return new_supplier
    
    def _handle_supplier_image(self, supplier: ProductProvider, image: ProviderImage_API):
        """Handle supplier image creation or update"""
        if image.id_provider_image == 0:
            new_image = ProviderImage(provider_image_url=image.provider_image_url)
            new_image.provider_ref = supplier
            try:
                self.supplier_repo.create_supplier_image(new_image)
                logger.info(f"Created supplier image for supplier {supplier.id_product_provider}")
            except Exception as e:
                logger.error(f"Failed to create supplier image: {e}")
                raise ImageInsertFailedException(
                    error=str(e),
                    details={"supplier_id": supplier.id_product_provider}
                )
        else:
            existing_image = self.supplier_repo.get_supplier_image_by_id(image.id_provider_image)
            if existing_image:
                existing_image.provider_image_url = image.provider_image_url
                try:
                    self.supplier_repo.update_supplier_image(existing_image)
                    logger.info(f"Updated supplier image with ID: {image.id_provider_image}")
                except Exception as e:
                    logger.error(f"Failed to update supplier image: {e}")
                    raise ImageUpdateFailedException(
                        image_id=image.id_provider_image,
                        error=str(e)
                    )
    
    # ==================== Supplier CRUD Operations ====================
    
    def get_supplier_by_id(self, provider_id: str, full: bool = True) -> ProductProvider:
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
        supplier = self.supplier_repo.get_supplier_by_id(provider_id, eager_load=full)
        if not supplier:
            logger.warning(f"Supplier not found with ID: {provider_id}")
            raise SupplierNotFoundException(supplier_id=provider_id)
        
        logger.debug(f"Retrieved supplier with ID: {provider_id}")
        return supplier
    
    def get_all_suppliers(
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
    
    def get_supplier_types(self) -> List[ProductProviderType]:
        """
        Get all supplier types.
        
        Returns:
            List of ProductProviderType objects
        """
        logger.debug("Fetching all supplier types")
        return self.supplier_repo.get_all_supplier_types()
    
    def create_supplier(
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
            SupplierTypeNotFoundException: If supplier type not found
        """
        logger.info(f"Creating new supplier: {provider.provider_name}")
        
        # Check if supplier already exists
        existing = self.supplier_repo.get_supplier_by_id(provider.id_product_provider, eager_load=False)
        if existing:
            logger.warning(f"Supplier already exists with ID: {provider.id_product_provider}")
            raise SupplierAlreadyExistsException(
                supplier_id=provider.id_product_provider,
                supplier_name=provider.provider_name
            )
        
        # Build supplier model (validates supplier type internally)
        new_supplier = self._build_supplier_model(provider, location)
        
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
    
    def update_supplier(
        self,
        provider: ProductProvider_API,
        image: Optional[ProviderImage_API] = None,
        location: Optional[Location_API] = None
    ) -> ProductProvider:
        """
        Update an existing supplier.
        
        Args:
            provider: Updated supplier details
            image: Optional updated image
            location: Optional updated location
            
        Returns:
            Updated ProductProvider object
            
        Raises:
            SupplierNotFoundException: If supplier not found
            SupplierTypeNotFoundException: If supplier type not found
            SupplierUpdateFailedException: If update fails
        """
        logger.info(f"Updating supplier with ID: {provider.id_product_provider}")
        
        # Validate supplier type
        self._validate_supplier_type(provider.id_product_provider_type)
        
        # Fetch existing supplier
        supplier_old = self.get_supplier_by_id(provider.id_product_provider)
        
        # Update details
        if supplier_old.product_provider_details:
            supplier_old.product_provider_details.provider_name = provider.provider_name
            supplier_old.product_provider_details.provider_contact_info = provider.provider_contact_info
        
        supplier_old.product_provider_type_id = provider.id_product_provider_type
        supplier_old.product_provider_org_id = provider.id_provider_organisation
        
        # Handle image update
        if image and image.provider_image_url:
            self._handle_supplier_image(supplier_old, image)
        
        # Handle location update
        if location and location.id_location != 0:
            updated_location = self.location_service.update_location(
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
    
    def delete_supplier(self, provider_id: str) -> Dict[str, Any]:
        """
        Delete a supplier and associated images.
        
        Args:
            provider_id: Supplier ID to delete
            
        Returns:
            Dictionary with success message
            
        Raises:
            SupplierNotFoundException: If supplier not found
            SupplierDeleteFailedException: If deletion fails
        """
        logger.info(f"Deleting supplier with ID: {provider_id}")
        
        supplier = self.get_supplier_by_id(provider_id)
        
        # Delete all associated images
        images = self.supplier_repo.get_supplier_images(provider_id)
        for img in images:
            self.supplier_repo.delete_supplier_image(img)
        logger.info(f"Deleted {len(images)} associated images for supplier {provider_id}")
        
        # Delete the supplier
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
    
    # ==================== Supplier Search Operations ====================
    
    def search_suppliers_by_location(
        self,
        longitude: float,
        latitude: float,
        distance_km: float,
        offset: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search suppliers by location.
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            distance_km: Search radius in kilometers
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of suppliers with distance information
        """
        logger.info(f"Searching suppliers near ({longitude}, {latitude}) within {distance_km}km")
        return self.supplier_repo.search_by_location(
            (longitude, latitude), distance_km, offset, limit
        )
    


class OrganisationService:
    """Service for organisation-related business logic"""
    
    def __init__(self):
        self.org_repo = OrganisationRepository()
    
    # ==================== Private Helper Methods ====================
    
    def _handle_org_image(self, organisation: ProviderOrganisation, image: OrganisationImage_API):
        """Handle organisation image creation or update"""
        if image.id_org_image == 0:
            new_image = OrganisationImage(org_image_url=image.org_image_url)
            new_image.org_ref_id = organisation.id_provider_organisation
            try:
                self.org_repo.create_org_image(new_image)
                logger.info(f"Created organisation image for organisation {organisation.id_provider_organisation}")
            except Exception as e:
                logger.error(f"Failed to create organisation image: {e}")
                raise ImageInsertFailedException(
                    error=str(e),
                    details={"organisation_id": organisation.id_provider_organisation}
                )
        else:
            existing_image = self.org_repo.get_org_image_by_id(image.id_org_image)
            if existing_image:
                existing_image.org_image_url = image.org_image_url
                try:
                    self.org_repo.update_org_image(existing_image)
                    logger.info(f"Updated organisation image with ID: {image.id_org_image}")
                except Exception as e:
                    logger.error(f"Failed to update organisation image: {e}")
                    raise ImageUpdateFailedException(
                        image_id=image.id_org_image,
                        error=str(e)
                    )
    
    # ==================== Organisation CRUD Operations ====================
    
    def get_org_by_id(self, org_id: str) -> ProviderOrganisation:
        """
        Get organisation by ID.
        
        Args:
            org_id: Organisation ID to retrieve
            
        Returns:
            ProviderOrganisation object
            
        Raises:
            OrganisationNotFoundException: If organisation not found
        """
        org = self.org_repo.get_org_by_id(org_id)
        if not org:
            logger.warning(f"Organisation not found with ID: {org_id}")
            raise OrganisationNotFoundException(org_id=org_id)
        
        logger.debug(f"Retrieved organisation with ID: {org_id}")
        return org
    
    def get_org_by_name(self, org_name: str) -> Optional[ProviderOrganisation]:
        """
        Get organisation by name.
        
        Args:
            org_name: Organisation name to search for
            
        Returns:
            ProviderOrganisation object or None if not found
        """
        return self.org_repo.get_org_by_name(org_name)
    
    def get_all_orgs(self, offset: int = 0, limit: int = 100) -> List[ProviderOrganisation]:
        """
        Get all organisations with pagination.
        
        Args:
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of ProviderOrganisation objects
        """
        logger.debug(f"Fetching all organisations (offset={offset}, limit={limit})")
        return self.org_repo.get_all_orgs(offset, limit)
    
    def create_organisation(
        self,
        org: ProviderOrganisation_API,
        org_image: Optional[OrganisationImage_API] = None
    ) -> ProviderOrganisation:
        """
        Create a new organisation.
        
        Args:
            org: Organisation details
            org_image: Optional organisation image
            
        Returns:
            Created ProviderOrganisation object
            
        Raises:
            OrganisationAlreadyExistsException: If organisation name is taken
            OrganisationInsertFailedException: If creation fails
        """
        logger.info(f"Creating new organisation: {org.provider_organisation_name}")
        
        # Check if organisation name is taken
        existing = self.get_org_by_name(org.provider_organisation_name)
        if existing:
            logger.warning(f"Organisation name already exists: {org.provider_organisation_name}")
            raise OrganisationNameAlreadyUsedException(org_name=org.provider_organisation_name)
        
        # Build organisation model
        model_org = ProviderOrganisation(
            provider_organisation_name=org.provider_organisation_name,
            provider_organisation_desc=org.provider_organisation_desc
        )
        
        # Handle image
        if org_image and org_image.org_image_url:
            organisation_image = OrganisationImage(org_image_url=org_image.org_image_url)
            model_org.organisation_image = [organisation_image]
        
        # Save to database
        try:
            result = self.org_repo.create_org(model_org)
            logger.info(f"Organisation created successfully with ID: {result.idprovider_organisation}")
            return result
        except Exception as e:
            logger.error(f"Failed to create organisation: {e}")
            raise OrganisationInsertFailedException(
                error=str(e),
                org_name=org.provider_organisation_name
            )
    
    def update_organisation(
        self,
        organisation: ProviderOrganisation_API,
        image: Optional[OrganisationImage_API] = None
    ) -> ProviderOrganisation:
        """
        Update an existing organisation.
        
        Args:
            org: Updated organisation details
            image: Optional updated image
            
        Returns:
            Updated ProviderOrganisation object
            
        Raises:
            OrganisationNotFoundException: If organisation not found
            OrganisationNameAlreadyUsedException: If new name is taken
            OrganisationUpdateFailedException: If update fails
        """
        logger.info(f"Updating organisation with ID: {organisation.id_provider_organisation}")
        
        # Get existing organisation
        org_old = self.get_org_by_id(organisation.id_provider_organisation)
        
        # Check if name is taken (if changed)
        if org_old.provider_organisation_name != organisation.provider_organisation_name:
            existing = self.get_org_by_name(organisation.provider_organisation_name)
            if existing:
                logger.warning(f"Organisation name already exists: {organisation.provider_organisation_name}")
                raise OrganisationNameAlreadyUsedException(org_name=organisation.provider_organisation_name)
        
        # Update fields
        org_old.provider_organisation_name = organisation.provider_organisation_name
        org_old.provider_organisation_desc = organisation.provider_organisation_desc
        
        # Handle image
        if image and image.org_image_url:
            self._handle_org_image(org_old, image)
        
        # Save changes
        try:
            result = self.org_repo.update_org(org_old)
            logger.info(f"Organisation updated successfully with ID: {result.idprovider_organisation}")
            return result
        except Exception as e:
            logger.error(f"Failed to update organisation {organisation.id_provider_organisation}: {e}")
            raise OrganisationUpdateFailedException(
                org_id=organisation.id_provider_organisation,
                error=str(e)
            )
    
    def delete_organisation(self, org_id: str) -> Dict[str, Any]:
        """
        Delete an organisation and associated images.
        
        Args:
            org_id: Organisation ID to delete
            
        Returns:
            Dictionary with success message
            
        Raises:
            OrganisationNotFoundException: If organisation not found
            OrganisationDeleteFailedException: If deletion fails
        """
        logger.info(f"Deleting organisation with ID: {org_id}")
        
        org = self.get_org_by_id(org_id)
        
        # Delete associated images
        images = self.org_repo.get_org_images(org_id)
        for img in images:
            self.org_repo.delete_org_image(img)
        logger.info(f"Deleted {len(images)} associated images for organisation {org_id}")
        
        # Delete organisation
        success = self.org_repo.delete_org(org)
        
        if not success:
            logger.error(f"Failed to delete organisation {org_id}")
            raise OrganisationDeleteFailedException(
                org_id=org_id,
                error="Repository returned False"
            )
        
        logger.info(f"Organisation {org_id} deleted successfully")
        return {
            "success": True,
            "message": "Organisation deleted successfully",
            "organisation_id": org_id
        }