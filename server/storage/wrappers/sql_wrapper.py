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
    Session = sessionmaker(bind=engine)
    if object:        
        # Return the session if the object is already associated with one
        existing_session = object_session(object)
        if existing_session:
            return existing_session

    # Create the database engine and session
    return Session()

# Function to add a record to a table
def add_record(engine, obj):
    session = get_session(engine,obj)    
    # Add the new object to the session and commit
    session.add(obj)
    session.commit()
    session.refresh(obj)
    session.expunge(obj) 
    # Return the added object
    return obj

def add_records(engine, objs):
    session = get_session(engine)
    session.add_all(objs)
    session.commit()
    for obj in objs:
        session.refresh(obj)
        # # # session.expunge(obj)  # Expunge each object individually
    return objs

# Function to get all records from a table
def get_all_records(engine,model_class):
    session = get_session(engine)
    return session.query(model_class).all()

# Function to get an record by ID from a table
def get_record_by_id(engine,model_class, id):
    session = get_session(engine)
    data = session.query(model_class).get(id)
    # # # session.expunge(data)
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

    # # Expunge the results
    # session.expunge_all()

    return records

# Function to update an record in a table
def update_record(engine,obj):
    session = get_session(engine, obj)
    session.commit()
    session.refresh(obj)
    # # session.expunge(obj)
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