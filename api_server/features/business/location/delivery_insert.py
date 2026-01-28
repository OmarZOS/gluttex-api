
# schema translations for Location

from features.business.location.location_fetch import build_address_from_delivery
from storage import storage_broker
from core.exception_handler import APIException
from core.messages import *
from core.api_models import Delivery_API, Location_API
from core.models import Address, Delivery
from features.insertion import insert_or_complete_or_raise, update_record_in_api


# Constants for error codes (define these in your constants module)
DELIVERY_INSERT_FAILED = "DELIVERY_INSERT_FAILED"

def build_delivery(delivery_data: Delivery_API) -> Delivery:
    """
    Build a Delivery ORM object from a Delivery_API schema.
    Validates required fields and builds the delivery object.
    """
    
    
    
    
    
    # Build the delivery object
    delivery = Delivery(
        # Package details
        delivery_package_count=str(delivery_data.delivery_package_count) if delivery_data.delivery_package_count else None,
        delivery_total_weight=float(str(delivery_data.delivery_total_weight)) if delivery_data.delivery_total_weight else None,
        delivery_cargo_dimensions=delivery_data.delivery_cargo_dimensions,
        delivery_goods_description=delivery_data.delivery_goods_description,
        # Shipping information
        # hs_code=delivery_data.hs_code,
        delivery_merchant_name=delivery_data.delivery_merchant_name,
        delivery_shipping_method=delivery_data.delivery_shipping_method,
        delivery_special_instructions=delivery_data.delivery_special_instructions,        
        # Financial and operational
        delivery_fee=float(delivery_data.delivery_fee) if delivery_data.delivery_fee else 0.0,
        # Status (default to PENDING if not provided)
        delivery_status=delivery_data.delivery_status or 'PENDING',
    )

    if delivery_data.delivery_provider_id != 0:
        delivery.delivery_provider_id=delivery_data.delivery_provider_id
    if delivery_data.delivery_broker_id != 0:
        delivery.delivery_broker_id=delivery_data.delivery_broker_id

    if delivery_data.hs_code != "":
        delivery.hs_code = delivery_data.hs_code
    if delivery_data.id_delivery != 0:
        delivery.id_delivery = delivery_data.id_delivery
    if delivery_data.recipient_person != 0:
        delivery.recipient_person = delivery_data.recipient_person
    if delivery_data.recipient_provider != 0:
        delivery.recipient_provider = delivery_data.recipient_provider
    if delivery_data.delivery_package_count != 0:
        delivery.delivery_package_count = delivery_data.delivery_package_count
    if delivery_data.delivery_current_address_id != 0:
        delivery.delivery_current_address_id = delivery_data.delivery_current_address_id
    if delivery_data.delivery_placed_order != 0:
        delivery.delivery_placed_order = delivery_data.delivery_placed_order
    if delivery_data.delivery_provider_id != 0:
        delivery.delivery_provider_id = delivery_data.delivery_provider_id
    if delivery_data.delivery_broker_id != 0:
        delivery.delivery_broker_id = delivery_data.delivery_broker_id
    
    if delivery_data.delivery_address_id != 0:
        delivery.delivery_address_id = delivery_data.delivery_address_id
    else:
        delivery.delivery = build_address_from_delivery(delivery_data)

    return delivery

def insert_delivery(delivery_data: Delivery_API) -> Delivery:
    """
    Insert a new Delivery into the database or raise a controlled API exception.
    """
    try:
        # Build the delivery object
        delivery = build_delivery(delivery_data)
        
        return insert_or_complete_or_raise(delivery)
        
    except APIException:  # already wrapped from build_delivery
        raise
    except ValueError as e:
        # Handle type conversion errors (e.g., Decimal conversion)
        raise APIException(
            status=HTTP_400_BAD_REQUEST,
            code=DELIVERY_INSERT_FAILED,
            details=f"Invalid data format: {str(e)}"
        )
    except Exception as e:
        raise APIException(
            status=INTERNAL_SERVER_ERROR,
            code=DELIVERY_INSERT_FAILED,
            details=f"Failed to create delivery: {str(e)}"
        )

# Helper function if you need to create delivery with address (similar to location pattern)
def build_delivery_with_address(delivery_data: Delivery_API, address: Address) -> Delivery:
    """
    Build a Delivery with an Address object (instead of address_id).
    Useful when you have an Address object ready.
    """
    if not address.id_address:
        raise APIException(
            status=HTTP_400_BAD_REQUEST,
            code=DELIVERY_INSERT_FAILED,
            details="Address must be saved to database first"
        )
    
    # Update delivery data with the address ID
    delivery_data.delivery_address_id = address.id_address
    delivery_data.delivery_current_address_id = delivery_data.delivery_current_address_id or address.id_address
    
    return build_delivery(delivery_data)

# If you need a more comprehensive delivery builder with validation
def validate_and_build_delivery(delivery_data: Delivery_API, db_session) -> Delivery:
    """
    Validate delivery data and build delivery object with additional checks.
    """
    # Additional validation logic can go here
    if delivery_data.delivery_total_weight and delivery_data.delivery_total_weight < 0:
        raise APIException(
            status=HTTP_400_BAD_REQUEST,
            code=DELIVERY_INSERT_FAILED,
            details="Delivery weight cannot be negative"
        )
    
    if delivery_data.delivery_fee and delivery_data.delivery_fee < 0:
        raise APIException(
            status=HTTP_400_BAD_REQUEST,
            code=DELIVERY_INSERT_FAILED,
            details="Delivery fee cannot be negative"
        )
    
    # Check if address exists in database
    if delivery_data.delivery_address_id:
        address_exists = db_session.query(Address).filter(
            Address.id_address == delivery_data.delivery_address_id
        ).first()
        if not address_exists:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_INSERT_FAILED,
                details=f"Address with ID {delivery_data.delivery_address_id} does not exist"
            )
    
    # Check if current address exists (if different from delivery address)
    if (delivery_data.delivery_current_address_id and 
        delivery_data.delivery_current_address_id != delivery_data.delivery_address_id):
        current_address_exists = db_session.query(Address).filter(
            Address.id_address == delivery_data.delivery_current_address_id
        ).first()
        if not current_address_exists:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_INSERT_FAILED,
                details=f"Current address with ID {delivery_data.delivery_current_address_id} does not exist"
            )
    
    return build_delivery(delivery_data)



