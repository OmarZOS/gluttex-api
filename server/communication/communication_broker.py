# This component is responsible for choosing 
# the right router to send http requests

import communication.wrappers.http as http_broker

async def send_post_request(endpoint: str, input_data: dict,flags: dict = None) :
    response = await http_broker.send_post_request(endpoint, input_data,flags)
    # print(response.content)
    return response

async def send_get_request(endpoint: str, params: dict = None,flags: dict = None) :
    response = await http_broker.send_get_request(endpoint, params=params,flags=flags)
    return response

async def send_put_request(endpoint: str, input_data: dict,flags: dict = None) :
    response = await http_broker.send_put_request(endpoint, input_data,flags)
    return response

async def send_delete_request(endpoint: str, params: dict = None,flags: dict = None) :
    response = await http_broker.send_delete_request(endpoint, params=params,flags=flags)
    return response






