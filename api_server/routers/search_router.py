# routers/search_router.py
"""
Search router for searching across multiple entity types (products, recipes, users, people, suppliers).
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from typing import List, Optional, Dict, Any
import logging

from core.response_models import ErrorResponseModel, get_crud_error_responses
from core.exceptions.specific.search_exceptions import (
    SearchQueryTooShortException,
    SearchEntityNotFoundException,
    SearchExecutionException
)
from services.search_service import SearchService

logger = logging.getLogger(__name__)

search_router = APIRouter()


# ==================== Dependency Injection ====================

def get_search_service() -> SearchService:
    return SearchService()


# ==================== Single Entity Search Endpoints ====================

@search_router.get(
    "/search/product/{token}/{offset}/{limit}",
    summary="Search products",
    description="Search products by token in name, brand, and description",
    responses={
        # 200: {"description": "Products retrieved successfully"},
        400: {"model": ErrorResponseModel, "description": "Search query too short"},
        404: {"model": ErrorResponseModel}
    }
)
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
    logger.info(f"Searching products with token: '{token}' (offset={offset}, limit={limit})")
    
    if len(token) < 2:
        raise SearchQueryTooShortException(min_length=2)
    
    results = search_service.search_products(token, offset, limit)
    logger.info(f"Found {len(results)} products matching '{token}'")
    
    return results


@search_router.get(
    "/search/recipe/{token}/{offset}/{limit}",
    summary="Search recipes",
    description="Search recipes by token in name, description, and instructions",
    responses={
        # 200: {"description": "Recipes retrieved successfully"},
        400: {"model": ErrorResponseModel, "description": "Search query too short"},
        404: {"model": ErrorResponseModel}
    }
)
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
    logger.info(f"Searching recipes with token: '{token}' (offset={offset}, limit={limit})")
    
    if len(token) < 2:
        raise SearchQueryTooShortException(min_length=2)
    
    results = search_service.search_recipes(token, offset, limit)
    logger.info(f"Found {len(results)} recipes matching '{token}'")
    
    return results


@search_router.get(
    "/search/personnel/{token}",
    summary="Search personnel/users",
    description="Search users (personnel) by token in person details and username",
    responses={
        # 200: {"description": "Users retrieved successfully"},
        400: {"model": ErrorResponseModel, "description": "Search query too short"},
        404: {"model": ErrorResponseModel}
    }
)
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
    logger.info(f"Searching users with token: '{token}' (offset={offset}, limit={limit})")
    
    if len(token) < 2:
        raise SearchQueryTooShortException(min_length=2)
    
    results = search_service.search_users(token, offset, limit)
    logger.info(f"Found {len(results)} users matching '{token}'")
    
    return results


@search_router.get(
    "/search/people/{token}",
    summary="Search people",
    description="Search people by token in person details (first name, last name, nationality)",
    responses={
        # 200: {"description": "People retrieved successfully"},
        400: {"model": ErrorResponseModel, "description": "Search query too short"},
        404: {"model": ErrorResponseModel}
    }
)
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
    logger.info(f"Searching people with token: '{token}' (offset={offset}, limit={limit})")
    
    if len(token) < 2:
        raise SearchQueryTooShortException(min_length=2)
    
    results = search_service.search_people(token, offset, limit)
    logger.info(f"Found {len(results)} people matching '{token}'")
    
    return results


@search_router.get(
    "/search/supplier/{token}/{offset}/{limit}",
    summary="Search suppliers",
    description="Search suppliers by token in provider name and contact info",
    responses={
        # 200: {"description": "Suppliers retrieved successfully"},
        400: {"model": ErrorResponseModel, "description": "Search query too short"},
        404: {"model": ErrorResponseModel}
    }
)
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
    logger.info(f"Searching suppliers with token: '{token}' (offset={offset}, limit={limit})")
    
    if len(token) < 2:
        raise SearchQueryTooShortException(min_length=2)
    
    results = search_service.search_suppliers(token, offset, limit)
    logger.info(f"Found {len(results)} suppliers matching '{token}'")
    
    return results


@search_router.get(
    "/search/position/supplier/{longitude}/{latitude}/{distance_km}/{offset}/{limit}",
    summary="Search suppliers by geographic position",
    description="Search suppliers by geographic position within a radius",
    responses={
        # 200: {"description": "Suppliers retrieved successfully"},
        400: {"model": ErrorResponseModel, "description": "Invalid coordinates"},
        404: {"model": ErrorResponseModel}
    }
)
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
    logger.info(f"Searching suppliers near ({longitude}, {latitude}) within {distance_km}km")
    
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Invalid longitude: {longitude}")
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Invalid latitude: {latitude}")
    if distance_km <= 0:
        raise ValueError(f"Distance must be positive: {distance_km}")
    
    results = search_service.search_suppliers_by_location(
        longitude, latitude, distance_km, offset, limit
    )
    logger.info(f"Found {len(results)} suppliers in the specified area")
    
    return results


# ==================== Enhanced Multi-Search Endpoints ====================

@search_router.get(
    "/search/multi",
    summary="Multi-entity search",
    description="Search across multiple entity types in a single request",
    responses={
        # 200: {"description": "Search completed successfully"},
        400: {"model": ErrorResponseModel, "description": "Invalid parameters"}
    }
)
def multi_search(
    token: str = Query(..., min_length=2, description="Search query string"),
    entities: List[str] = Query(
        default=['products', 'recipes', 'users', 'people', 'suppliers'],
        description="Entity types to search (comma-separated: products,recipes,users,people,suppliers)"
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results per entity type"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search across multiple entity types in a single request.
    
    Args:
        token: Search query string (minimum 2 characters)
        entities: List of entity types to search
        offset: Pagination offset
        limit: Pagination limit per entity
    
    Returns:
        Dictionary with results grouped by entity type
    """
    logger.info(f"Multi-search with token: '{token}', entities: {entities}")
    
    valid_entities = {'products', 'recipes', 'users', 'people', 'suppliers'}
    invalid_entities = [e for e in entities if e not in valid_entities]
    
    if invalid_entities:
        logger.warning(f"Invalid entity types requested: {invalid_entities}")
        raise SearchEntityNotFoundException(
            entity_type=", ".join(invalid_entities),
            valid_types=list(valid_entities)
        )
    
    results = search_service.multi_search(token, entities, offset, limit)
    
    return {
        "status": "success",
        "query": token,
        "entities_searched": entities,
        "results": results,
        "summary": {
            entity: len(results.get(entity, []))
            for entity in entities
        }
    }


