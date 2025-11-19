from sqlalchemy.inspection import inspect
from core.exception_handler import APIException
from core.messages import *
from constants import *
from storage.storage_service.StorageService import *
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload,contains_eager,Load
from sqlalchemy.orm import object_session
from contextlib import contextmanager
from sqlalchemy import desc, or_, and_
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.attributes import InstrumentedAttribute
from typing import Any, List

@contextmanager
def session_scope(engine):
    session = get_session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# engine = create_engine(DB_URI)
def get_engine(db_uri):
    try:
        engine = create_engine(db_uri)
        return engine
    except Exception as e:
        raise APIException(status=HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
                           ,code=DATABASE_ERROR
                           ,details=f'{str(e)}')

def get_session(engine, obj=None):
    Session = sessionmaker(bind=engine)
    if obj:
        existing_session = object_session(obj)
        if existing_session:
            return existing_session
    return Session()

# Function to add a record to a table
def add_record(engine, obj):
    with session_scope(engine) as session:
        session = get_session(engine,obj)    
        # Add the new object to the session and commit
        session.add(obj)
        session.commit()
        session.refresh(obj)
        # session.expunge(obj) 
        # Return the added object
        return obj

def add_records(engine, objs):
    with session_scope(engine) as session:
        session.add_all(objs)
        session.commit()
        for obj in objs:
            session.refresh(obj)
            # # # session.expunge(obj)  # Expunge each object individually
        return objs

# Function to get all records from a table
def get_all_records(engine,model_class):
    with session_scope(engine) as session:
        session = get_session(engine)
        return session.query(model_class).all()

# Function to get an record by ID from a table
def get_record_by_id(engine,model_class, id):
    with session_scope(engine) as session:
        data = session.query(model_class).get(id)
        # # # session.expunge(data)
        return data



