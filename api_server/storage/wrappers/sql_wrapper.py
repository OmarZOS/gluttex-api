# storage/storage_broker.py

from sqlalchemy.inspection import inspect
from core.exceptions.handler import APIException, DatabaseException
from core.messages import *
from constants import *
from storage.storage_service.StorageService import *
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload, contains_eager, Load
from sqlalchemy.orm import object_session
from contextlib import contextmanager
from sqlalchemy import desc, or_, and_
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.attributes import InstrumentedAttribute
from typing import Any, List
from sqlalchemy.sql import func
import logging

logger = logging.getLogger(__name__)

# Global engine reference
_engine = None

def init_engine(db_uri):
    """Initialize the database engine once"""
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(db_uri, pool_pre_ping=True, echo=False)
            logger.info("Database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise DatabaseException(f"Database connection failed: {e}")
    return _engine

def get_engine(db_uri=None):
    """Get the database engine, creating it if necessary"""
    global _engine
    if _engine is None:
        if db_uri is None:
            from config import DB_URI
            db_uri = DB_URI
        _engine = init_engine(db_uri)
    return _engine

@contextmanager
def session_scope(engine=None):
    """Context manager for database sessions"""
    if engine is None:
        engine = get_engine()
    session = get_session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Session error: {e}")
        raise
    finally:
        session.close()

def get_session(engine, obj=None):
    """Get a session, optionally from an existing object"""
    Session = sessionmaker(bind=engine)
    if obj:
        existing_session = object_session(obj)
        if existing_session:
            return existing_session
    return Session()

# Function to add a record to a table
def add_record(engine, obj):
    with session_scope(engine) as session:
        session = get_session(engine, obj)    
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

def add_records(engine, objs):
    with session_scope(engine) as session:
        session.add_all(objs)
        session.commit()
        for obj in objs:
            session.refresh(obj)
        return objs

# Function to get all records from a table
def get_all_records(engine, model_class, serialize=False):
    with session_scope(engine) as session:
        records = session.query(model_class).all()
        if serialize:
            records = serialize_model(records)
        return records

# Function to get a record by ID from a table
def get_record_by_id(engine, model_class, id, serialize=False):
    with session_scope(engine) as session:
        data = session.query(model_class).get(id)
        if serialize and data:
            data = serialize_model(data)
        return data

def _get_attr_key(field: Any) -> str:
    """Return a canonical attribute key name for a field"""
    if isinstance(field, str):
        return field
    key = getattr(field, "key", None)
    if isinstance(key, str):
        return key
    s = str(field)
    if "." in s:
        return s.split(".")[-1]
    return s

def _resolve_attr(model, key: str):
    """Return getattr(model, key) or raise ValueError."""
    try:
        return getattr(model, key)
    except AttributeError as e:
        raise ValueError(f"Model {model} has no attribute '{key}'") from e

def build_eager_options(model_class, eager_load_depth: List[Any]):
    """
    Build SQLAlchemy eager loading options.
    """
    from sqlalchemy.orm import load_only, joinedload, selectinload
    
    options: List[Any] = []

    def process(model, fields, current_path=None):
        local_opts: List[Any] = []
        inspected = inspect(model)

        for field in fields:
            if isinstance(field, dict):
                for outer, nested_fields in field.items():
                    outer_key = _get_attr_key(outer)
                    rel_attr = _resolve_attr(model, outer_key)

                    if outer_key not in inspected.relationships:
                        raise ValueError(
                            f"Requested nested load '{outer_key}' is not a relationship on {model}"
                        )

                    # Use selectinload for better performance with nested loads
                    loader = selectinload(rel_attr)
                    
                    rel_prop = inspected.relationships[outer_key]
                    target_model = rel_prop.mapper.class_
                    
                    if nested_fields:
                        nested_opts = build_eager_options(target_model, nested_fields)
                        for nested_opt in nested_opts:
                            loader = loader.options(nested_opt)
                    
                    local_opts.append(loader)

            else:
                key = _get_attr_key(field)
                attr = _resolve_attr(model, key)

                inspected = inspect(model)
                if key in inspected.relationships:
                    local_opts.append(joinedload(attr))
                elif key in inspected.columns:
                    # Skip load_only for now to avoid complexity
                    pass
                else:
                    if key in inspected.attrs:
                        pass
                    else:
                        raise ValueError(
                            f"Field '{key}' is not a recognized relationship/column on {model}"
                        )

        return local_opts

    options.extend(process(model_class, eager_load_depth))
    return options

# Function to get objects from a table based on conditions
def get_records(engine, model_class, conditions=None, join_tables=None, eager_load_depth=None, offset=0, limit=10, serialize=False):
    with session_scope(engine) as session:
        query = session.query(model_class)

        # Join tables if specified
        if join_tables:
            for join_table in join_tables:
                query = query.join(join_table)

        # Apply conditions if specified
        if conditions:
            for attr, value in conditions.items():
                # Handle different condition formats
                if hasattr(attr, 'key'):
                    query = query.filter(attr == value)
                else:
                    # Parse string attribute like "Model.column"
                    parts = str(attr).split('.')
                    if len(parts) == 2:
                        model_attr = getattr(model_class, parts[1])
                        query = query.filter(model_attr == value)
                    else:
                        query = query.filter(getattr(model_class, attr) == value)

        # Apply eager loading
        if eager_load_depth:
            try:
                query = query.options(*build_eager_options(model_class, eager_load_depth))
            except Exception as e:
                logger.warning(f"Failed to apply eager loading: {e}")

        # Order by primary key in descending order (newest first)
        if len(list(model_class.__table__.primary_key.columns)) > 0:
            pk_column = list(model_class.__table__.primary_key.columns)[0]
            query = query.order_by(desc(pk_column))

        # Fetch all records
        records = query.offset(offset).limit(limit).all()
        
        if serialize:
            records = serialize_model(records)
        session.expunge_all()
        return records

def count_records(engine, model_class, conditions=None, join_tables=None, group_by=None):
    with session_scope(engine) as session:
        pk_col = list(model_class.__table__.primary_key.columns)[0]

        if group_by is not None and not isinstance(group_by, InstrumentedAttribute):
            raise ValueError(f"group_by must be a model column, got: {group_by}")

        if group_by is not None:
            query = session.query(group_by, func.count(pk_col))
        else:
            query = session.query(func.count(pk_col))

        query = query.select_from(model_class)

        if join_tables:
            for join_table in join_tables:
                if isinstance(join_table, InstrumentedAttribute):
                    query = query.join(join_table)
                else:
                    raise ValueError(f"join_tables must contain relationship attributes, got: {join_table}")

        if conditions:
            for attr, value in conditions.items():
                if not isinstance(attr, InstrumentedAttribute):
                    raise ValueError(f"Condition key must be a column, got: {attr}")
                query = query.filter(attr == value)

        if group_by is not None:
            query = query.group_by(group_by)
            return query.all()

        return query.scalar()

# Function to update a record in a table
def update_record(engine, obj):
    session = get_session(engine, obj)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    session.expunge(obj)
    return obj

# Function to delete a record from a table
def delete_record(engine, obj):
    session = get_session(engine, obj)
    session.delete(obj)
    session.commit()
    return True

def delete_record_by_id(engine, model_class, id):
    with session_scope(engine) as session:
        obj = session.query(model_class).get(id)
        if obj:
            session.delete(obj)
            session.commit()
            return True
        return False

from sqlalchemy.orm import aliased
from sqlalchemy.inspection import inspect

def resolve_attr_recursive(model, field_path):
    """Takes e.g. 'product_provider.provider_name' and returns the actual SQLAlchemy attribute"""
    parts = field_path.split(".")
    current_model = model
    joins = []
    
    for i, part in enumerate(parts):
        mapper = inspect(current_model)

        if i == len(parts) - 1:
            if part in mapper.columns:
                return getattr(current_model, part), joins
            raise ValueError(f"Column '{part}' not found on {current_model}")

        if part not in mapper.relationships:
            raise ValueError(f"Relationship '{part}' not found on {current_model}")

        rel = mapper.relationships[part]
        joins.append(getattr(current_model, part))
        current_model = rel.mapper.class_

    raise RuntimeError("Invalid path parsing")

def search_records(
    engine,
    model_class,
    join_tables,
    eager_load_depth,
    search_query=None,
    search_fields=None,
    offset=0,
    limit=20
):
    with session_scope(engine) as session:
        query = session.query(model_class)

        if search_query and search_fields:
            keywords = search_query.split()
            
            for kw in keywords:
                or_conditions = []
                required_joins = []

                for field_path in search_fields:
                    attr, joins = resolve_attr_recursive(model_class, field_path)

                    for j in joins:
                        required_joins.append(j)

                    or_conditions.append(attr.ilike(f"%{kw}%"))

                for j in required_joins:
                    query = query.join(j, isouter=True)

                query = query.filter(or_(*or_conditions))

        if join_tables:
            for join_table in join_tables:
                query = query.join(join_table)
                
        if eager_load_depth:
            query = query.options(*build_eager_options(model_class, eager_load_depth))

        pk_column = list(model_class.__table__.primary_key.columns)[0]
        query = query.order_by(desc(pk_column)).offset(offset).limit(limit)

        records = query.all()
        return records

def get_records_by_filter(
    engine,
    model_class,
    conditions=None,
    ordering_attr=None,
    join_tables=None,
    labeled_attrs=None,
    selected_fields=None,
    eager_load_depth=None,
    offset=0,
    limit=20
):
    with session_scope(engine) as session:
        query_elements = []

        if selected_fields:
            query_elements.extend(selected_fields)
        elif not selected_fields:
            query_elements.append(model_class)

        if labeled_attrs:
            query_elements.extend(labeled_attrs)

        query = session.query(*query_elements)

        if join_tables:
            for join_table in join_tables:
                query = query.join(join_table)
                
        if eager_load_depth and model_class in query_elements:
            query = query.options(*build_eager_options(model_class, eager_load_depth))

        if conditions:
            query = query.filter(and_(*conditions))

        if ordering_attr:
            for attr in ordering_attr:
                query = query.order_by(attr)

        query = query.offset(offset).limit(limit)

        records = query.all()

        results = []
        for row in records:
            if hasattr(row, "_mapping"):
                results.append(dict(row._mapping))
            elif hasattr(row, '__table__'):
                results.append(serialize_model(row))
            else:
                results.append(row)

        return results

def serialize_model(obj):
    """Convert SQLAlchemy model instance to dictionary."""
    if obj is None:
        return None
    if isinstance(obj, list):
        return [serialize_model(item) for item in obj]
    if isinstance(obj, dict):
        return {k: serialize_model(v) for k, v in obj.items()}
    if hasattr(obj, '__table__'):
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, type(None))):
                continue
            result[column.name] = value
        return result
    return obj