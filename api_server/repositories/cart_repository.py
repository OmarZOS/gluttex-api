# repositories/cart_repository.py
from typing import Optional, List, Dict, Any
from core.models.models import *
import storage.storage_broker as storage_broker

class CartRepository:
    """Repository for Cart-related database operations"""
    
    def get_cart_by_id(self, cart_id: int, eager_load: bool = True) -> Optional[Cart]:
        """Get cart by ID with optional eager loading"""
        if eager_load:
            eager_fields = [
                Cart.invoice,
                Cart.receipt,
                Cart.deposit,
                {
                    Cart.ordered_item: [
                        OrderedItem.id_ordered_item,
                        OrderedItem.ordered_product_id,
                        OrderedItem.ordered_quantity,
                        OrderedItem.applied_vat,
                        OrderedItem.order_ref,
                        OrderedItem.unit_price,
                        OrderedItem.product_discount,
                        OrderedItem.ordered_product,
                    ]
                },
                {
                    Cart.app_user_: {
                        AppUser.app_user_person: [Person.person_details]
                    }
                },
                {
                    Cart.app_user: {
                        AppUser.app_user_person: [Person.person_details]
                    }
                },
                {Cart.ordered_service: [OrderedService.ordered_service_service]},
                {
                    Cart.cart_product_provider: [
                        ProductProvider.product_provider_details,
                        ProductProvider.product_provider_type,
                        ProductProvider.product_provider_org
                    ]
                },
                {
                    Cart.invoice: [Invoice.payment]
                },
                
                {
                    Cart.person: [Person.person_details]
                },
            ]
        else:
            eager_fields = []
        
        records = storage_broker.get(
            Cart,
            {Cart.cart_id: cart_id},
            [],
            eager_fields
        )
        return records[0] if records else None
    
    def get_carts_by_provider(self, provider_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by provider ID"""
        return storage_broker.get(
            Cart,
            {Cart.cart_product_provider_id: provider_id},
            [],
            [Cart.invoice, Cart.receipt, Cart.deposit],
            offset=offset,
            limit=limit
        )
    
    def get_carts_by_seller(self, seller_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by seller user ID"""
        return storage_broker.get(
            Cart,
            {Cart.cart_selling_user: seller_id},
            [],
            [Cart.invoice, Cart.receipt],
            offset=offset,
            limit=limit
        )
    
    def get_carts_by_buyer(self, buyer_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by buyer/client user ID"""
        return storage_broker.get(
            Cart,
            {Cart.cart_client_user: buyer_id},
            [],
            [Cart.invoice, Cart.receipt, Cart.deposit],
            offset=offset,
            limit=limit
        )
    
    def get_carts_by_status(self, status: str, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by status"""
        return storage_broker.get(
            Cart,
            {Cart.cart_status: status},
            [],
            [Cart.invoice, Cart.receipt],
            offset=offset,
            limit=limit
        )
    
    def create_cart(self, cart: Cart) -> Cart:
        """Create a new cart"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(cart)
    
    def update_cart(self, cart: Cart) -> Cart:
        """Update an existing cart"""
        from features.insertion import update_record_in_api
        return update_record_in_api(cart)
    
    def delete_cart(self, cart: Cart) -> bool:
        """Delete a cart"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(cart)

# repositories/service_repository.py
from typing import Optional, List
from core.models.models import ProvidedService, ServiceResourceRequirement, ServiceStaffRequirement
import storage.storage_broker as storage_broker

class ServiceRepository:
    """Repository for Service-related database operations"""
    
    def get_service_by_id(self, service_id: int, eager_load: bool = True) -> Optional[ProvidedService]:
        """Get service by ID"""
        eager_fields = []
        if eager_load:
            eager_fields = [
                ProvidedService.service_resource_requirement,
                ProvidedService.service_staff_requirement
            ]
        
        records = storage_broker.get(
            ProvidedService,
            {ProvidedService.provided_service_id: service_id},
            [],
            eager_fields
        )
        return records[0] if records else None
    
    def get_services_by_category(self, category_id: int, offset: int = 0, limit: int = 100) -> List[ProvidedService]:
        """Get services by category"""
        return storage_broker.get(
            ProvidedService,
            {ProvidedService.provided_service_category_id: category_id},
            [],
            [],
            offset=offset,
            limit=limit
        )
    
    def get_category_by_id(self, category_id: int) -> ProvidedServiceCategory:
        """Get services by category"""
        data = storage_broker.get(
            ProvidedServiceCategory,
            {ProvidedServiceCategory.provided_service_category_id: category_id},
            [],
            [],
            offset=0,
            limit=1
        )
        return data[0] if len(data)>0 else None
    
    def get_services_by_provider(self, provider_id: int, offset: int = 0, limit: int = 100) -> List[ProvidedService]:
        """Get services by provider"""
        return storage_broker.get(
            ProvidedService,
            {ProvidedService.provided_service_product_provider_id: provider_id},
            [],
            [],
            offset=offset,
            limit=limit
        )
    
    def get_services(self, offset: int = 0, limit: int = 100) -> List[ProvidedService]:
        """Get services by provider"""
        return storage_broker.get(
            ProvidedService,
            {},
            [],
            [],
            offset=offset,
            limit=limit
        )
    
    def get_package_items_by_service(self, id:int) -> List[ProvidedService]:
        return storage_broker.get(
            ServicePackageItem,
            {ServicePackageItem.service_package_item_service_id: id},
            [],
            [],
            offset=0,
            limit=10
        )
    
    def get_cart_items_by_service(self, id:int) -> List[ProvidedService]:
        return storage_broker.get(
            OrderedService,
            {OrderedService.ordered_service_service_id: id},
            [],
            [],
            offset=0,
            limit=10
        )
    
    
    
    def get_active_services(self, provider_id: Optional[int] = None) -> List[ProvidedService]:
        """Get active services"""
        conditions = {ProvidedService.provided_service_is_active: True}
        if provider_id:
            conditions[ProvidedService.provided_service_product_provider_id] = provider_id
        
        return storage_broker.get(ProvidedService, conditions, [], [])
    
    def create_service(self, service: ProvidedService) -> ProvidedService:
        """Create a new service"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(service)
    
    def update_service(self, service: ProvidedService) -> ProvidedService:
        """Update an existing service"""
        from features.insertion import update_record_in_api
        return update_record_in_api(service)
    
    def delete_service_resource_requirements(self, service: ServiceResourceRequirement) -> bool:
        """Delete a service req"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(service)
    
    def delete_service_staff_requirements(self, service: ServiceStaffRequirement) -> bool:
        """Delete a service req"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(service)
    
    def delete_service(self, service: ProvidedService) -> bool:
        """Delete a service"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(service)

    def delete_service(self, service: ProvidedService) -> bool:
        """Delete a service"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(service)
    
    def get_service_resource_requirements(self, service_id: int) -> List[ServiceResourceRequirement]:
        """Get resource requirements for a service"""
        return storage_broker.get(
            ServiceResourceRequirement,
            {ServiceResourceRequirement.service_resource_requirement_service_id: service_id},
            [],
            []
        )
    
    def get_service_staff_requirements(self, service_id: int) -> List[ServiceStaffRequirement]:
        """Get staff requirements for a service"""
        return storage_broker.get(
            ServiceStaffRequirement,
            {ServiceStaffRequirement.service_staff_requirement_service_id: service_id},
            [],
            []
        )
    

# repositories/financial_repository.py
from typing import Optional, List
from core.models.models import Invoice, Payment
import storage.storage_broker as storage_broker

class FinancialRepository:
    """Repository for financial document operations"""
    
    def create_invoice(self, invoice: Invoice) -> Invoice:
        """Create an invoice"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(invoice)
    
    def create_payment(self, payment: Payment) -> Payment:
        """Create a payment"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(payment)
    
    
    def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        records = storage_broker.get(Invoice, {Invoice.invoice_id: invoice_id}, [], [])
        return records[0] if records else None
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        records = storage_broker.get(Payment, {Payment.payment_id: payment_id}, [], [])
        return records[0] if records else None
    
    def update_invoice(self, invoice: Invoice) -> Invoice:
        """Update an invoice"""
        from features.insertion import update_record_in_api
        return update_record_in_api(invoice)
    
    def update_payment(self, payment: Payment) -> Payment:
        """Update a payment"""
        from features.insertion import update_record_in_api
        return update_record_in_api(payment)