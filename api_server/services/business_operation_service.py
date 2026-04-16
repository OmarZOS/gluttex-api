# services/business_operation_service.py
from typing import List, Dict, Any
from core.persistent_models import BusinessOperation
from storage import storage_broker

class BusinessOperationService:
    """Service for business operations"""
    
    def get_operations(
        self,
        supplier_id: int = 0,
        order_id: int = 0,
        cart_id: int = 0,
        client_id: int = 0,
        seller_id: int = 0,
        offset: int = 0,
        limit: int = 100
    ) -> List[BusinessOperation]:
        """Get business operations with filters"""
        conditions = {}
        
        if supplier_id > 0:
            conditions[BusinessOperation.supplier_id] = supplier_id
        if order_id > 0:
            conditions[BusinessOperation.order_id] = order_id
        if cart_id > 0:
            conditions[BusinessOperation.cart_id] = cart_id
        if client_id > 0:
            conditions[BusinessOperation.client_id] = client_id
        if seller_id > 0:
            conditions[BusinessOperation.seller_id] = seller_id
        
        return storage_broker.get(
            BusinessOperation,
            conditions,
            [],
            None,
            offset,
            limit
        )