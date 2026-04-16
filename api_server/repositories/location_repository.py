from typing import Optional, List
from core.models import Address
from core.persistent_models import Location
import storage.storage_broker as storage_broker

class LocationRepository:
    """Repository for Location-related database operations"""
    
    def get_location_by_id(self, location_id: str, with_address: bool = False) -> Optional[Location]:
        """Get location by ID with optional address loading"""
        if with_address:
            records = storage_broker.get(
                Location,
                {Location.id_location: location_id},
                None,
                [Location.location_address]
            )
        else:
            records = storage_broker.get(
                Location,
                {Location.id_location: location_id},
                None,
                []
            )
        return records[0] if records else None
    
    def get_all_locations(self, offset: int = 0, limit: int = 100) -> List[Location]:
        """Get all locations with pagination"""
        return storage_broker.get(
            Location,
            conditions={},
            join_tables=[],
            eager_load_depth=[Location.location_address],
            offset=offset,
            limit=limit
        )
    
    def create_location(self, location: Location) -> Location:
        """Create a new location"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(location)
    
    def update_location(self, location: Location) -> Location:
        """Update an existing location"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(location)
    
    def delete_location(self, location_id: str) -> bool:
        """Delete a location"""
        from features.insertion import delete_record_from_api
        location = self.get_location_by_id(location_id)
        if location:
            return delete_record_from_api(location)
        return False

