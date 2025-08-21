# This component is responsible for choosing 
# the right router to send http requests

import communication.wrappers.http as https_broker

async def send_post_request(endpoint: str, json_data: dict=None, payload_data: dict=None,flags: dict = None,file: bytes=None) :
    response = await https_broker.send_post_request(endpoint,json_data, payload_data,flags,file)
    return response

async def send_get_request(endpoint: str, params: dict = None,flags: dict = None) :
    response = await https_broker.send_get_request(endpoint, params=params,flags=flags)
    return response

async def send_put_request(endpoint, input_data,flags) :
    response = await https_broker.send_put_request(endpoint, input_data,flags)
    return response

async def send_delete_request(endpoint: str, params: dict = None,flags: dict = None) :
    response = await https_broker.send_delete_request(endpoint, params=params,flags=flags)
    return response






