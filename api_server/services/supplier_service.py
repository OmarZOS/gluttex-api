# services/supplier_service.py
from typing import Optional, List, Dict, Any
from core.api_models import (
    Location_API, ProductProvider_API, ProviderImage_API,
    ProviderOrganisation_API, OrganisationImage_API
)
from core.exception_handler import APIException
from core.messages import *
from core.models import (
    ProductProvider, ProductProviderType, ProviderDetails,
    ProviderImage, ProviderOrganisation, OrganisationImage
)
from repositories.supplier_repository import SupplierRepository, OrganisationRepository
from services.location_service import LocationService

class SupplierService:
    """Service for supplier/provider-related business logic"""
    
    def __init__(self):
        self.supplier_repo = SupplierRepository()
        self.org_repo = OrganisationRepository()
        self.location_service = LocationService()
    
    def _build_supplier_details(self, provider: ProductProvider_API) -> ProviderDetails:
        """Build ProviderDetails from API data"""
        details = ProviderDetails(
            provider_name=provider.provider_name,
            provider_contact_info=provider.provider_contact_info,
        )
        if provider.idprovider_details_id != 0:
            details.idprovider_details_id = provider.idprovider_details_id
        return details
    
    def _build_supplier_model(
        self,
        provider: ProductProvider_API,
        location: Optional[Location_API] = None
    ) -> ProductProvider:
        """Build ProductProvider model from API data"""
        
        # Validate supplier type
        supplier_type = self.supplier_repo.get_supplier_type_by_id(provider.id_product_provider_type)
        if not supplier_type:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=SUPPLIER_TYPE_NOT_EXISTS,
                message=f"{SUPPLIER_TYPE_NOT_EXISTS}: {provider.id_product_provider_type}"
            )
        
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
    
    def get_supplier_by_id(self, provider_id: str, full: bool = True) -> ProductProvider:
        """Get supplier by ID"""
        supplier = self.supplier_repo.get_supplier_by_id(provider_id, eager_load=full)
        if not supplier:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=SUPPLIER_NOT_EXISTS,
                message=SUPPLIER_NOT_EXISTS,
                details=f"Supplier {provider_id} not found"
            )
        return supplier
    
    def get_all_suppliers(
        self,
        owner_id: int = 0,
        org_id: int = 0,
        offset: int = 0,
        limit: int = 10
    ) -> List[ProductProvider]:
        """Get all suppliers with filters"""
        return self.supplier_repo.get_all_suppliers(owner_id, org_id, offset, limit)
    
    def get_supplier_types(self) -> List[ProductProviderType]:
        """Get all supplier types"""
        return self.supplier_repo.get_all_supplier_types()
    
    def create_supplier(
        self,
        provider: ProductProvider_API,
        location: Location_API,
        image: Optional[ProviderImage_API] = None
    ) -> ProductProvider:
        """Create a new supplier"""
        
        # Check if supplier already exists
        existing = self.supplier_repo.get_supplier_by_id(provider.id_product_provider, eager_load=False)
        if existing:
            raise APIException(
                status=HTTP_409_CONFLICT,
                code=SUPPLIER_INSERT_FAILED,
                message=f"{SUPPLIER_INSERT_FAILED}: {provider.id_product_provider}"
            )
        
        # Build supplier model
        new_supplier = self._build_supplier_model(provider, location)
        
        # Handle image
        if image and image.provider_image_url:
            provider_image = ProviderImage(provider_image_url=image.provider_image_url)
            new_supplier.provider_image = [provider_image]
        
        # Save to database
        try:
            return self.supplier_repo.create_supplier(new_supplier)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=SUPPLIER_INSERT_FAILED,
                message=SUPPLIER_INSERT_FAILED,
                details=str(e)
            )
    
    def update_supplier(
        self,
        provider: ProductProvider_API,
        image: Optional[ProviderImage_API] = None,
        location: Optional[Location_API] = None
    ) -> ProductProvider:
        """Update an existing supplier"""
        
        # Validate supplier type
        if not self.supplier_repo.get_supplier_type_by_id(provider.id_product_provider_type):
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PRODUCT_CATEGORY_NOT_EXISTS,
                message=PRODUCT_CATEGORY_NOT_EXISTS,
                details=PRODUCT_CATEGORY_NOT_EXISTS
            )
        
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
            return self.supplier_repo.update_supplier(supplier_old)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=SUPPLIER_UPDATE_FAILED,
                message=f"{SUPPLIER_UPDATE_FAILED}: {provider.id_product_provider}",
                details=str(e)
            )
    
    def delete_supplier(self, provider_id: str) -> Dict[str, Any]:
        """Delete a supplier and associated images"""
        
        supplier = self.get_supplier_by_id(provider_id)
        
        # Delete all associated images
        images = self.supplier_repo.get_supplier_images(provider_id)
        for img in images:
            self.supplier_repo.delete_supplier_image(img)
        
        # Delete the supplier
        success = self.supplier_repo.delete_supplier(supplier)
        
        if not success:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=SUPPLIER_DELETE_FAILED,
                details=f"Failed to delete supplier {provider_id}"
            )
        
        return {
            "message": "Supplier deleted successfully",
            "supplier_id": provider_id
        }
    
    def search_suppliers_by_location(
        self,
        longitude: float,
        latitude: float,
        distance_km: float,
        offset: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search suppliers by location"""
        return self.supplier_repo.search_by_location(
            (longitude, latitude), distance_km, offset, limit
        )
    
    def _handle_supplier_image(self, supplier: ProductProvider, image: ProviderImage_API):
        """Handle supplier image creation or update"""
        if image.id_provider_image == 0:
            new_image = ProviderImage(provider_image_url=image.provider_image_url)
            new_image.provider_ref = supplier
            try:
                self.supplier_repo.create_supplier_image(new_image)
            except Exception as e:
                raise APIException(
                    status=HTTP_417_EXPECTATION_FAILED,
                    code=IMAGE_INSERT_FAILED,
                    message=IMAGE_INSERT_FAILED,
                    details=str(e)
                )
        else:
            existing_image = self.supplier_repo.get_supplier_image_by_id(image.id_provider_image)
            if existing_image:
                existing_image.provider_image_url = image.provider_image_url
                try:
                    self.supplier_repo.update_supplier_image(existing_image)
                except Exception as e:
                    raise APIException(
                        status=HTTP_409_CONFLICT,
                        code=IMAGE_UPDATE_FAILED,
                        details=str(e)
                    )

# services/organisation_service.py
from typing import Optional, List, Dict, Any
from core.api_models import ProviderOrganisation_API, OrganisationImage_API
from core.exception_handler import APIException
from core.messages import *
from core.models import ProviderOrganisation, OrganisationImage
from repositories.supplier_repository import OrganisationRepository

class OrganisationService:
    """Service for organisation-related business logic"""
    
    def __init__(self):
        self.org_repo = OrganisationRepository()
    
    def get_org_by_id(self, org_id: str) -> ProviderOrganisation:
        """Get organisation by ID"""
        org = self.org_repo.get_org_by_id(org_id)
        if not org:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=ORGANISAION_NOT_FOUND,
                details=f"Organisation {org_id} not found"
            )
        return org
    
    def get_org_by_name(self, org_name: str) -> Optional[ProviderOrganisation]:
        """Get organisation by name"""
        return self.org_repo.get_org_by_name(org_name)
    
    def get_all_orgs(self, offset: int = 0, limit: int = 100) -> List[ProviderOrganisation]:
        """Get all organisations"""
        return self.org_repo.get_all_orgs(offset, limit)
    
    def create_organisation(
        self,
        org: ProviderOrganisation_API,
        org_image: Optional[OrganisationImage_API] = None
    ) -> ProviderOrganisation:
        """Create a new organisation"""
        
        # Check if organisation name is taken
        existing = self.get_org_by_name(org.provider_organisation_name)
        if existing:
            raise APIException(
                status=HTTP_409_CONFLICT,
                code=ORG_ALREADY_EXISTS,
                message=f"{ORG_ALREADY_EXISTS}: {org.provider_organisation_name}"
            )
        
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
            return self.org_repo.create_org(model_org)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=ORG_INSERT_FAILED,
                details=str(e)
            )
    
    def update_organisation(
        self,
        org: ProviderOrganisation,
        image: Optional[OrganisationImage_API] = None
    ) -> ProviderOrganisation:
        """Update an existing organisation"""
        
        # Get existing organisation
        org_old = self.get_org_by_id(org.id_provider_organisation)
        
        # Check if name is taken (if changed)
        if org_old.provider_organisation_name != org.provider_organisation_name:
            existing = self.get_org_by_name(org.provider_organisation_name)
            if existing:
                raise APIException(
                    status=HTTP_409_CONFLICT,
                    code=ORGANISAION_NAME_USED,
                    details=f"Organisation name '{org.provider_organisation_name}' is already taken"
                )
        
        # Update fields
        org_old.provider_organisation_name = org.provider_organisation_name
        org_old.provider_organisation_desc = org.provider_organisation_desc
        
        # Handle image
        if image and image.org_image_url:
            self._handle_org_image(org_old, image)
        
        # Save changes
        try:
            return self.org_repo.update_org(org_old)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=ORG_UPDATE_FAILED,
                message=f"{ORG_UPDATE_FAILED}: {org.idprovider_organisation}",
                details=str(e)
            )
    
    def delete_organisation(self, org_id: str) -> Dict[str, Any]:
        """Delete an organisation"""
        
        org = self.get_org_by_id(org_id)
        
        # Delete associated images
        images = self.org_repo.get_org_images(org_id)
        for img in images:
            self.org_repo.delete_org_image(img)
        
        # Delete organisation
        success = self.org_repo.delete_org(org)
        
        if not success:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=ORG_DELETE_FAILED,
                details=f"Failed to delete organisation {org_id}"
            )
        
        return {
            "message": "Organisation deleted successfully",
            "organisation_id": org_id
        }
    
    def _handle_org_image(self, organisation: ProviderOrganisation, image: OrganisationImage_API):
        """Handle organisation image creation or update"""
        if image.id_org_image == 0:
            new_image = OrganisationImage(org_image_url=image.org_image_url)
            new_image.org_ref_id = organisation.idprovider_organisation
            try:
                self.org_repo.create_org_image(new_image)
            except Exception as e:
                raise APIException(
                    status=HTTP_417_EXPECTATION_FAILED,
                    code=IMAGE_INSERT_FAILED,
                    message=IMAGE_INSERT_FAILED,
                    details=str(e)
                )
        else:
            existing_image = self.org_repo.get_org_image_by_id(image.id_org_image)
            if existing_image:
                existing_image.org_image_url = image.org_image_url
                try:
                    self.org_repo.update_org_image(existing_image)
                except Exception as e:
                    raise APIException(
                        status=HTTP_409_CONFLICT,
                        code=IMAGE_UPDATE_FAILED,
                        details=str(e)
                    )