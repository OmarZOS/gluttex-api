

import storage.storage_broker as storage_broker

def find_object_by_id(obj):
    obj_class = type(obj)
    id_attributes = {attr: getattr(obj, attr) for attr in dir(obj) if "id" in attr and getattr(obj, attr) is not None}
    id_key, id_value = next(iter(id_attributes.items()))
    # print("ID Key:", id_key)
    # print("ID Value:", id_value)
    return storage_broker.get_by_id(obj_class, id_value)


