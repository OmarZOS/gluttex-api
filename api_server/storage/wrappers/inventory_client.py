


from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

from constants import SILO_SERVER_URL
from core.models.inventory_models import AvailableQuantityResponse, BulkInventoryRequest, BulkOperationResponse, CheckAndReserveResponse, ConfirmRequest, InventoryOperationResponse, ReleaseRequest, ReserveRequest, StockStatusResponse
from core.models.finance_models import DailyPaymentStats, InvoicePaymentSummary, PaymentCreate, PaymentRefund, PaymentResponse

from communication.communication_broker import (
    send_post_request,
    send_get_request,
    send_put_request,
    send_delete_request
)
import logging

logger = logging.getLogger(__name__)

class InventoryServiceClient:
    """Client for Inventory API"""
    
    base_url = SILO_SERVER_URL
    timeout = 30
    
    async def reserve_inventory(self, items: List[Dict], item_type: str = 'ordered_item') -> Dict:
        """
        Reserve inventory for ordered items or consumptions.
        
        Args:
            items: List of items with id and quantity
            item_type: 'ordered_item' or 'consumption'
            
        Returns:
            Dict: Operation result
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/reserve"
            
            request_data = {
                "items": items,
                "item_type": item_type
            }
            
            logger.info(f"Reserving {len(items)} {item_type}(s)")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Reservation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to reserve inventory: {e}")
            raise
    
    async def confirm_inventory(self, items: List[Dict], item_type: str = 'ordered_item') -> Dict:
        """
        Confirm inventory reservations (deduct from stock).
        
        Args:
            items: List of items with id and quantity
            item_type: 'ordered_item' or 'consumption'
            
        Returns:
            Dict: Operation result
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/confirm"
            
            request_data = {
                "items": items,
                "item_type": item_type
            }
            
            logger.info(f"Confirming {len(items)} {item_type}(s)")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Confirmation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to confirm inventory: {e}")
            raise
    
    async def release_inventory(self, items: List[Dict], item_type: str = 'ordered_item') -> Dict:
        """
        Release inventory reservations (cancel reservation).
        
        Args:
            items: List of items with id and quantity
            item_type: 'ordered_item' or 'consumption'
            
        Returns:
            Dict: Operation result
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/release"
            
            request_data = {
                "items": items,
                "item_type": item_type
            }
            
            logger.info(f"Releasing {len(items)} {item_type}(s)")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Release failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to release inventory: {e}")
            raise
    
    async def check_and_reserve(self, items: List[Dict], item_type: str = 'ordered_item') -> Dict:
        """
        Check availability and reserve in one operation.
        
        Args:
            items: List of items with id and quantity
            item_type: 'ordered_item' or 'consumption'
            
        Returns:
            Dict: Check and reserve results
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/check-and-reserve"
            
            request_data = {
                "items": items,
                "item_type": item_type
            }
            
            logger.info(f"Checking and reserving {len(items)} {item_type}(s)")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Check and reserve failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to check and reserve: {e}")
            raise
    
    async def get_stock_status(self, product_id: int) -> Dict:
        """
        Get stock status for a single product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Dict: Stock status
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/stock/{product_id}"
            
            logger.info(f"Getting stock status for product {product_id}")
            
            response = await send_get_request(
                endpoint=endpoint,
                params={}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Failed to get stock status: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to get stock status for product {product_id}: {e}")
            raise
    
    async def get_bulk_stock_status(self, product_ids: List[int]) -> Dict:
        """
        Get stock status for multiple products.
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            Dict: Stock status for each product
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/stock/bulk"
            
            request_data = {"product_ids": product_ids}
            
            logger.info(f"Getting bulk stock status for {len(product_ids)} products")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Failed to get bulk stock status: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to get bulk stock status: {e}")
            raise
    
    async def get_available_quantity(self, product_id: int) -> Dict:
        """
        Get available quantity for a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Dict: Available quantity
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/available/{product_id}"
            
            logger.info(f"Getting available quantity for product {product_id}")
            
            response = await send_get_request(
                endpoint=endpoint,
                params={}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Failed to get available quantity: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to get available quantity for product {product_id}: {e}")
            raise
    
    async def bulk_reserve(self, ordered_items: List[Dict] = None, consumptions: List[Dict] = None) -> Dict:
        """
        Bulk reserve inventory for both ordered items and consumptions.
        
        Args:
            ordered_items: List of ordered items with id and quantity
            consumptions: List of consumptions with id and quantity
            
        Returns:
            Dict: Bulk operation result
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/bulk/reserve"
            
            request_data = {}
            if ordered_items:
                request_data["ordered_items"] = ordered_items
            if consumptions:
                request_data["consumptions"] = consumptions
            
            logger.info(f"Bulk reserving: {len(ordered_items or [])} ordered items, {len(consumptions or [])} consumptions")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Bulk reservation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to bulk reserve: {e}")
            raise
    
    async def bulk_confirm(self, ordered_items: List[Dict] = None, consumptions: List[Dict] = None) -> Dict:
        """
        Bulk confirm inventory for both ordered items and consumptions ATOMICALLY.
        
        Args:
            ordered_items: List of ordered items with id and quantity
            consumptions: List of consumptions with id and quantity
            
        Returns:
            Dict: Bulk operation result
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/bulk/confirm"
            
            request_data = {}
            if ordered_items:
                request_data["ordered_items"] = ordered_items
            if consumptions:
                request_data["consumptions"] = consumptions
            
            logger.info(f"Bulk confirming: {len(ordered_items or [])} ordered items, {len(consumptions or [])} consumptions")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Bulk confirmation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to bulk confirm: {e}")
            raise
    
    async def bulk_release(self, ordered_items: List[Dict] = None, consumptions: List[Dict] = None) -> Dict:
        """
        Bulk release inventory for both ordered items and consumptions.
        
        Args:
            ordered_items: List of ordered items with id and quantity
            consumptions: List of consumptions with id and quantity
            
        Returns:
            Dict: Bulk operation result
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/bulk/release"
            
            request_data = {}
            if ordered_items:
                request_data["ordered_items"] = ordered_items
            if consumptions:
                request_data["consumptions"] = consumptions
            
            logger.info(f"Bulk releasing: {len(ordered_items or [])} ordered items, {len(consumptions or [])} consumptions")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {})
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Bulk release failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to bulk release: {e}")
            raise
    
    async def health_check(self) -> Dict[str, str]:
        """
        Check the health of the Inventory API.
        
        Returns:
            Dict: Health status
        """
        try:
            endpoint = f"{self.base_url}/esilo/inventory/health"
            
            response = await send_get_request(
                endpoint=endpoint,
                params={}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {"status": "healthy"})
            else:
                return {"status": "unhealthy", "error": response.get("data", {}).get("detail", "Unknown error")}
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
