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


def build_eager_options(model_class, eager_load_depth):
    """
    Recursively build SQLAlchemy eager loading options.
    Supports a mix of relationships, columns, and nested dicts.
    """

    options = []

    def process(model, fields):
        local_options = []
        for field in fields:
            if isinstance(field, dict):
                # Nested dict: {relationship: [nested_fields...]}
                for rel, nested_fields in field.items():
                    rel_attr = getattr(model, rel.key if hasattr(rel, "key") else str(rel).split(".")[-1])
                    nested_loader = joinedload(rel_attr)
                    # Recurse into nested relationship
                    nested_options = process(rel.mapper.class_, nested_fields)
                    for opt in nested_options:
                        nested_loader = nested_loader.options(opt)
                    local_options.append(nested_loader)

            else:
                # Either a column or a relationship
                rel_attr = getattr(model, field.key if hasattr(field, "key") else str(field).split(".")[-1])
                prop = getattr(model, rel_attr.key).property

                if hasattr(prop, "direction"):  
                    # It's a relationship → load full relationship
                    local_options.append(joinedload(rel_attr))
                else:
                    # It's a column → load only this column
                    local_options.append(Load(model).load_only(rel_attr))

        return local_options

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
        if eager_load_depth and (model_class in query_elements):
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
    