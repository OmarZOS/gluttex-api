"""
Supplier service for managing providers, their details, locations, and images.
"""

import logging
from typing import Optional, List, Dict, Any

from services.delegates.supplier.supplier_search import SupplierSearch
from services.delegates.supplier.organisation_crud import OrganisationCrud
from services.delegates.supplier.supplier_crud import SupplierCrud
from core.models.api_models import (
    Location_API, ProductProvider_API, ProviderImage_API,
    ProviderOrganisation_API, OrganisationImage_API
)
from core.models.models import ProductProvider, ProductProviderType, ProviderOrganisation

# Import components

logger = logging.getLogger(__name__)


class SupplierService:
    """Service for supplier/provider-related business logic"""
    
    def __init__(self):
        self.supplier_crud = SupplierCrud()
        self.organisation_crud = OrganisationCrud()
    
    # ==================== Supplier Operations ====================
    
    def get_supplier_by_id(self, provider_id: str, full: bool = True) -> ProductProvider:
        """Get supplier by ID."""
        return self.supplier_crud.get_by_id(provider_id, full)
    
    def get_all_suppliers(
        self,
        owner_id: int = 0,
        org_id: int = 0,
        offset: int = 0,
        limit: int = 10
    ) -> List[ProductProvider]:
        """Get all suppliers with filters."""
        return self.supplier_crud.get_all(owner_id, org_id, offset, limit)
    
    def get_supplier_types(self) -> List[ProductProviderType]:
        """Get all supplier types."""
        return self.supplier_crud.get_types()
    
    def create_supplier(
        self,
        provider: ProductProvider_API,
        location: Location_API,
        image: Optional[ProviderImage_API] = None,
    ) -> ProductProvider:
        """Create a new supplier."""
        return self.supplier_crud.create(provider, location, image)
    
    def update_supplier(
        self,
        provider: ProductProvider_API,
        image: Optional[ProviderImage_API] = None,
        location: Optional[Location_API] = None,
        user_id: Optional[int] = 0
    ) -> ProductProvider:
        """Update an existing supplier."""
        return self.supplier_crud.update(provider, image, location, user_id)
    
    def delete_supplier(self, provider_id: str, user_id: int) -> Dict[str, Any]:
        """Delete a supplier and associated images."""
        return self.supplier_crud.delete(provider_id, user_id)
    
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
        search = SupplierSearch()
        logger.info(f"Searching suppliers near ({longitude}, {latitude}) within {distance_km}km")
        return search.search_by_location(longitude, latitude, distance_km, offset, limit)


class OrganisationService:
    """Service for organisation-related business logic"""
    
    def __init__(self):
        self.organisation_crud = OrganisationCrud()
    
    def get_org_by_id(self, org_id: str) -> ProviderOrganisation:
        """Get organisation by ID."""
        return self.organisation_crud.get_by_id(org_id)
    
    def get_org_by_name(self, org_name: str) -> Optional[ProviderOrganisation]:
        """Get organisation by name."""
        return self.organisation_crud.get_by_name(org_name)
    
    def get_all_orgs(self, offset: int = 0, limit: int = 100) -> List[ProviderOrganisation]:
        """Get all organisations with pagination."""
        return self.organisation_crud.get_all(offset, limit)
    
    def create_organisation(
        self,
        org: ProviderOrganisation_API,
        org_image: Optional[OrganisationImage_API] = None
    ) -> ProviderOrganisation:
        """Create a new organisation."""
        return self.organisation_crud.create(org, org_image)
    
    def update_organisation(
        self,
        organisation: ProviderOrganisation_API,
        image: Optional[OrganisationImage_API] = None
    ) -> ProviderOrganisation:
        """Update an existing organisation."""
        return self.organisation_crud.update(organisation, image)
    
    def delete_organisation(self, org_id: str, user_id: int) -> Dict[str, Any]:
        """Delete an organisation and associated images."""
        return self.organisation_crud.delete(org_id, user_id)