def _get_attr_key(field: Any) -> str:
    """
    Return a canonical attribute key name for a field that can be:
      - a string (attribute name)
      - an InstrumentedAttribute (has .key)
      - a column or descriptor where str(...) ends with '.<name>'
    """
    if isinstance(field, str):
        return field

    # typical InstrumentedAttribute / ColumnElement have .key
    key = getattr(field, "key", None)
    if isinstance(key, str):
        return key

    # fallback: try to parse string representation
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

    `eager_load_depth` can contain:
      - model_attr (e.g. ManagementRule.product_provider)
      - column attr (e.g. ManagementRule.management_rule_code)
      - string attr name "product_provider"
      - nested dicts { relationship_attr_or_name: [ nested_fields... ] }

    Returns a list of loader options suitable for `.options(*...)`.
    """
    options: List[Any] = []

    def process(model, fields):
        local_opts: List[Any] = []
        inspected = inspect(model)

        for field in fields:
            # nested dict: { relationship: [ nested_fields ] }
            if isinstance(field, dict):
                for outer, nested_fields in field.items():
                    outer_key = _get_attr_key(outer)
                    rel_attr = _resolve_attr(model, outer_key)

                    # ensure it's a relationship
                    if outer_key not in inspected.relationships:
                        raise ValueError(
                            f"Requested nested load '{outer_key}' is not a relationship on {model}"
                        )

                    # start joinedload on that relationship attribute
                    loader = joinedload(rel_attr)

                    # get target model for nested recursion
                    rel_prop = inspected.relationships[outer_key]
                    target_model = rel_prop.mapper.class_

                    # recurse to build nested options for the target model
                    nested_opts = process(target_model, nested_fields)
                    for nopt in nested_opts:
                        loader = loader.options(nopt)

                    local_opts.append(loader)

            else:
                # single field (could be column or relationship)
                key = _get_attr_key(field)
                attr = _resolve_attr(model, key)

                # re-check after resolution
                inspected = inspect(model)
                if key in inspected.relationships:
                    # relationship -> eager load the whole relationship
                    local_opts.append(joinedload(attr))
                elif key in inspected.columns:
                    # column -> load only this column
                    local_opts.append(Load(model).load_only(attr))
                else:
                    # not found in relationships or columns, try to be permissive:
                    # sometimes hybrid properties or column_property names appear only in mapper.attrs
                    if key in inspected.attrs:
                        # If it's not a relationship, loading the attribute may be skipped (no loader)
                        # But we attempt load_only for safety if it's a column-like attr
                        local_opts.append(Load(model).load_only(attr))
                    else:
                        raise ValueError(
                            f"Field '{key}' is not a recognized relationship/column on {model}"
                        )

        return local_opts

    options.extend(process(model_class, eager_load_depth))
    return options

# Function to get objects from a table based on conditions
def get_records(engine, model_class, conditions=None, join_tables=None, eager_load_depth=None, offset=0, limit=10):
    with session_scope(engine) as session:
        query = session.query(model_class)

        # Join tables if specified
        if join_tables:
            for join_table in join_tables:
                query = query.join(join_table)

        # Apply conditions if specified
        if conditions:
            for attr, value in conditions.items():
                query = query.filter(getattr(model_class, str(attr).split(".")[1]) == str(value))

        # Use joinedload to eager load relationships with specified depth
        """
    Recursively apply eager loading.
    Example:
        eager_load_depth = [
            AppUser.app_user_type,
            AppUser.app_user_person,
            {AppUser.app_user_person: [Person.person_blood_type_id]}
        ]
    """
        # Apply loaders to the query
        if eager_load_depth :
            query = query.options(*build_eager_options(model_class,eager_load_depth))

        # Order by primary key in descending order (newest first)
        pk_column = list(model_class.__table__.primary_key.columns)[0]
        query = query.order_by(desc(pk_column))

        # Fetch all records
        records = query.offset(offset).limit(limit).all()

        session.expunge_all()
        return records

# Function to update an record in a table
def update_record(engine,obj):
    session = get_session(engine, obj)
    session.add(obj)  # Make sure the object is persistent
    session.commit()  # Commit the session to save the changes
    session.refresh(obj)  # Refresh the object to get the updated state
    session.expunge(obj)  # Optionally expunge the object from the session
    return obj

# Function to delete an record from a table
def delete_record(engine,obj):
    session = get_session(engine, obj)
    data = session.delete(obj)
    # session.expunge(obj)
    session.commit()
    return data

def delete_record_by_id(engine,model_class, id):

    # Get the primary key column name
    primary_key_name = model_class.__table__.primary_key.columns.keys()[0]

    session = get_session(engine)
    data = session.delete()   #.query(model_class).filter(primary_key_name == str(id)).delete()
    # # # session.expunge(data)
    return data


def search_records(
    engine,
    model_class,
    join_tables,
    eager_load_depth,
    search_query=None,
    search_fields=None,
    offset= 0,
    limit = 20
):
    with session_scope(engine) as session:
        query = session.query(model_class)
        # Generic search across multiple fields


        if search_query and search_fields:
            keywords = search_query.split()
            for kw in keywords:
                conditions = [
                    getattr(model_class, str(field).split(".")[1]).ilike(f"%{kw}%")
                    for field in search_fields
                ]
                query = query.filter(or_(*conditions))
        
        if join_tables:
            for join_table in join_tables:
                query = query.join(join_table)
        # Apply loaders to the query
        if eager_load_depth:
            query = query.options(*build_eager_options(model_class,eager_load_depth))

        # Order by primary key in descending order (newest first)
        pk_column = list(model_class.__table__.primary_key.columns)[0]
        query = query.order_by(desc(pk_column)).offset(offset).limit(limit)

        # Fetch records
        records = query.all()

        session.expunge_all()
        return records
    


def get_records_by_filter(
    engine,
    model_class,
    conditions=None,
    ordering_attr=None,
    join_tables=None,
    labeled_attrs=None,
    selected_fields=None,
    eager_load_depth= None,
    offset=0,
    limit=20
):
    with session_scope(engine) as session:
        # Base query
        query_elements = []

        # If selected_fields provided, use them instead of full model
        if selected_fields:
            # query_elements.append(model_class)
            query_elements.extend(selected_fields)

        # Always include model if nothing is selected
        elif not selected_fields:
            query_elements.append(model_class)

        # Add labeled attributes if any
        if labeled_attrs:
            query_elements.extend(labeled_attrs)

        query = session.query(*query_elements)

        # Join tables if specified
        if join_tables:
            for join_table in join_tables:
                query = query.join(join_table)
        # Apply loaders to the query
        if (eager_load_depth is not None) and (model_class in query_elements):
            query = query.options(*build_eager_options(model_class,eager_load_depth))

        # Apply filters
        if conditions:
            query = query.filter(and_(*conditions))
        

        # Apply ordering
        if ordering_attr:
            for attr in ordering_attr:
                query = query.order_by(attr)

        
        # Apply offset and limit
        query = query.offset(offset).limit(limit)

        # Fetch results
        records = query.all()
        session.expunge_all()

        # Convert rows to dicts when multiple entities are queried
        results = []
        try:
            for row in records:
                if hasattr(row, "_mapping"):  
                    results.append(dict(row._mapping))  
                else:
                    results.append(row)
        except:
            pass

        return results
    