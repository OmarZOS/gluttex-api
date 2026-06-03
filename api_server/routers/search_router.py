# routers/search_router.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from services.search_service import SearchService

search_router = APIRouter()

def get_search_service() -> SearchService:
    return SearchService()


@search_router.get("/search/product/{token}/{offset}/{limit}")
def search_for_product(
    token: str,
    offset: int,
    limit: int,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search products by token in name, brand, and description.
    
    Args:
        token: Search query string
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of matching products
    """
    return search_service.search_products(token, offset, limit)


@search_router.get("/search/recipe/{token}/{offset}/{limit}")
def search_for_recipe(
    token: str,
    offset: int,
    limit: int,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search recipes by token in name, description, and instructions.
    
    Args:
        token: Search query string
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of matching recipes
    """
    return search_service.search_recipes(token, offset, limit)


@search_router.get("/search/personnel/{token}/{offset}/{limit}")
def search_for_user(
    token: str,
    offset: int,
    limit: int,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search users (personnel) by token in person details and username.
    
    Args:
        token: Search query string
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of matching users
    """
    return search_service.search_users(token, offset, limit)


@search_router.get("/search/people/{token}/{offset}/{limit}")
def search_for_people(
    token: str,
    offset: int,
    limit: int,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search people by token in person details.
    
    Args:
        token: Search query string
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of matching people
    """
    return search_service.search_people(token, offset, limit)


@search_router.get("/search/supplier/{token}/{offset}/{limit}")
def search_supplier(
    token: str,
    offset: int,
    limit: int,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search suppliers by token in provider name and contact info.
    
    Args:
        token: Search query string
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of matching suppliers
    """
    return search_service.search_suppliers(token, offset, limit)


@search_router.get("/search/position/supplier/{longitude}/{latitude}/{distance_km}/{offset}/{limit}")
def search_supplier_by_position(
    longitude: float,
    latitude: float,
    distance_km: float,
    offset: int,
    limit: int,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search suppliers by geographic position.
    
    Args:
        longitude: Longitude coordinate
        latitude: Latitude coordinate
        distance_km: Search radius in kilometers
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of matching suppliers with distance information
    """
    return search_service.search_suppliers_by_location(
        longitude, latitude, distance_km, offset, limit
    )


# ==================== Enhanced Search Endpoints ====================

@search_router.get("/search/multi")
def multi_search(
    token: str = Query(..., description="Search query string"),
    entities: List[str] = Query(
        default=['products', 'recipes', 'users', 'people', 'suppliers'],
        description="Entity types to search"
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search across multiple entity types in a single request.
    
    Args:
        token: Search query string
        entities: List of entity types to search
        offset: Pagination offset
        limit: Pagination limit per entity
    
    Returns:
        Dictionary with results grouped by entity type
    """
    return search_service.multi_search(token, entities, offset, limit)


@search_router.get("/search/quick/{token}")
def quick_search(
    token: str,
    limit: int = Query(5, ge=1, le=20),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Quick search across all entity types with small result sets.
    Useful for autocomplete or quick lookup features.
    
    Args:
        token: Search query string
        limit: Maximum results per entity type
    
    Returns:
        Dictionary with limited results from all entity types
    """
    return search_service.multi_search(
        token,
        ['products', 'recipes', 'users', 'people', 'suppliers'],
        0,
        limit
    )