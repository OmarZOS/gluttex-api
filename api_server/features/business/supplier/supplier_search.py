


from sqlalchemy import func

from storage.storage_broker import search_by_location
from core.models import Address, PersonDetails, ProductProvider, ProviderDetails, ProviderOrganisation
from core.persistent_models import Location
from storage.wrappers.sql_wrapper import get_records_by_filter
from sqlalchemy import func
# from shapely.geometry import Point
# from geoalchemy2.shape import from_shape
from geoalchemy2.elements import WKTElement

# # Suppose we have a user location POINT
# user_location = 'SRID=4326;POINT(3.05 36.75)'  # Algiers example

# labeled_attrs = [
#     func.ST_Distance(Store.location, user_location).label("distance")
# ]

# conditions = 
# [
#     func.ST_DWithin(Store.location, user_location, 5000)  # stores within 5km
# ]

def search_supplier_by_location(location:tuple[float,float],distance:float,offset:int,limit:int):
    """
    Search supplier by location (longitude,latitude).
    """
    ST_location = WKTElement(
            f"POINT({location[0]} {location[1]})",
            srid=4326
        )
    labeled_attrs = [func.ST_Distance(Location.location_position, ST_location).label("distance")]

    selected_fields = [
                        ProviderDetails.idprovider_details_id
                        ,ProviderDetails.provider_name
                        ,ProviderDetails.provider_contact_info
                        
                        ,Location.id_location
                        ,Location.position_wkt
                        
                        ,ProductProvider.id_product_provider
                        ,ProductProvider.product_provider_type_id
                        ,ProductProvider.product_provider_owner

                        ,ProviderOrganisation.idprovider_organisation
                        ,ProviderOrganisation.provider_organisation_name
                        
                        ,Address.id_address
                        ,Address.address_street
                        ,Address.address_city
                        ,Address.address_postal_code
                        ,Address.address_country
                       ]

    return search_by_location(ProductProvider
        ,join_tables=[
            ProductProvider.product_provider_location
            ,Location.location_address,ProductProvider.product_provider_details,ProductProvider.product_provider_org
            ]
        ,conditions=[func.ST_Distance(Location.location_position, ST_location) <= distance*1000]
        ,labeled_attrs=labeled_attrs
        ,ordering_attr=["distance"]
        ,selected_fields= selected_fields
        ,eager_load_depth=None
        ,offset=offset
        ,limit=limit)










# def search_supplier_by_location(location:tuple[float,float],distance:float,offset:int,limit:int):
#     """
#     Search supplier by location (longitude,latitude).
#     """
#     ST_location = WKTElement(
#             f"POINT({location[0]} {location[1]})",
#             srid=4326
#         )
#     labeled_attrs = [func.ST_Distance(Location.location_position, ST_location).label("distance")]

#     selected_fields = [
#         Location.id_location
#                         ,Location.position_wkt
#                         # ,ProductProvider.id_product_provider
#                         # ,ProductProvider.product_provider_org_id
                       
#                         # ,Address.address_street
#                         # ,Address.address_city
#                         # ,Address.address_postal_code
#                         # ,Address.address_country
#                        ]

#     return search_by_location(Location
#         ,join_tables=[
#             # Location.product_provider
#             # ,Location.location_address
#             ]
#         ,conditions=[func.ST_Distance(Location.location_position, ST_location) <= distance*1000]
#         ,labeled_attrs=labeled_attrs
#         ,ordering_attr=["distance"]
#         ,selected_fields= selected_fields
#         ,eager_load_depth=[]
#         ,offset=offset
#         ,limit=limit)


