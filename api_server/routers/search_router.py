from fastapi import APIRouter
from features.business.supplier.supplier_search import search_supplier_by_location
from core.models import Location, Product, ProductProvider, ProviderDetails, Recipe
from storage.storage_broker import search_records

search_router = APIRouter()
# logger = logging.getLogger("FastAPIApp")

@search_router.get("/search/product/{token}/{offset}/{limit}")
def search_for_product(token:str,offset:int,limit:int):
    """
    Search products by token.
    """
    return search_records( Product, search_query=token,search_fields=[Product.product_brand,Product.product_name,Product.product_description],offset=offset,limit=limit )


@search_router.get("/search/recipe/{token}/{offset}/{limit}")
def search_for_recipe(token:str,offset:int,limit:int):
    """
    Search recipes by token.
    """
    return search_records(Recipe, search_query= token,search_fields= [Recipe.recipe_name,Recipe.recipe_description,Recipe.recipe_instructions],offset= offset,limit= limit)

@search_router.get("/search/supplier/{token}/{offset}/{limit}")
def search_supplier(token:str,offset:int,limit:int):
    """
    Search supplier by token.
    """
    return search_records(ProviderDetails
                          ,[
                              ProviderDetails.product_provider
                              ]
                          ,
                          search_fields=[ProviderDetails.provider_name
                            ,ProviderDetails.provider_contact_info
                            # ,ProductProvider.product_provider_details_id
                            ]
                            ,search_query=token
                            ,eager_load_depth=[
                                {ProviderDetails.product_provider:[ProductProvider.product_provider_org,{ProductProvider.product_provider_location:{
                                    Location.location_name,Location.position_wkt,Location.location_address,
                                }}]}
                                ]
                            ,offset=offset
                            ,limit=limit)

@search_router.get("/search/position/supplier/{longitude}/{latitude}/{offset}/{limit}")
def search_supplier_by_position(longitude:float,latitude:float,distance_km:float,offset:int,limit:int):
    """
    Search supplier by position, distance is in meters.
    """
    return search_supplier_by_location((longitude,latitude),distance_km,offset,limit)


