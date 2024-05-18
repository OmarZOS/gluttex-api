
# using insert_or_complete_or_raise imposes these lines:
# # code,obj,msg = insert_or_complete_or_raise(obj)
# #     if (code == 1): return msg

import server.storage.storage_broker as storage_broker

def insert_or_complete_or_raise(obj):
    data = None
    try:
        data = storage_broker.insert_record(obj)
    except Exception as e:
        return (1,None,f"An exception occurred with {type(data)} "+str(e))
    # object found, fetched and returned
    return (0,data,"Object found, fetched and returned")

def delete_record_from_api(obj):
    data = storage_broker.delete_record(obj)
    return data

def get_existent_object(obj):
    obj = storage_broker.get(obj)
    return obj

