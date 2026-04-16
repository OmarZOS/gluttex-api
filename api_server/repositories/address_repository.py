from typing import Optional, List
from core.models import Address
import storage.storage_broker as storage_broker

class AddressRepository:
    """Repository for Address-related database operations"""
    
    def get_address_by_id(self, address_id: str) -> Optional[Address]:
        """Get address by ID"""
        records = storage_broker.get(Address, {Address.id_address: address_id}, None, [])
        return records[0] if records else None
    
    def get_addresses_by_city(self, city: str) -> List[Address]:
        """Get addresses by city"""
        return storage_broker.get(Address, {Address.address_city: city}, None, [])
    
    def get_addresses_by_country(self, country: str) -> List[Address]:
        """Get addresses by country"""
        return storage_broker.get(Address, {Address.address_country: country}, None, [])
    
    def create_address(self, address: Address) -> Address:
        """Create a new address"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(address)
    
    def update_address(self, address: Address) -> Address:
        """Update an existing address"""
        from features.insertion import update_record_in_api
        return update_record_in_api(address)
    
    def delete_address(self, address_id: str) -> bool:
        """Delete an address"""
        from features.insertion import delete_record_from_api
        address = self.get_address_by_id(address_id)
        if address:
            return delete_record_from_api(address)
        return False