
# using insert_or_complete_or_raise imposes these lines:
# # code,obj,msg = insert_or_complete_or_raise(obj)
# #     if (code == 1): return msg

import storage.storage_broker as storage_broker

def find_object_by_id(obj):
    obj_class = type(obj)
    id_attributes = {attr: getattr(obj, attr) for attr in dir(obj) if "Id" in attr and getattr(obj, attr) is not None}
    id_key, id_value = next(iter(id_attributes.items()))
    # print("ID Key:", id_key)
    # print("ID Value:", id_value)
    try:
        object = storage_broker.get_by_id(obj_class, id_value)
        # print("Objects:", objects)
        if object:
            return (0, object, "Found objects")
        else:
            return (1, None, f"No {obj_class.__name__} found with ID: {id_value}")
    except Exception as e:
        return (1, None, f"An exception occurred with {type(obj)}: {str(e)}")
