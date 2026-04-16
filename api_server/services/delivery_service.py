# services/delivery_service.py
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import BackgroundTasks
from core.api_models import Delivery_API
from core.exception_handler import APIException
from core.messages import *
from core.models import Delivery, Address
from repositories.delivery_repository import DeliveryRepository
from repositories.address_repository import AddressRepository
from services.location_service import LocationService

class DeliveryService:
    """Service for delivery-related business logic"""
    
    # Valid delivery statuses
    VALID_STATUSES = [
        'PENDING', 'PROCESSING', 'READY_FOR_PICKUP', 'IN_TRANSIT',
        'OUT_FOR_DELIVERY', 'DELIVERED', 'FAILED', 'CANCELLED', 'RETURNED'
    ]
    
    # Statuses that cannot be modified
    FROZEN_STATUSES = ['DELIVERED', 'CANCELLED']
    
    def __init__(self):
        self.delivery_repo = DeliveryRepository()
        self.address_repo = AddressRepository()
        self.location_service = LocationService()
    
    def _validate_delivery_data(self, delivery_data: Delivery_API, is_update: bool = False):
        """Validate delivery data before creation or update"""
        
        # Validate weight
        if delivery_data.delivery_total_weight is not None and delivery_data.delivery_total_weight < 0:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_VALIDATION_FAILED,
                details="Delivery weight cannot be negative"
            )
        
        # Validate package count
        if delivery_data.delivery_package_count is not None and delivery_data.delivery_package_count < 0:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_VALIDATION_FAILED,
                details="Package count cannot be negative"
            )
        
        # Validate fee
        if delivery_data.delivery_fee is not None and delivery_data.delivery_fee < 0:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_VALIDATION_FAILED,
                details="Delivery fee cannot be negative"
            )
        
        # Validate status for new deliveries
        if not is_update and delivery_data.delivery_status:
            if delivery_data.delivery_status not in self.VALID_STATUSES:
                raise APIException(
                    status=HTTP_400_BAD_REQUEST,
                    code=DELIVERY_VALIDATION_FAILED,
                    details=f"Invalid delivery status: {delivery_data.delivery_status}"
                )
        
        # Validate recipient information
        has_recipient = (
            (delivery_data.recipient_person and delivery_data.recipient_person != 0) or
            (delivery_data.recipient_provider and delivery_data.recipient_provider != 0) or
            (delivery_data.delivery_placed_order and delivery_data.delivery_placed_order != 0)
        )
        
        if not has_recipient and not is_update:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_VALIDATION_FAILED,
                details="Either recipient person, provider, or order reference is required"
            )
    
    def _validate_status_transition(self, current_status: str, new_status: str):
        """Validate if status transition is allowed"""
        
        if current_status == new_status:
            return True
        
        # Cannot change frozen statuses
        if current_status in self.FROZEN_STATUSES:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_UPDATE_FAILED,
                details=f"Cannot change status of a {current_status.lower()} delivery"
            )
        
        # Validate new status is valid
        if new_status not in self.VALID_STATUSES:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_UPDATE_FAILED,
                details=f"Invalid delivery status: {new_status}"
            )
        
        return True
    
    def _build_delivery_model(self, delivery_data: Delivery_API, existing_delivery: Optional[Delivery] = None) -> Delivery:
        """Build or update a Delivery model from API data"""
        
        if existing_delivery:
            # Update existing delivery
            delivery = existing_delivery
        else:
            # Create new delivery
            delivery = Delivery()
            delivery.delivery_created_at = datetime.now()
        
        # Update basic delivery information
        if delivery_data.delivery_package_count is not None and delivery_data.delivery_package_count != 0:
            delivery.delivery_package_count = str(delivery_data.delivery_package_count)
        
        if delivery_data.delivery_total_weight is not None and delivery_data.delivery_total_weight != 0:
            delivery.delivery_total_weight = float(delivery_data.delivery_total_weight)
        
        if delivery_data.delivery_cargo_dimensions is not None:
            delivery.delivery_cargo_dimensions = delivery_data.delivery_cargo_dimensions
        
        if delivery_data.delivery_goods_description is not None:
            delivery.delivery_goods_description = delivery_data.delivery_goods_description
        
        if delivery_data.hs_code is not None:
            delivery.hs_code = delivery_data.hs_code
        
        if delivery_data.delivery_merchant_name is not None:
            delivery.delivery_merchant_name = delivery_data.delivery_merchant_name
        
        if delivery_data.delivery_shipping_method is not None:
            delivery.delivery_shipping_method = delivery_data.delivery_shipping_method
        
        if delivery_data.delivery_special_instructions is not None:
            delivery.delivery_special_instructions = delivery_data.delivery_special_instructions
        
        if delivery_data.delivery_status is not None:
            if existing_delivery:
                self._validate_status_transition(existing_delivery.delivery_status, delivery_data.delivery_status)
            delivery.delivery_status = delivery_data.delivery_status
        elif not existing_delivery:
            delivery.delivery_status = 'PENDING'
        
        if delivery_data.delivery_fee is not None:
            delivery.delivery_fee = float(delivery_data.delivery_fee)
        
        # Update recipient information
        if delivery_data.recipient_person is not None and delivery_data.recipient_person != 0:
            delivery.recipient_person = delivery_data.recipient_person
        
        if delivery_data.recipient_provider is not None and delivery_data.recipient_provider != 0:
            delivery.recipient_provider = delivery_data.recipient_provider
        
        # Update order reference
        if delivery_data.delivery_placed_order is not None and delivery_data.delivery_placed_order != 0:
            delivery.delivery_placed_order = delivery_data.delivery_placed_order
        
        # Update provider and broker information
        if delivery_data.delivery_provider_id is not None and delivery_data.delivery_provider_id != 0:
            delivery.delivery_provider_id = delivery_data.delivery_provider_id
        
        if delivery_data.delivery_broker_id is not None and delivery_data.delivery_broker_id != 0:
            delivery.delivery_broker_id = delivery_data.delivery_broker_id
        
        # Handle ID if provided
        if delivery_data.id_delivery != 0:
            delivery.id_delivery = delivery_data.id_delivery
        
        # Handle address
        if delivery_data.delivery_address_id is not None and delivery_data.delivery_address_id != 0:
            # Validate address exists
            address = self.address_repo.get_address_by_id(delivery_data.delivery_address_id)
            if address is None:
                raise APIException(
                    status=HTTP_404_NOT_FOUND,
                    code=DELIVERY_UPDATE_FAILED,
                    details=f"Address with ID {delivery_data.delivery_address_id} does not exist"
                )
            delivery.delivery_address_id = delivery_data.delivery_address_id
        elif delivery_data.delivery_address_id == 0 and delivery_data.delivery_address:
            # Create new address from delivery data
            address = self.location_service.build_address_from_delivery(delivery_data)
            created_address = self.address_repo.create_address(address)
            delivery.delivery_address_id = created_address.id_address
        
        # Handle current address (tracking)
        if delivery_data.delivery_current_address_id is not None and delivery_data.delivery_current_address_id != 0:
            current_address = self.address_repo.get_address_by_id(delivery_data.delivery_current_address_id)
            if current_address is None:
                raise APIException(
                    status=HTTP_404_NOT_FOUND,
                    code=DELIVERY_UPDATE_FAILED,
                    details=f"Current address with ID {delivery_data.delivery_current_address_id} does not exist"
                )
            delivery.delivery_current_address_id = delivery_data.delivery_current_address_id
        
        # Update timestamp
        delivery.delivery_updated_at = datetime.now()
        
        return delivery
    
    def get_delivery_by_id(self, delivery_id: int, eager_load: bool = True) -> Delivery:
        """Get delivery by ID"""
        delivery = self.delivery_repo.get_by_id(delivery_id, eager_load)
        if not delivery:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=DELIVERY_NOT_EXISTS,
                message=DELIVERY_NOT_EXISTS,
                details=f"Delivery with ID {delivery_id} does not exist"
            )
        return delivery
    
    def get_all_deliveries(
        self,
        provider_id: int = 0,
        order_id: int = 0,
        broker_id: int = 0,
        offset: int = 0,
        limit: int = 100
    ) -> List[Delivery]:
        """Get all deliveries with filters"""
        return self.delivery_repo.get_all(provider_id, order_id, broker_id, offset, limit)
    
    def get_deliveries_by_status(self, status: str) -> List[Delivery]:
        """Get deliveries by status"""
        if status not in self.VALID_STATUSES:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_VALIDATION_FAILED,
                details=f"Invalid status: {status}"
            )
        return self.delivery_repo.get_by_status(status)
    
    def create_delivery(self, delivery_data: Delivery_API) -> Delivery:
        """Create a new delivery"""
        
        # Validate data
        self._validate_delivery_data(delivery_data, is_update=False)
        
        # Build delivery model
        delivery = self._build_delivery_model(delivery_data)
        
        # Save to database
        try:
            return self.delivery_repo.create(delivery)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=DELIVERY_INSERT_FAILED,
                details=f"Failed to create delivery: {str(e)}"
            )
    
    def update_delivery(
        self,
        delivery_id: int,
        delivery_data: Delivery_API,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Delivery:
        """Update an existing delivery"""
        
        # Get existing delivery
        existing_delivery = self.get_delivery_by_id(delivery_id)
        
        # Validate update data
        self._validate_delivery_data(delivery_data, is_update=True)
        
        # Build updated delivery
        updated_delivery = self._build_delivery_model(delivery_data, existing_delivery)
        
        # Save to database
        try:
            delivery = self.delivery_repo.update(updated_delivery)
            
            # Notify subscribers if background tasks provided
            if background_tasks:
                delivery_dict = self._delivery_to_dict(delivery)
                background_tasks.add_task(self._notify_delivery_subscribers, delivery_id, delivery_dict)
            
            return delivery
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=DELIVERY_UPDATE_FAILED,
                details=f"Failed to update delivery: {str(e)}"
            )
    
    def update_delivery_status(
        self,
        delivery_id: int,
        new_status: str,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Delivery:
        """Update only the delivery status"""
        
        # Create minimal delivery API object
        status_update = Delivery_API(delivery_status=new_status)
        return self.update_delivery(delivery_id, status_update, background_tasks)
    
    def update_delivery_address(
        self,
        delivery_id: int,
        address_id: int,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Delivery:
        """Update only the delivery address"""
        
        # Validate address exists
        address = self.address_repo.get_address_by_id(address_id)
        if address is None:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=DELIVERY_UPDATE_FAILED,
                details=f"Address with ID {address_id} does not exist"
            )
        
        # Create minimal delivery API object
        address_update = Delivery_API(delivery_address_id=address_id)
        return self.update_delivery(delivery_id, address_update, background_tasks)
    
    def update_delivery_tracking(
        self,
        delivery_id: int,
        current_address_id: int,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Delivery:
        """Update the current tracking location of a delivery"""
        
        # Validate current address exists
        current_address = self.address_repo.get_address_by_id(current_address_id)
        if current_address is None:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=DELIVERY_UPDATE_FAILED,
                details=f"Current address with ID {current_address_id} does not exist"
            )
        
        # Create minimal delivery API object
        tracking_update = Delivery_API(delivery_current_address_id=current_address_id)
        return self.update_delivery(delivery_id, tracking_update, background_tasks)
    
    def delete_delivery(self, delivery_id: int) -> Dict[str, Any]:
        """Delete a delivery"""
        
        # Get existing delivery
        existing_delivery = self.get_delivery_by_id(delivery_id)
        
        # Check if delivery can be deleted (only PENDING, CANCELLED, or FAILED)
        if existing_delivery.delivery_status not in ['PENDING', 'CANCELLED', 'FAILED']:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=DELIVERY_DELETE_FAILED,
                message="Cannot delete delivery",
                details=f"Cannot delete delivery with status: {existing_delivery.delivery_status}"
            )
        
        # Delete from database
        success = self.delivery_repo.delete(existing_delivery)
        
        if not success:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=DELIVERY_DELETE_FAILED,
                details=f"Failed to delete delivery {delivery_id}"
            )
        
        return {
            "message": "Delivery deleted successfully",
            "delivery_id": delivery_id
        }
    
    def bulk_delete_deliveries(
        self,
        provider_id: int = 0,
        order_id: int = 0,
        status: str = None
    ) -> Dict[str, Any]:
        """Delete multiple deliveries matching criteria"""
        
        try:
            deleted_count = self.delivery_repo.bulk_delete_by_criteria(provider_id, order_id, status)
            
            return {
                "message": f"Deleted {deleted_count} deliveries",
                "deleted_count": deleted_count
            }
        except Exception as e:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=DELIVERY_BULK_DELETE_FAILED,
                details=f"Failed to delete deliveries: {str(e)}"
            )
    
    def bulk_update_status(
        self,
        delivery_ids: List[int],
        new_status: str,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> List[Delivery]:
        """Update status for multiple deliveries"""
        
        updated_deliveries = []
        failed_deliveries = []
        
        for delivery_id in delivery_ids:
            try:
                updated_delivery = self.update_delivery_status(delivery_id, new_status, background_tasks)
                updated_deliveries.append(updated_delivery)
            except APIException as e:
                failed_deliveries.append({
                    'delivery_id': delivery_id,
                    'error': e.details if e.details else str(e)
                })
        
        if failed_deliveries:
            raise APIException(
                status=HTTP_207_MULTI_STATUS,
                code=DELIVERY_BULK_UPDATE_FAILED,
                details={
                    'successful': len(updated_deliveries),
                    'failed': failed_deliveries
                }
            )
        
        return updated_deliveries
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        stats = {}
        for status in self.VALID_STATUSES:
            stats[status.lower()] = self.delivery_repo.count_by_status(status)
        
        return stats
    
    def _delivery_to_dict(self, delivery: Delivery) -> Dict[str, Any]:
        """Convert delivery to dictionary for notifications"""
        delivery_dict = {}
        for key, value in delivery.__dict__.items():
            if not key.startswith('_'):
                if hasattr(value, 'isoformat'):
                    delivery_dict[key] = value.isoformat()
                else:
                    delivery_dict[key] = value
        return delivery_dict
    
    async def _notify_delivery_subscribers(self, delivery_id: int, data: Dict[str, Any]):
        """Notify subscribers about delivery updates"""
        # This would integrate with your SSE subscriber system
        # Similar to product notifications
        pass