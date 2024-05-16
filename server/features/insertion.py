
# using insert_or_complete_or_raise imposes these lines:
# # code,obj,msg = insert_or_complete_or_raise(obj)
# #     if (code == 1): return msg

import server.storage.storage_broker as storage_broker

def insert_or_complete_or_raise(obj):

    try:
        obj = storage_broker.insert_record(obj)
    except Exception as e:
        return (1,None,f"An exception occurred with {type(obj)}"+str(e))
    # Object found, fetched and returned
    return (0,obj,"Object found, fetched and returned")

def get_existent_object(obj):
    obj = storage_broker.get(obj)
    return obj

