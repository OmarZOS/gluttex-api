"""
CRUD operations for organisations.
"""

import logging
from typing import Optional, List, Dict, Any

from core.models.api_models import ProviderOrganisation_API, OrganisationImage_API
from core.models.models import OrganisationImage, ProviderOrganisation
from core.exceptions.specific.supplier_exceptions import (
    OrganisationInsertFailedException,
    OrganisationUpdateFailedException,
    OrganisationDeleteFailedException
)
from repositories.supplier_repository import OrganisationRepository
from .organisation_validator import OrganisationValidator
from .organisation_image import OrganisationImageHandler

logger = logging.getLogger(__name__)


class OrganisationCrud:
    """CRUD operations for organisations"""
    
    def __init__(self):
        self.org_repo = OrganisationRepository()
        self.validator = OrganisationValidator()
        self.image_handler = OrganisationImageHandler()
    
    def get_by_id(self, org_id: str) -> ProviderOrganisation:
        """
        Get organisation by ID.
        
        Args:
            org_id: Organisation ID to retrieve
            
        Returns:
            ProviderOrganisation object
            
        Raises:
            OrganisationNotFoundException: If organisation not found
        """
        return self.validator.validate_org_exists(org_id)
    
    def get_by_name(self, org_name: str) -> Optional[ProviderOrganisation]:
        """
        Get organisation by name.
        
        Args:
            org_name: Organisation name to search for
            
        Returns:
            ProviderOrganisation object or None if not found
        """
        return self.org_repo.get_org_by_name(org_name)
    
    def get_all(self, offset: int = 0, limit: int = 100) -> List[ProviderOrganisation]:
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
    
    def create(
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
            OrganisationNameAlreadyUsedException: If organisation name is taken
            OrganisationInsertFailedException: If creation fails
        """
        logger.info(f"Creating new organisation: {org.provider_organisation_name}")
        
        # Validate name is unique
        self.validator.validate_org_name_unique(org.provider_organisation_name)
        
        # Build organisation model
        model_org = ProviderOrganisation(
            app_user_id=org.app_user_id,
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
    
    def update(
        self,
        organisation: ProviderOrganisation_API,
        image: Optional[OrganisationImage_API] = None
    ) -> ProviderOrganisation:
        """
        Update an existing organisation.
        
        Args:
            organisation: Updated organisation details
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
        org_old = self.validator.validate_org_exists(organisation.id_provider_organisation)
        
        # Validate ownership
        self.validator.validate_ownership(org_old, organisation.app_user_id)
        
        # Check if name is unique (if changed)
        if org_old.provider_organisation_name != organisation.provider_organisation_name:
            self.validator.validate_org_name_unique(
                organisation.provider_organisation_name,
                exclude_org_id=organisation.id_provider_organisation
            )
        
        # Update fields
        org_old.provider_organisation_name = organisation.provider_organisation_name
        org_old.provider_organisation_desc = organisation.provider_organisation_desc
        
        # Handle image
        self.image_handler.handle_image(org_old, image)
        
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
    
    def delete(self, org_id: str, user_id: int) -> Dict[str, Any]:
        """
        Delete an organisation and associated images.
        
        Args:
            org_id: Organisation ID to delete
            user_id: User ID for ownership validation
            
        Returns:
            Dictionary with success message
            
        Raises:
            OrganisationNotFoundException: If organisation not found
            OrganisationDeleteFailedException: If deletion fails
        """
        logger.info(f"Deleting organisation with ID: {org_id}")
        
        # Validate
        org = self.validator.validate_org_exists(org_id)
        self.validator.validate_ownership(org, user_id)
        
        # Delete images
        self.image_handler.delete_images(org_id)
        
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