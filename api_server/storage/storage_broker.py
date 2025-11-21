# This component is responsible for choosing the right place
# to insert/fetch data in/from the most appropriate
# store, it can support multiple
# storage engines, the insertion/fetch logic is in here

from core.messages import *
from core.exception_handler import APIException
from constants import DB_URI
import storage.wrappers.sql_wrapper as medicom_store

def insert_record(item):
    engine = medicom_store.get_engine(DB_URI)
    res = medicom_store.add_record(engine,item)
    return res

def get(table,conditions=None, join_tables=None,eager_load_depth=None,offset=0, limit=10):
    engine = medicom_store.get_engine(DB_URI)
    res = medicom_store.get_records(engine,table,conditions,join_tables,eager_load_depth,offset,limit)
    return res

def count(table,conditions=None, join_tables=None):
    engine = medicom_store.get_engine(DB_URI)
    res = medicom_store.count_records(engine,table,conditions,join_tables)
    return res

def delete_record(item):
    engine = medicom_store.get_engine(DB_URI)
    medicom_store.delete_record(engine,item)

def update_record(item):
    engine = medicom_store.get_engine(DB_URI)
    return medicom_store.update_record(engine,item)

def delete_record_by_id(table,id):
    engine = medicom_store.get_engine(DB_URI)
    res = medicom_store.delete_record_by_id(engine,table,id)
    return res

def search_records(table,
    join_tables=None,
    eager_load_depth = None,
    search_query=None,
    search_fields=None,
    offset= 0,
    limit = 20
    ):
    engine = medicom_store.get_engine(DB_URI)
    res = medicom_store.search_records(engine,table,join_tables,eager_load_depth,search_query,search_fields,offset,limit)
    return res

def search_by_location(
    table,
    join_tables,
    conditions,
    labeled_attrs,
    ordering_attr,
    selected_fields,
    eager_load_depth,
    offset= 0,
    limit = 20
    ):
    engine = medicom_store.get_engine(DB_URI)
    return medicom_store.get_records_by_filter(engine,table
        ,join_tables=join_tables
        ,conditions=conditions
        ,labeled_attrs=labeled_attrs
        ,ordering_attr=ordering_attr
        ,selected_fields=selected_fields
        ,eager_load_depth=eager_load_depth
        ,offset=offset
        ,limit=limit)


# def search_for(search_tokens):
#     pass
