# This component is responsible for choosing the right place
# to insert/fetch data in/from the most appropriate
# store, it can support multiple
# storage engines, the insertion/fetch logic is in here

from constants import DB_URI
import storage.wrappers.sql_wrapper as medicom_store

def insert_record(item):
    try:
        engine = medicom_store.get_engine(DB_URI)
    except:
        raise Exception('An exception occurred while connecting to the database.')
    res = medicom_store.add_record(engine,item)
    return res

def get(table,conditions=None, join_tables=None,eagerjoinload=None):
    try:
        engine = medicom_store.get_engine(DB_URI)
    except:
        raise Exception('An exception occurred while connecting to the database.')
    res = medicom_store.get_records(engine,table,conditions,join_tables,eagerjoinload)
    return res

def get(table,conditions=None, join_tables=None,eagerjoinload=None):
    try:
        engine = medicom_store.get_engine(DB_URI)
    except:
        raise Exception('An exception occurred while connecting to the database.')
    res = medicom_store.get_records(engine,table,conditions,join_tables,eagerjoinload)
    return res

def delete_record(item):
    try:
        engine = medicom_store.get_engine(DB_URI)
    except:
        raise Exception('An exception occurred while connecting to the database.')
    medicom_store.delete_record(engine,item)
    

def delete_record_by_id(table,id):
    try:
        engine = medicom_store.get_engine(DB_URI)
    except:
        raise Exception('An exception occurred while connecting to the database.')
    res = medicom_store.delete_record_by_id(engine,table,id)
    return res
# for meta search engines like elasticsearch
def insert_metadata(args):
    pass

def search_for(search_tokens):
    pass
