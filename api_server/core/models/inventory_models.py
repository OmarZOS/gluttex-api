# models/inventory_models.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

from core.models.finance_models import DailyPaymentStats, InvoicePaymentSummary, PaymentCreate, PaymentRefund, PaymentResponse

# ==================== Request Models ====================

class InventoryItem(BaseModel):
    """Single inventory item for reservation/confirmation/release"""
    id: int = Field(..., description="ID of the ordered_item or consumption", gt=0)
    quantity: int = Field(..., description="Quantity to reserve/confirm/release", ge=1)
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 10000:
            raise ValueError('Quantity cannot exceed 10,000')
        return v


class ReserveRequest(BaseModel):
    """Request model for reserving inventory"""
    items: List[InventoryItem] = Field(..., description="Items to reserve", min_length=1)
    item_type: str = Field(..., description="Type of items: 'ordered_item' or 'consumption'")
    
    @field_validator('item_type')
    @classmethod
    def validate_item_type(cls, v: str) -> str:
        if v not in ['ordered_item', 'consumption']:
            raise ValueError("item_type must be 'ordered_item' or 'consumption'")
        return v
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v: List[InventoryItem]) -> List[InventoryItem]:
        if len(v) > 100:
            raise ValueError('Cannot process more than 100 items at once')
        return v


class ConfirmRequest(BaseModel):
    """Request model for confirming inventory"""
    items: List[InventoryItem] = Field(..., description="Items to confirm", min_length=1)
    item_type: str = Field(..., description="Type of items: 'ordered_item' or 'consumption'")
    
    @field_validator('item_type')
    @classmethod
    def validate_item_type(cls, v: str) -> str:
        if v not in ['ordered_item', 'consumption']:
            raise ValueError("item_type must be 'ordered_item' or 'consumption'")
        return v


class ReleaseRequest(BaseModel):
    """Request model for releasing inventory"""
    items: List[InventoryItem] = Field(..., description="Items to release", min_length=1)
    item_type: str = Field(..., description="Type of items: 'ordered_item' or 'consumption'")
    
    @field_validator('item_type')
    @classmethod
    def validate_item_type(cls, v: str) -> str:
        if v not in ['ordered_item', 'consumption']:
            raise ValueError("item_type must be 'ordered_item' or 'consumption'")
        return v


class CheckAvailabilityRequest(BaseModel):
    """Request model for checking availability"""
    product_ids: List[int] = Field(..., description="Product IDs to check", min_length=1)
    
    @field_validator('product_ids')
    @classmethod
    def validate_product_ids(cls, v: List[int]) -> List[int]:
        if len(v) > 100:
            raise ValueError('Cannot check more than 100 products at once')
        return v


class BulkInventoryRequest(BaseModel):
    """Request model for bulk inventory operations"""
    ordered_items: List[InventoryItem] = Field(
        default_factory=list,
        description="Ordered items to process"
    )
    consumptions: List[InventoryItem] = Field(
        default_factory=list,
        description="Consumptions to process"
    )
    
    @field_validator('ordered_items', 'consumptions')
    @classmethod
    def validate_items_length(cls, v: List[InventoryItem]) -> List[InventoryItem]:
        if len(v) > 100:
            raise ValueError('Cannot process more than 100 items per type')
        return v
    
    def has_items(self) -> bool:
        return bool(self.ordered_items) or bool(self.consumptions)


# ==================== Response Models ====================

class InventoryItemResult(BaseModel):
    """Result for a single inventory item"""
    id: int = Field(..., description="ID of the item")
    product_id: Optional[int] = Field(None, description="Product ID associated with the item")
    quantity: int = Field(..., description="Quantity processed")
    success: bool = Field(..., description="Whether the operation succeeded")
    reason: Optional[str] = Field(None, description="Reason for failure if any")


class InventoryOperationResponse(BaseModel):
    """Response model for inventory operations"""
    success: bool = Field(..., description="Whether the entire operation succeeded")
    success_count: int = Field(..., description="Number of successfully processed items")
    failed_count: int = Field(..., description="Number of failed items")
    success_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of successfully processed items"
    )
    failed_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of failed items with reasons"
    )
    results: Optional[Dict[str, bool]] = Field(
        None,
        description="Detailed results mapping item ID to success status"
    )
    
    @property
    def is_partial_success(self) -> bool:
        return self.success_count > 0 and self.failed_count > 0
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failed_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100


class CheckAndReserveResponse(BaseModel):
    """Response model for check and reserve operation"""
    success: bool = Field(..., description="Whether the entire operation succeeded")
    items: List[InventoryItemResult] = Field(..., description="Results for each item")
    
    @property
    def all_successful(self) -> bool:
        return all(item.success for item in self.items)
    
    @property
    def failed_items(self) -> List[InventoryItemResult]:
        return [item for item in self.items if not item.success]


class StockStatusResponse(BaseModel):
    """Response model for stock status"""
    product_id: int = Field(..., description="Product ID")
    stock_quantity: int = Field(..., description="Current stock quantity")
    reserved_quantity: int = Field(..., description="Currently reserved quantity")
    available_quantity: int = Field(..., description="Available quantity (stock - reserved)")
    version: int = Field(0, description="Version number for optimistic locking")
    
    @property
    def is_in_stock(self) -> bool:
        return self.available_quantity > 0
    
    @property
    def is_low_stock(self, threshold: int = 10) -> bool:
        return self.available_quantity <= threshold


class InventorySummaryResponse(BaseModel):
    """Response model for inventory summary"""
    id: int = Field(..., description="Product ID")
    stock_quantity: int = Field(..., description="Current stock quantity")
    reserved_quantity: int = Field(..., description="Currently reserved quantity")
    available_quantity: int = Field(..., description="Available quantity (stock - reserved)")
    version: int = Field(0, description="Version number for optimistic locking")


class AvailableQuantityResponse(BaseModel):
    """Response model for available quantity"""
    product_id: int = Field(..., description="Product ID")
    available_quantity: int = Field(..., description="Available quantity")


class BulkOperationResponse(BaseModel):
    """Response model for bulk operations"""
    ordered_items: Optional[InventoryOperationResponse] = Field(
        None,
        description="Result for ordered items"
    )
    consumptions: Optional[InventoryOperationResponse] = Field(
        None,
        description="Result for consumptions"
    )
    overall_success: bool = Field(..., description="Whether the entire bulk operation succeeded")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    
    @property
    def total_success_count(self) -> int:
        count = 0
        if self.ordered_items:
            count += self.ordered_items.success_count
        if self.consumptions:
            count += self.consumptions.success_count
        return count
    
    @property
    def total_failed_count(self) -> int:
        count = 0
        if self.ordered_items:
            count += self.ordered_items.failed_count
        if self.consumptions:
            count += self.consumptions.failed_count
        return count


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    database: str = Field(..., description="Database connection status")





