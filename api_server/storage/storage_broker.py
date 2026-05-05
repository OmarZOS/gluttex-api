# storage/medicom_store.py
"""
This component is responsible for choosing the right place
to insert/fetch data in/from the most appropriate
store, it can support multiple storage engines.
The insertion/fetch logic is in here.
"""

import logging
from typing import Optional, List, Dict, Any, Union

from core.exceptions.handler import APIException
from core.messages.error_codes import ErrorCode
from core.messages.http_status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_417_EXPECTATION_FAILED,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from constants import DB_URI
import storage.wrappers.sql_wrapper as medicom_store

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Base exception for storage-related errors"""
    pass


def _handle_storage_exception(error: Exception, operation: str, **context) -> None:
    """Centralized storage exception handler"""
    logger.error(f"Storage error during {operation}: {error}", extra=context)
    
    if isinstance(error, StorageError):
        raise APIException(
            status_code=HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.DATABASE_ERROR,
            message=str(error),
            details=context
        )
    elif "integrity" in str(error).lower() or "duplicate" in str(error).lower():
        raise APIException(
            status_code=HTTP_417_EXPECTATION_FAILED,
            error_code=ErrorCode.INTEGRITY_ERROR,
            message="Database integrity constraint violated",
            details={"operation": operation, "error": str(error), **context}
        )
    elif "not found" in str(error).lower():
        raise APIException(
            status_code=HTTP_404_NOT_FOUND,
            error_code=ErrorCode.DATA_ERROR,
            message="Record not found",
            details={"operation": operation, "error": str(error), **context}
        )
    else:
        raise APIException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.DATABASE_ERROR,
            message=f"Database operation failed: {operation}",
            details={"error": str(error), **context}
        )


def get_engine_with_retry(uri: str = DB_URI, retry_count: int = 3):
    """Get database engine with retry logic"""
    import time
    
    for attempt in range(retry_count):
        try:
            engine = medicom_store.get_engine(uri)
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except Exception as e:
            if attempt == retry_count - 1:
                _handle_storage_exception(e, "get_engine", uri=uri, attempt=attempt)
            time.sleep(1)
    return None


def insert_record(item: Any) -> Any:
    """
    Insert a record into the database
    
    Args:
        item: ORM object to insert
        
    Returns:
        The inserted record with generated ID
        
    Raises:
        APIException: If insertion fails
    """
    try:
        engine = get_engine_with_retry(DB_URI)
        if not engine:
            raise StorageError("Failed to establish database connection")
        
        result = medicom_store.add_record(engine, item)
        logger.debug(f"Record inserted successfully: {type(item).__name__}")
        return result
    except Exception as e:
        _handle_storage_exception(e, "insert_record", record_type=type(item).__name__)


def get(
    table: Any,
    conditions: Optional[Dict] = None,
    join_tables: Optional[List] = None,
    eager_load_depth: Optional[int] = None,
    offset: int = 0,
    limit: int = 10
) -> List[Any]:
    """
    Fetch records from the database
    
    Args:
        table: SQLAlchemy table/model class
        conditions: Filter conditions (dict or SQLAlchemy conditions)
        join_tables: List of tables to join
        eager_load_depth: Depth for eager loading relationships
        offset: Pagination offset
        limit: Records per page (max 1000)
        
    Returns:
        List of records
    """
    # Validate pagination parameters
    if limit > 1000:
        raise APIException(
            status_code=HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Limit cannot exceed 1000",
            details={"limit": limit, "max_limit": 1000}
        )
    
    try:
        engine = get_engine_with_retry(DB_URI)
        if not engine:
            raise StorageError("Failed to establish database connection")
        
        result = medicom_store.get_records(
            engine, table, conditions, join_tables, 
            eager_load_depth, offset, limit
        )
        logger.debug(f"Retrieved {len(result)} records from {table.__name__ if hasattr(table, '__name__') else table}")
        return result
    except Exception as e:
        _handle_storage_exception(
            e, "get_records", 
            table=str(table), 
            offset=offset, 
            limit=limit
        )


def count(
    table: Any,
    conditions: Optional[Dict] = None,
    join_tables: Optional[List] = None,
    group_by: Optional[List] = None
) -> int:
    """
    Count records in the database
    
    Args:
        table: SQLAlchemy table/model class
        conditions: Filter conditions
        join_tables: List of tables to join
        group_by: Group by fields
        
    Returns:
        Total count of records
    """
    try:
        engine = get_engine_with_retry(DB_URI)
        if not engine:
            raise StorageError("Failed to establish database connection")
        
        result = medicom_store.count_records(engine, table, conditions, join_tables, group_by)
        logger.debug(f"Counted {result} records from {table.__name__ if hasattr(table, '__name__') else table}")
        return result
    except Exception as e:
        _handle_storage_exception(
            e, "count_records",
            table=str(table)
        )


def delete_record(item: Any) -> bool:
    """
    Delete a record from the database
    
    Args:
        item: ORM object to delete
        
    Returns:
        True if deletion successful
        
    Raises:
        APIException: If deletion fails
    """
    try:
        engine = get_engine_with_retry(DB_URI)
        if not engine:
            raise StorageError("Failed to establish database connection")
        
        medicom_store.delete_record(engine, item)
        logger.debug(f"Record deleted successfully: {type(item).__name__}")
        return True
    except Exception as e:
        _handle_storage_exception(e, "delete_record", record_type=type(item).__name__)


def update_record(item: Any) -> Any:
    """
    Update a record in the database
    
    Args:
        item: ORM object with updated values
        
    Returns:
        Updated record
    """
    try:
        engine = get_engine_with_retry(DB_URI)
        if not engine:
            raise StorageError("Failed to establish database connection")
        
        result = medicom_store.update_record(engine, item)
        logger.debug(f"Record updated successfully: {type(item).__name__}")
        return result
    except Exception as e:
        _handle_storage_exception(e, "update_record", record_type=type(item).__name__)


def delete_record_by_id(table: Any, record_id: Union[int, str]) -> bool:
    """
    Delete a record by its ID
    
    Args:
        table: SQLAlchemy table/model class
        record_id: ID of the record to delete
        
    Returns:
        True if deletion successful
    """
    try:
        engine = get_engine_with_retry(DB_URI)
        if not engine:
            raise StorageError("Failed to establish database connection")
        
        result = medicom_store.delete_record_by_id(engine, table, record_id)
        logger.debug(f"Record {record_id} deleted from {table.__name__ if hasattr(table, '__name__') else table}")
        return result
    except Exception as e:
        _handle_storage_exception(
            e, "delete_record_by_id",
            table=str(table),
            record_id=record_id
        )


def search_records(
    table: Any,
    join_tables: Optional[List] = None,
    eager_load_depth: Optional[int] = None,
    search_query: Optional[str] = None,
    search_fields: Optional[List[str]] = None,
    offset: int = 0,
    limit: int = 20
) -> List[Any]:
    """
    Search records using full-text search
    
    Args:
        table: SQLAlchemy table/model class
        join_tables: Tables to join
        eager_load_depth: Eager loading depth
        search_query: Search string
        search_fields: Fields to search in
        offset: Pagination offset
        limit: Records per page (max 100)
        
    Returns:
        List of matching records
    """
    # Validate pagination
    if limit > 100:
        limit = 100
        logger.warning(f"Limit capped to 100 for search operation")
    
    if search_query and len(search_query) < 2:
        raise APIException(
            status_code=HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Search query must be at least 2 characters long",
            details={"search_query": search_query, "min_length": 2}
        )
    
    try:
        engine = get_engine_with_retry(DB_URI)
        if not engine:
            raise StorageError("Failed to establish database connection")
        
        result = medicom_store.search_records(
            engine, table, join_tables, eager_load_depth,
            search_query, search_fields, offset, limit
        )
        logger.debug(f"Search returned {len(result)} results for query '{search_query}'")
        return result
    except Exception as e:
        _handle_storage_exception(
            e, "search_records",
            table=str(table),
            search_query=search_query,
            offset=offset,
            limit=limit
        )


def search_by_location(
    table: Any,
    join_tables: Optional[List] = None,
    conditions: Optional[Dict] = None,
    labeled_attrs: Optional[List] = None,
    ordering_attr: Optional[str] = None,
    selected_fields: Optional[List] = None,
    eager_load_depth: Optional[int] = None,
    offset: int = 0,
    limit: int = 20
) -> List[Any]:
    """
    Search records by geographic location
    
    Args:
        table: SQLAlchemy table/model class
        join_tables: Tables to join
        conditions: Filter conditions
        labeled_attrs: Attributes to label/return
        ordering_attr: Attribute to order by (e.g., distance)
        selected_fields: Specific fields to select
        eager_load_depth: Eager loading depth
        offset: Pagination offset
        limit: Records per page (max 100)
        
    Returns:
        List of records with location data
    """
    # Validate pagination
    if limit > 100:
        limit = 100
        logger.warning(f"Limit capped to 100 for location search")
    
    try:
        engine = get_engine_with_retry(DB_URI)
        if not engine:
            raise StorageError("Failed to establish database connection")
        
        result = medicom_store.get_records_by_filter(
            engine, table,
            join_tables=join_tables,
            conditions=conditions,
            labeled_attrs=labeled_attrs,
            ordering_attr=ordering_attr,
            selected_fields=selected_fields,
            eager_load_depth=eager_load_depth,
            offset=offset,
            limit=limit
        )
        logger.debug(f"Location search returned {len(result)} results")
        return result
    except Exception as e:
        _handle_storage_exception(
            e, "search_by_location",
            table=str(table),
            offset=offset,
            limit=limit
        )


# Optional: Add validation utilities
def validate_table_name(table: Any) -> bool:
    """Validate that table is a valid SQLAlchemy model"""
    if table is None:
        raise APIException(
            status_code=HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Table cannot be None",
            details={"table": str(table)}
        )
    return True


def validate_pagination(offset: int, limit: int, max_limit: int = 1000) -> None:
    """Validate pagination parameters"""
    if offset < 0:
        raise APIException(
            status_code=HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Offset must be non-negative",
            details={"offset": offset}
        )
    
    if limit < 1 or limit > max_limit:
        raise APIException(
            status_code=HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.VALIDATION_ERROR,
            message=f"Limit must be between 1 and {max_limit}",
            details={"limit": limit, "max_limit": max_limit}
        )