
# using insert_or_complete_or_raise imposes these lines:
# # code,obj,msg = insert_or_complete_or_raise(obj)
# #     if (code == 1): return msg

from core.exception_handler import APIException
from core.messages import *
import storage.storage_broker as storage_broker

def insert_or_complete_or_raise(obj):
    data = storage_broker.insert_record(obj)
    return data

def delete_record_from_api(obj):
        
    data = storage_broker.delete_record(obj)
    return data

def update_record_in_api(obj):
    data = storage_broker.update_record(obj)
    return data

def get_existent_object(obj):
    obj = storage_broker.get(obj)
    return obj

