
from typing import Optional, Dict, Any, List
from enum import Enum

from core.messages.error_codes import ErrorCode
from core.messages.error_messages import get_error_message
from core.messages.http_status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_402_PAYMENT_REQUIRED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_410_GONE,
    HTTP_417_EXPECTATION_FAILED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_502_BAD_GATEWAY,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
    HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
)
from core.exceptions.handler import APIException


# ==================== Supplier Exceptions ====================

class SupplierException(APIException):
    """Base exception for all supplier-related errors"""
    
    def __init__(
        self,
        message: str = "Supplier service error",
        error_code: ErrorCode = ErrorCode.SUPPLIER_NOT_EXISTS,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: dict = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


class SupplierNotFoundException(SupplierException):
    """Exception when a supplier is not found"""
    
    def __init__(
        self,
        supplier_id: str = None,
        supplier_name: str = None,
        owner_id: int = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if supplier_id:
            error_details["supplier_id"] = supplier_id
        if supplier_name:
            error_details["supplier_name"] = supplier_name
        if owner_id:
            error_details["owner_id"] = owner_id
        
        message = "Supplier not found"
        if supplier_id:
            message = f"Supplier with ID '{supplier_id}' not found"
        elif supplier_name:
            message = f"Supplier '{supplier_name}' not found"
        elif owner_id:
            message = f"No suppliers found for owner ID '{owner_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SUPPLIER_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class SupplierAlreadyExistsException(SupplierException):
    """Exception when trying to create a duplicate supplier"""
    
    def __init__(
        self,
        supplier_id: str = None,
        supplier_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if supplier_id:
            error_details["supplier_id"] = supplier_id
        if supplier_name:
            error_details["supplier_name"] = supplier_name
        
        message = "Supplier already exists"
        if supplier_id:
            message = f"Supplier with ID '{supplier_id}' already exists"
        elif supplier_name:
            message = f"Supplier '{supplier_name}' already exists"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SUPPLIER_INSERT_FAILED,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class SupplierTypeNotFoundException(SupplierException):
    """Exception when a supplier type is not found"""
    
    def __init__(
        self,
        supplier_type_id: int = None,
        supplier_type_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if supplier_type_id:
            error_details["supplier_type_id"] = supplier_type_id
        if supplier_type_name:
            error_details["supplier_type_name"] = supplier_type_name
        
        message = "Supplier type not found"
        if supplier_type_id:
            message = f"Supplier type with ID '{supplier_type_id}' not found"
        elif supplier_type_name:
            message = f"Supplier type '{supplier_type_name}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SUPPLIER_TYPE_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class SupplierInsertFailedException(SupplierException):
    """Exception when supplier insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        supplier_id: str = None,
        supplier_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if supplier_id:
            error_details["supplier_id"] = supplier_id
        if supplier_name:
            error_details["supplier_name"] = supplier_name
        
        message = "Failed to create supplier"
        if supplier_name:
            message = f"Failed to create supplier '{supplier_name}'"
        elif supplier_id:
            message = f"Failed to create supplier with ID '{supplier_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SUPPLIER_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class SupplierUpdateFailedException(SupplierException):
    """Exception when supplier update fails"""
    
    def __init__(
        self,
        supplier_id: str = None,
        error: str = None,
        fields_attempted: list = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if supplier_id:
            error_details["supplier_id"] = supplier_id
        if error:
            error_details["update_error"] = error
        if fields_attempted:
            error_details["fields_attempted"] = fields_attempted
        
        message = "Failed to update supplier"
        if supplier_id:
            message = f"Failed to update supplier with ID '{supplier_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SUPPLIER_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class SupplierDeleteFailedException(SupplierException):
    """Exception when supplier deletion fails"""
    
    def __init__(
        self,
        supplier_id: str = None,
        error: str = None,
        has_products: bool = False,
        has_images: bool = False,
        details: dict = None
    ):
        error_details = details or {}
        
        if supplier_id:
            error_details["supplier_id"] = supplier_id
        if error:
            error_details["delete_error"] = error
        if has_products:
            error_details["has_products"] = has_products
        if has_images:
            error_details["has_images"] = has_images
        
        message = "Failed to delete supplier"
        if supplier_id:
            message = f"Failed to delete supplier with ID '{supplier_id}'"
        
        if has_products:
            message += " - Supplier has associated products. Use force_delete=true to delete anyway."
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SUPPLIER_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class SupplierImageNotFoundException(SupplierException):
    """Exception when a supplier image is not found"""
    
    def __init__(
        self,
        image_id: int = None,
        supplier_id: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if image_id:
            error_details["image_id"] = image_id
        if supplier_id:
            error_details["supplier_id"] = supplier_id
        
        message = "Supplier image not found"
        if image_id:
            message = f"Supplier image with ID '{image_id}' not found"
        elif supplier_id:
            message = f"Image for supplier '{supplier_id}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.IMAGE_INSERT_FAILED,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


# ==================== Organisation Exceptions ====================

class OrganisationException(SupplierException):
    """Base exception for all organisation-related errors"""
    
    def __init__(
        self,
        message: str = "Organisation service error",
        error_code: ErrorCode = ErrorCode.ORGANISATION_NOT_FOUND,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: dict = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class OrganisationNotFoundException(OrganisationException):
    """Exception when an organisation is not found"""
    
    def __init__(
        self,
        org_id: str = None,
        org_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if org_id:
            error_details["organisation_id"] = org_id
        if org_name:
            error_details["organisation_name"] = org_name
        
        message = "Organisation not found"
        if org_id:
            message = f"Organisation with ID '{org_id}' not found"
        elif org_name:
            message = f"Organisation '{org_name}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORGANISATION_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class OrganisationAlreadyExistsException(OrganisationException):
    """Exception when trying to create a duplicate organisation"""
    
    def __init__(
        self,
        org_id: str = None,
        org_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if org_id:
            error_details["organisation_id"] = org_id
        if org_name:
            error_details["organisation_name"] = org_name
        
        message = "Organisation already exists"
        if org_id:
            message = f"Organisation with ID '{org_id}' already exists"
        elif org_name:
            message = f"Organisation '{org_name}' already exists"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORG_ALREADY_EXISTS,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class OrganisationNameAlreadyUsedException(OrganisationException):
    """Exception when organisation name is already taken"""
    
    def __init__(
        self,
        org_name: str,
        existing_org_id: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        error_details["organisation_name"] = org_name
        if existing_org_id:
            error_details["existing_organisation_id"] = existing_org_id
        
        message = f"Organisation name '{org_name}' is already in use"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORGANISATION_NAME_USED,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class OrganisationInsertFailedException(OrganisationException):
    """Exception when organisation insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        org_id: str = None,
        org_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if org_id:
            error_details["organisation_id"] = org_id
        if org_name:
            error_details["organisation_name"] = org_name
        
        message = "Failed to create organisation"
        if org_name:
            message = f"Failed to create organisation '{org_name}'"
        elif org_id:
            message = f"Failed to create organisation with ID '{org_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORG_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class OrganisationUpdateFailedException(OrganisationException):
    """Exception when organisation update fails"""
    
    def __init__(
        self,
        org_id: str = None,
        error: str = None,
        fields_attempted: list = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if org_id:
            error_details["organisation_id"] = org_id
        if error:
            error_details["update_error"] = error
        if fields_attempted:
            error_details["fields_attempted"] = fields_attempted
        
        message = "Failed to update organisation"
        if org_id:
            message = f"Failed to update organisation with ID '{org_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORG_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class OrganisationDeleteFailedException(OrganisationException):
    """Exception when organisation deletion fails"""
    
    def __init__(
        self,
        org_id: str = None,
        error: str = None,
        has_suppliers: bool = False,
        has_images: bool = False,
        details: dict = None
    ):
        error_details = details or {}
        
        if org_id:
            error_details["organisation_id"] = org_id
        if error:
            error_details["delete_error"] = error
        if has_suppliers:
            error_details["has_suppliers"] = has_suppliers
        if has_images:
            error_details["has_images"] = has_images
        
        message = "Failed to delete organisation"
        if org_id:
            message = f"Failed to delete organisation with ID '{org_id}'"
        
        if has_suppliers:
            message += " - Organisation has associated suppliers. Use force_delete=true to delete anyway."
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORG_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class OrganisationImageNotFoundException(OrganisationException):
    """Exception when an organisation image is not found"""
    
    def __init__(
        self,
        image_id: int = None,
        org_id: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if image_id:
            error_details["image_id"] = image_id
        if org_id:
            error_details["organisation_id"] = org_id
        
        message = "Organisation image not found"
        if image_id:
            message = f"Organisation image with ID '{image_id}' not found"
        elif org_id:
            message = f"Image for organisation '{org_id}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.IMAGE_INSERT_FAILED,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


# ==================== Image Exceptions ====================

class ImageException(SupplierException):
    """Base exception for image-related errors"""
    
    def __init__(
        self,
        message: str = "Image operation failed",
        error_code: ErrorCode = ErrorCode.IMAGE_INSERT_FAILED,
        status_code: int = HTTP_417_EXPECTATION_FAILED,
        details: dict = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class ImageInsertFailedException(ImageException):
    """Exception when image insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        image_url: str = None,
        supplier_id: str = None,
        organisation_id: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if image_url:
            error_details["image_url"] = image_url[:100]  # Truncate long URLs
        if supplier_id:
            error_details["supplier_id"] = supplier_id
        if organisation_id:
            error_details["organisation_id"] = organisation_id
        
        message = "Failed to upload image"
        if supplier_id:
            message = f"Failed to upload image for supplier '{supplier_id}'"
        elif organisation_id:
            message = f"Failed to upload image for organisation '{organisation_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.IMAGE_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class ImageUpdateFailedException(ImageException):
    """Exception when image update fails"""
    
    def __init__(
        self,
        image_id: int = None,
        error: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if image_id:
            error_details["image_id"] = image_id
        if error:
            error_details["update_error"] = error
        
        message = "Failed to update image"
        if image_id:
            message = f"Failed to update image with ID '{image_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.IMAGE_UPDATE_FAILED,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class ImageDeleteFailedException(ImageException):
    """Exception when image deletion fails"""
    
    def __init__(
        self,
        image_id: int = None,
        error: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if image_id:
            error_details["image_id"] = image_id
        if error:
            error_details["delete_error"] = error
        
        message = "Failed to delete image"
        if image_id:
            message = f"Failed to delete image with ID '{image_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.IMAGE_INSERT_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


# ==================== Location Search Exceptions ====================

class LocationSearchException(SupplierException):
    """Exception for location-based search errors"""
    
    def __init__(
        self,
        message: str = "Location search failed",
        longitude: float = None,
        latitude: float = None,
        distance_km: float = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if longitude:
            error_details["longitude"] = longitude
        if latitude:
            error_details["latitude"] = latitude
        if distance_km:
            error_details["distance_km"] = distance_km
        
        message = "Location search failed"
        if longitude and latitude:
            message = f"Location search failed for coordinates ({longitude}, {latitude})"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.LOCATION_NOT_FOUND,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class InvalidCoordinatesException(LocationSearchException):
    """Exception for invalid geographic coordinates"""
    
    def __init__(
        self,
        longitude: float = None,
        latitude: float = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if longitude:
            error_details["longitude"] = longitude
        if latitude:
            error_details["latitude"] = latitude
        
        message = "Invalid coordinates provided"
        if longitude is not None and (longitude < -180 or longitude > 180):
            message = f"Longitude must be between -180 and 180, got {longitude}"
        elif latitude is not None and (latitude < -90 or latitude > 90):
            message = f"Latitude must be between -90 and 90, got {latitude}"
        
        super().__init__(
            message=message,
            longitude=longitude,
            latitude=latitude,
            details=error_details
        )



