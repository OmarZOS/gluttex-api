# services/delivery_service.py
"""
Delivery service for managing deliveries, tracking, and status updates.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import BackgroundTasks
import logging

from core.api_models import Delivery_API
from core.exceptions.specific.delivery_exceptions import (
    DeliveryNotFoundException,
    DeliveryCreationFailedException,
    DeliveryUpdateFailedException,
    DeliveryDeleteFailedException,
    DeliveryValidationFailedException,
    DeliveryCannotBeUpdatedException,
    DeliveryBulkUpdateFailedException,
    DeliveryBulkDeleteFailedException,
    DeliveryStatusInvalidException,
    AddressNotFoundException,
    DeliveryAlreadyDeliveredException
)
from core.models import Delivery
from repositories.delivery_repository import DeliveryRepository
from repositories.address_repository import AddressRepository
from services.location_service import LocationService

logger = logging.getLogger(__name__)


class DeliveryService:
    """Service for delivery-related business logic"""
    
    # Valid delivery statuses
    VALID_STATUSES = [
        'PENDING', 'PROCESSING', 'READY_FOR_PICKUP', 'IN_TRANSIT',
        'OUT_FOR_DELIVERY', 'DELIVERED', 'FAILED', 'CANCELLED', 'RETURNED'
    ]
    
    # Statuses that cannot be modified
    FROZEN_STATUSES = ['DELIVERED', 'CANCELLED']
    
    # Status transitions that are allowed
    ALLOWED_TRANSITIONS = {
        'PENDING': ['PROCESSING', 'CANCELLED'],
        'PROCESSING': ['READY_FOR_PICKUP', 'CANCELLED'],
        'READY_FOR_PICKUP': ['IN_TRANSIT', 'CANCELLED'],
        'IN_TRANSIT': ['OUT_FOR_DELIVERY', 'FAILED', 'RETURNED'],
        'OUT_FOR_DELIVERY': ['DELIVERED', 'FAILED', 'RETURNED'],
        'FAILED': ['PENDING', 'CANCELLED'],
        'RETURNED': ['PENDING', 'PROCESSING'],
        'DELIVERED': [],
        'CANCELLED': []
    }
    
    def __init__(self):
        self.delivery_repo = DeliveryRepository()
        self.address_repo = AddressRepository()
        self.location_service = LocationService()
    
    # ==================== Private Helper Methods ====================
    
    def _validate_delivery_data(self, delivery_data: Delivery_API, is_update: bool = False):
        """Validate delivery data before creation or update"""
        
        # Validate weight
        if delivery_data.delivery_total_weight is not None and delivery_data.delivery_total_weight < 0:
            raise DeliveryValidationFailedException(
                field="delivery_total_weight",
                value=delivery_data.delivery_total_weight,
                reason="Delivery weight cannot be negative"
            )
        
        # Validate package count
        if delivery_data.delivery_package_count is not None and delivery_data.delivery_package_count < 0:
            raise DeliveryValidationFailedException(
                field="delivery_package_count",
                value=delivery_data.delivery_package_count,
                reason="Package count cannot be negative"
            )
        
        # Validate fee
        if delivery_data.delivery_fee is not None and delivery_data.delivery_fee < 0:
            raise DeliveryValidationFailedException(
                field="delivery_fee",
                value=delivery_data.delivery_fee,
                reason="Delivery fee cannot be negative"
            )
        
        # Validate status for new deliveries
        if not is_update and delivery_data.delivery_status:
            if delivery_data.delivery_status not in self.VALID_STATUSES:
                raise DeliveryStatusInvalidException(
                    requested_status=delivery_data.delivery_status,
                    allowed_statuses=self.VALID_STATUSES
                )
        
        # Validate recipient information
        has_recipient = (
            (delivery_data.recipient_person and delivery_data.recipient_person != 0) or
            (delivery_data.recipient_provider and delivery_data.recipient_provider != 0) or
            (delivery_data.delivery_placed_order and delivery_data.delivery_placed_order != 0)
        )
        
        if not has_recipient and not is_update:
            raise DeliveryValidationFailedException(
                field="recipient",
                reason="Either recipient person, provider, or order reference is required"
            )
    
    def _validate_status_transition(self, current_status: str, new_status: str):
        """Validate if status transition is allowed"""
        
        if current_status == new_status:
            return True
        
        # Cannot change frozen statuses
        if current_status in self.FROZEN_STATUSES:
            raise DeliveryCannotBeUpdatedException(
                delivery_id=None,  # Will be set by caller
                current_status=current_status,
                attempted_action=f"change status to {new_status}",
                allowed_actions=["view"]
            )
        
        # Check if transition is allowed
        allowed = self.ALLOWED_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise DeliveryStatusInvalidException(
                current_status=current_status,
                requested_status=new_status,
                allowed_statuses=allowed
            )
        
        # Check if delivery is already delivered
        if current_status == 'DELIVERED':
            raise DeliveryAlreadyDeliveredException(
                delivery_id=None,  # Will be set by caller
                action="update status"
            )
        
        return True
    
    def _build_delivery_model(self, delivery_data: Delivery_API, existing_delivery: Optional[Delivery] = None) -> Delivery:
        """Build or update a Delivery model from API data"""
        
        if existing_delivery:
            # Update existing delivery
            delivery = existing_delivery
            logger.debug(f"Updating existing delivery {delivery.id_delivery}")
        else:
            # Create new delivery
            delivery = Delivery()
            delivery.delivery_created_at = datetime.now()
            logger.debug("Creating new delivery")
        
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
        
        # Handle ID if provided (for new deliveries, keep id_delivery as None/0)
        # For new deliveries, don't set id_delivery at all (let DB auto-generate)
        # For updates, only set if it's provided and non-zero
        if existing_delivery and delivery_data.id_delivery != 0:
            delivery.id_delivery = delivery_data.id_delivery
        elif not existing_delivery:
            # For new deliveries, id_delivery should be None (will be set by DB)
            # But we need to handle the test expectation of 0
            if delivery_data.id_delivery != 0:
                delivery.id_delivery = delivery_data.id_delivery
            # Otherwise leave as None (the test expects 0, but that's inconsistent with DB auto-increment)
            # Let's explicitly set to None for new deliveries without an ID
        
        # Handle address
        if delivery_data.delivery_address_id is not None and delivery_data.delivery_address_id != 0:
            # Validate address exists
            address = self.address_repo.get_address_by_id(delivery_data.delivery_address_id)
            if address is None:
                raise AddressNotFoundException(address_id=delivery_data.delivery_address_id)
            delivery.delivery_address_id = delivery_data.delivery_address_id
        elif delivery_data.delivery_address_id == 0:
            # Create new address from delivery data
            address = self.location_service.build_address_from_delivery(delivery_data)
            created_address = self.address_repo.create_address(address)
            delivery.delivery_address_id = created_address.id_address
            logger.debug(f"Created new address {created_address.id_address} for delivery")
        
        # Handle current address (tracking)
        if delivery_data.delivery_current_address_id is not None and delivery_data.delivery_current_address_id != 0:
            current_address = self.address_repo.get_address_by_id(delivery_data.delivery_current_address_id)
            if current_address is None:
                raise AddressNotFoundException(address_id=delivery_data.delivery_current_address_id)
            delivery.delivery_current_address_id = delivery_data.delivery_current_address_id
    
        # Update timestamp
        delivery.delivery_updated_at = datetime.now()
        
        return delivery

    # ==================== CRUD Operations ====================
    
    def get_delivery_by_id(self, delivery_id: int, eager_load: bool = True) -> Delivery:
        """
        Get delivery by ID.
        
        Args:
            delivery_id: Delivery ID to retrieve
            eager_load: Whether to load related data eagerly
            
        Returns:
            Delivery object
            
        Raises:
            DeliveryNotFoundException: If delivery not found
        """
        delivery = self.delivery_repo.get_by_id(delivery_id, eager_load)
        if not delivery:
            logger.warning(f"Delivery not found with ID: {delivery_id}")
            raise DeliveryNotFoundException(delivery_id=delivery_id)
        
        logger.debug(f"Retrieved delivery with ID: {delivery_id}")
        return delivery
    
    def get_all_deliveries(
        self,
        provider_id: int = 0,
        order_id: int = 0,
        broker_id: int = 0,
        offset: int = 0,
        limit: int = 100
    ) -> List[Delivery]:
        """
        Get all deliveries with filters.
        
        Args:
            provider_id: Filter by provider ID
            order_id: Filter by order ID
            broker_id: Filter by broker ID
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of Delivery objects
        """
        logger.debug(f"Fetching deliveries - provider:{provider_id}, order:{order_id}, broker:{broker_id}, offset:{offset}, limit:{limit}")
        return self.delivery_repo.get_all(provider_id, order_id, broker_id, offset, limit)
    
    def get_deliveries_by_status(self, status: str) -> List[Delivery]:
        """
        Get deliveries by status.
        
        Args:
            status: Delivery status to filter by
            
        Returns:
            List of Delivery objects
            
        Raises:
            DeliveryStatusInvalidException: If status is invalid
        """
        if status not in self.VALID_STATUSES:
            logger.warning(f"Invalid status requested: {status}")
            raise DeliveryStatusInvalidException(
                requested_status=status,
                allowed_statuses=self.VALID_STATUSES
            )
        
        logger.debug(f"Fetching deliveries with status: {status}")
        return self.delivery_repo.get_by_status(status)
    
    def create_delivery(self, delivery_data: Delivery_API) -> Delivery:
        """
        Create a new delivery.
        
        Args:
            delivery_data: Delivery data to create
            
        Returns:
            Created Delivery object
            
        Raises:
            DeliveryValidationFailedException: If validation fails
            DeliveryCreationFailedException: If creation fails
        """
        logger.info(f"Creating new delivery for order: {delivery_data.delivery_placed_order}")
        
        # Validate data
        self._validate_delivery_data(delivery_data, is_update=False)
        
        # Build delivery model
        delivery = self._build_delivery_model(delivery_data)
        
        # Save to database
        try:
            result = self.delivery_repo.create(delivery)
            logger.info(f"Delivery created successfully with ID: {result.id_delivery}")
            return result
        except Exception as e:
            logger.error(f"Failed to create delivery: {e}")
            raise DeliveryCreationFailedException(
                error=str(e),
                order_id=delivery_data.delivery_placed_order,
                provider_id=delivery_data.delivery_provider_id
            )
    
    def update_delivery(
        self,
        delivery_id: int,
        delivery_data: Delivery_API,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Delivery:
        """
        Update an existing delivery.
        
        Args:
            delivery_id: Delivery ID to update
            delivery_data: Updated delivery data
            background_tasks: Optional background tasks for notifications
            
        Returns:
            Updated Delivery object
            
        Raises:
            DeliveryNotFoundException: If delivery not found
            DeliveryValidationFailedException: If validation fails
            DeliveryUpdateFailedException: If update fails
        """
        logger.info(f"Updating delivery with ID: {delivery_id}")
        
        # Get existing delivery
        existing_delivery = self.get_delivery_by_id(delivery_id)
        
        # Validate update data
        self._validate_delivery_data(delivery_data, is_update=True)
        
        # Build updated delivery
        updated_delivery = self._build_delivery_model(delivery_data, existing_delivery)
        
        # Save to database
        try:
            delivery = self.delivery_repo.update(updated_delivery)
            logger.info(f"Delivery {delivery_id} updated successfully")
            
            # Notify subscribers if background tasks provided
            if background_tasks:
                delivery_dict = self._delivery_to_dict(delivery)
                background_tasks.add_task(self._notify_delivery_subscribers, delivery_id, delivery_dict)
            
            return delivery
        except Exception as e:
            logger.error(f"Failed to update delivery {delivery_id}: {e}")
            raise DeliveryUpdateFailedException(
                delivery_id=delivery_id,
                error=str(e)
            )
    
    def update_delivery_status(
        self,
        delivery_id: int,
        new_status: str,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Delivery:
        """
        Update only the delivery status.
        
        Args:
            delivery_id: Delivery ID to update
            new_status: New status value
            background_tasks: Optional background tasks for notifications
            
        Returns:
            Updated Delivery object
            
        Raises:
            DeliveryNotFoundException: If delivery not found
            DeliveryStatusInvalidException: If status transition invalid
        """
        logger.info(f"Updating status for delivery {delivery_id} to '{new_status}'")
        
        # Create minimal delivery API object
        status_update = Delivery_API(delivery_status=new_status)
        
        try:
            return self.update_delivery(delivery_id, status_update, background_tasks)
        except DeliveryCannotBeUpdatedException:
            raise
        except DeliveryStatusInvalidException:
            raise
        except DeliveryNotFoundException:
            raise
    
    def update_delivery_address(
        self,
        delivery_id: int,
        address_id: int,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Delivery:
        """
        Update only the delivery address.
        
        Args:
            delivery_id: Delivery ID to update
            address_id: New address ID
            background_tasks: Optional background tasks for notifications
            
        Returns:
            Updated Delivery object
        """
        logger.info(f"Updating address for delivery {delivery_id} to address {address_id}")
        
        # Validate address exists
        address = self.address_repo.get_address_by_id(address_id)
        if address is None:
            logger.warning(f"Address not found with ID: {address_id}")
            raise AddressNotFoundException(address_id=address_id)
        
        # Create minimal delivery API object
        address_update = Delivery_API(delivery_address_id=address_id)
        return self.update_delivery(delivery_id, address_update, background_tasks)
    
    def update_delivery_tracking(
        self,
        delivery_id: int,
        current_address_id: int,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Delivery:
        """
        Update the current tracking location of a delivery.
        
        Args:
            delivery_id: Delivery ID to update
            current_address_id: Current tracking address ID
            background_tasks: Optional background tasks for notifications
            
        Returns:
            Updated Delivery object
        """
        logger.info(f"Updating tracking for delivery {delivery_id} to address {current_address_id}")
        
        # Validate current address exists
        current_address = self.address_repo.get_address_by_id(current_address_id)
        if current_address is None:
            logger.warning(f"Current address not found with ID: {current_address_id}")
            raise AddressNotFoundException(address_id=current_address_id)
        
        # Create minimal delivery API object
        tracking_update = Delivery_API(delivery_current_address_id=current_address_id)
        return self.update_delivery(delivery_id, tracking_update, background_tasks)
    
    def delete_delivery(self, delivery_id: int) -> Dict[str, Any]:
        """
        Delete a delivery.
        
        Args:
            delivery_id: Delivery ID to delete
            
        Returns:
            Dictionary with success message
            
        Raises:
            DeliveryNotFoundException: If delivery not found
            DeliveryDeleteFailedException: If deletion fails
        """
        logger.info(f"Deleting delivery with ID: {delivery_id}")
        
        # Get existing delivery
        existing_delivery = self.get_delivery_by_id(delivery_id)
        
        # Check if delivery can be deleted (only PENDING, CANCELLED, or FAILED)
        if existing_delivery.delivery_status not in ['PENDING', 'CANCELLED', 'FAILED']:
            logger.warning(f"Cannot delete delivery {delivery_id} with status: {existing_delivery.delivery_status}")
            raise DeliveryDeleteFailedException(
                delivery_id=delivery_id,
                error=f"Cannot delete delivery with status: {existing_delivery.delivery_status}"
            )
        
        # Delete from database
        success = self.delivery_repo.delete(existing_delivery)
        
        if not success:
            logger.error(f"Failed to delete delivery {delivery_id}")
            raise DeliveryDeleteFailedException(
                delivery_id=delivery_id,
                error="Repository returned False"
            )
        
        logger.info(f"Delivery {delivery_id} deleted successfully")
        return {
            "success": True,
            "message": "Delivery deleted successfully",
            "delivery_id": delivery_id
        }
    
    # ==================== Bulk Operations ====================
    
    def bulk_delete_deliveries(
        self,
        provider_id: int = 0,
        order_id: int = 0,
        status: str = None,
        force_delete: bool = False
    ) -> Dict[str, Any]:
        """
        Delete multiple deliveries matching criteria.
        
        Args:
            provider_id: Filter by provider ID
            order_id: Filter by order ID
            status: Filter by status
            force_delete: Force delete even if deliveries are in transit
            
        Returns:
            Dictionary with deletion statistics
            
        Raises:
            DeliveryBulkDeleteFailedException: If bulk deletion fails
        """
        logger.info(f"Bulk deleting deliveries - provider:{provider_id}, order:{order_id}, status:{status}, force:{force_delete}")
        
        try:
            deleted_count = self.delivery_repo.bulk_delete_by_criteria(
                provider_id, order_id, status, force_delete
            )
            
            logger.info(f"Bulk deleted {deleted_count} deliveries")
            return {
                "success": True,
                "message": f"Deleted {deleted_count} deliveries",
                "deleted_count": deleted_count,
                "filters": {
                    "provider_id": provider_id if provider_id > 0 else None,
                    "order_id": order_id if order_id > 0 else None,
                    "status": status,
                    "force_delete": force_delete
                }
            }
        except Exception as e:
            logger.error(f"Failed to bulk delete deliveries: {e}")
            # Pass the error in the details parameter
            raise DeliveryBulkDeleteFailedException(
                provider_id=provider_id if provider_id > 0 else None,
                order_id=order_id if order_id > 0 else None,
                status=status,
                details={
                    "error": str(e),
                    "force_delete": force_delete
                }
            )


    
    def bulk_update_status(
        self,
        delivery_ids: List[int],
        new_status: str,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> List[Delivery]:
        """
        Update status for multiple deliveries.
        
        Args:
            delivery_ids: List of delivery IDs to update
            new_status: New status value
            background_tasks: Optional background tasks for notifications
            
        Returns:
            List of updated Delivery objects
            
        Raises:
            DeliveryBulkUpdateFailedException: If some updates fail
            DeliveryStatusInvalidException: If status is invalid
        """
        logger.info(f"Bulk updating status for {len(delivery_ids)} deliveries to '{new_status}'")
        
        # Validate status first
        if new_status not in self.VALID_STATUSES:
            raise DeliveryStatusInvalidException(
                requested_status=new_status,
                allowed_statuses=self.VALID_STATUSES
            )
        
        updated_deliveries = []
        failed_deliveries = []
        
        for delivery_id in delivery_ids:
            try:
                updated_delivery = self.update_delivery_status(delivery_id, new_status, background_tasks)
                updated_deliveries.append(updated_delivery)
            except Exception as e:
                logger.error(f"Failed to update delivery {delivery_id}: {e}")
                failed_deliveries.append({
                    'delivery_id': delivery_id,
                    'error': str(e)
                })
        
        if failed_deliveries:
            logger.warning(f"Bulk update completed with {len(updated_deliveries)} successes and {len(failed_deliveries)} failures")
            raise DeliveryBulkUpdateFailedException(
                delivery_ids=delivery_ids,
                target_status=new_status,
                success_count=len(updated_deliveries),
                failed_count=len(failed_deliveries),
                failed_ids=[f['delivery_id'] for f in failed_deliveries],
                errors=failed_deliveries
            )
        
        logger.info(f"Successfully updated status for {len(updated_deliveries)} deliveries")
        return updated_deliveries
    
    # ==================== Statistics ====================
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """
        Get delivery statistics.
        
        Returns:
            Dictionary with counts per status
        """
        logger.debug("Fetching delivery statistics")
        
        stats = {
            "total": 0,
            "by_status": {}
        }
        
        for status in self.VALID_STATUSES:
            count = self.delivery_repo.count_by_status(status)
            stats["by_status"][status.lower()] = count
            stats["total"] += count
        
        logger.debug(f"Delivery stats: {stats['total']} total deliveries")
        return stats
    
    # ==================== Helper Methods ====================
    
    def _delivery_to_dict(self, delivery: Delivery) -> Dict[str, Any]:
        """
        Convert delivery to dictionary for notifications.
        
        Args:
            delivery: Delivery object to convert
            
        Returns:
            Dictionary representation of delivery
        """
        delivery_dict = {}
        for key, value in delivery.__dict__.items():
            if not key.startswith('_'):
                if hasattr(value, 'isoformat'):
                    delivery_dict[key] = value.isoformat()
                elif hasattr(value, 'id'):
                    delivery_dict[key] = value.id
                else:
                    delivery_dict[key] = value
        return delivery_dict
    
    async def _notify_delivery_subscribers(self, delivery_id: int, data: Dict[str, Any]):
        """
        Notify subscribers about delivery updates.
        
        Args:
            delivery_id: Delivery ID that was updated
            data: Update data to send
        """
        # This would integrate with your SSE subscriber system
        # Similar to product notifications
        logger.debug(f"Notifying subscribers for delivery {delivery_id}")
        # Implementation depends on your notification system
        pass