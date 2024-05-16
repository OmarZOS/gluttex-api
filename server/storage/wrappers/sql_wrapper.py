from server.constants import *
from server.storage.storage_service.StorageService import *
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import object_session


# engine = create_engine(DB_URI)
def get_engine(db_uri):
    engine = create_engine(db_uri)
    return engine

def get_session(engine,object=None):
    
    if object:        
        if object_session(object):
            return object_session(object)

    # Create the database engine and session
    Session = sessionmaker(bind=engine)
    return Session()

# Function to add a record to a table
def add_record(engine, obj):
    session = get_session(engine, obj)
    obj_class = type(obj)
    obj_dict = {
        attr: value
        for attr, value in obj.__dict__.items()
        if not attr.startswith('_') and value is not None
    }
    
    # Get the primary key column name
    primary_key_name = obj_class.__table__.primary_key.columns.keys()[0]

    # Get the primary key value
    primary_key_value = obj_dict.get(primary_key_name)

    if primary_key_value is not None:
        # Check if the object with the given primary key value exists in the database
        existing_obj = session.query(obj_class).filter(getattr(obj_class, primary_key_name) == primary_key_value).first()

        if existing_obj is not None:
            # Object already exists, return the existing object
            session.expunge(existing_obj)
            return existing_obj

    # Exclude the primary key attribute from obj_dict
    obj_dict = {attr: value for attr, value in obj_dict.items() if attr != primary_key_name}
    # Create a new object with non-empty attributes
    new_obj = obj_class(**obj_dict)

    # Add the new object to the session and commit
    session.add(new_obj)
    session.commit()
    session.refresh(new_obj)
    session.expunge(new_obj) 

    # Return the added object
    return new_obj

def add_records(engine, objs):
    session = get_session(engine)
    session.add_all(objs)
    session.commit()
    for obj in objs:
        session.refresh(obj)
        session.expunge(obj)  # Expunge each object individually
    return objs

# Function to get all records from a table
def get_all_records(engine,model_class):
    session = get_session(engine)
    return session.query(model_class).all()

# Function to get an record by ID from a table
def get_record_by_id(engine,model_class, id):
    session = get_session(engine)
    data = session.query(model_class).get(id)
    # session.expunge(data)
    return data

# Function to get objects from a table based on conditions
def get_records(engine, model_class, conditions=None, join_tables=None, eager_load_depth=None):
    session = get_session(engine)
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
    if eager_load_depth is not None:
        for attr in eager_load_depth:
            query = query.options(joinedload(attr))
            
    # # Use joinedload to eager load relationships
    # query = query.options(joinedload('*'))
    # Fetch all records
    records = query.all()

    # Expunge the results
    session.expunge_all()

    return records

# Function to update an record in a table
def update_record(engine,obj):
    session = get_session(engine)
    session.commit()
    session.refresh(obj)
    session.expunge(obj)
    return obj

# Function to delete an record from a table
def delete_record(engine,obj):
    session = get_session(engine)
    session.delete(obj)
    session.commit()
    session.expunge(obj)