@search_router.get(
    "/search/quick/{token}",
    summary="Quick search (autocomplete)",
    description="Quick search across all entity types with small result sets for autocomplete",
    responses={
        # 200: {"description": "Quick search completed successfully"},
        400: {"model": ErrorResponseModel, "description": "Search query too short"}
    }
)
def quick_search(
    token: str,
    limit: int = Query(5, ge=1, le=20, description="Maximum results per entity type"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Quick search across all entity types with small result sets.
    Useful for autocomplete or quick lookup features.
    
    Args:
        token: Search query string (minimum 2 characters)
        limit: Maximum results per entity type
    
    Returns:
        Dictionary with limited results from all entity types
    """
    logger.info(f"Quick search with token: '{token}' (limit={limit})")
    
    if len(token) < 2:
        raise SearchQueryTooShortException(min_length=2)
    
    entities = ['products', 'recipes', 'users', 'people', 'suppliers']
    results = search_service.multi_search(token, entities, 0, limit)
    
    return {
        "status": "success",
        "query": token,
        "results": results
    }


# ==================== Health Check Endpoint ====================

@search_router.get(
    "/search/health",
    summary="Search service health check",
    description="Check if search service is operational",
    responses={
        # 200: {"description": "Service is healthy"},
        500: {"model": ErrorResponseModel, "description": "Service is unhealthy"}
    }
)
def search_health_check(
    search_service: SearchService = Depends(get_search_service)
):
    """
    Health check endpoint for search service.
    """
    logger.info("Search service health check requested")
    
    try:
        # Try a simple search to verify service is working
        test_result = search_service.search_products("test", 0, 1)
        
        return {
            "status": "healthy",
            "message": "Search service is operational",
            "timestamp": import_datetime().now().isoformat()
        }
    except Exception as e:
        logger.error(f"Search service health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
            "timestamp": import_datetime().now().isoformat()
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


# Helper function for datetime import
def import_datetime():
    from datetime import datetime
    return datetime