




from fastapi import APIRouter, HTTPException, Depends

from typing import List, Optional

import pika
from lib import AMQP_HOST, AMQP_PASS, AMQP_PORT, AMQP_USER, AMQP_VIRTUAL_HOST, logger
from lib import WebSocketConnectionManager
from api_models import MultipleBindingRequest, BindingRequest, BindingInfo, BindingResponse

# Router for binding management

binding_router = APIRouter( tags=["queue-bindings"])
manager = WebSocketConnectionManager()

# ----------------- Binding Management Endpoints -----------------

@binding_router.post("/user/{user_id}/bind", response_model=BindingResponse)
async def bind_user_queue(
    user_id: int,
    binding: BindingRequest,
    # current_user: dict = Depends(get_current_user)  # Your auth dependency
):
    """
    Bind user's queue to a user-specific routing key
    Routing key format: user.{user_id}.*
    """
    try:
        # User can only bind to their own user routing key
        # if not binding.routing_key.startswith(f"user.{user_id}"):
        #     raise HTTPException(
        #         status_code=403, 
        #         detail="Can only bind to your own user routing keys"
        #     )
        
        queue_name = binding.queue_name or f"user.{user_id}.queue"
        
        # Ensure queue exists and bind it
        success = await manager.bind_queue_to_routing_key(
            queue_name=queue_name,
            routing_key=binding.routing_key
        )
        
        if success:
            return BindingResponse(
                success=True,
                message=f"Successfully bound queue to {binding.routing_key}",
                queue_name=queue_name
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create binding")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error binding user queue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@binding_router.post("/supplier/{user_id}/{supplier_id}/bind", response_model=BindingResponse)
async def bind_supplier_queue(
    user_id: int,
    supplier_id: int,
    binding: BindingRequest,
    # current_user: dict = Depends(get_current_user)
):
    """
    Bind queue to supplier-specific routing key
    Routing key format: supplier.{supplier_id}.*
    """
    try:
        # Validate supplier access (implement your own logic)
        # if not await has_supplier_access(current_user, supplier_id):
        #     raise HTTPException(status_code=403, detail="No access to this supplier")
        
        queue_name = binding.queue_name or f"user.{user_id}.queue"
        
        success = await manager.bind_queue_to_routing_key(
            queue_name=queue_name,
            routing_key=binding.routing_key
        )
        
        if success:
            return BindingResponse(
                success=True,
                message=f"Successfully bound to supplier routing key {binding.routing_key}",
                queue_name=queue_name
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create binding")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error binding supplier queue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@binding_router.post("/org/{user_id}/{org_id}/bind", response_model=BindingResponse)
async def bind_organization_queue(
    user_id: int,
    org_id: int,
    binding: BindingRequest,
    # current_user: dict = Depends(get_current_user)
):
    """
    Bind queue to organization-specific routing key
    Routing key format: org.{org_id}.*
    """
    try:
        # Validate organization access
        # if not await has_org_access(current_user, org_id):
        #     raise HTTPException(status_code=403, detail="No access to this organization")
        
        queue_name = binding.queue_name or f"user.{user_id}.queue"
        
        success = await manager.bind_queue_to_routing_key(
            queue_name=queue_name,
            routing_key=binding.routing_key
        )
        
        if success:
            return BindingResponse(
                success=True,
                message=f"Successfully bound to organization routing key {binding.routing_key}",
                queue_name=queue_name
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create binding")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error binding organization queue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@binding_router.post("/product/{user_id}/{product_id}/bind", response_model=BindingResponse)
async def bind_product_queue(
    user_id:int,
    product_id: int,
    binding: BindingRequest,
    # current_user: dict = Depends(get_current_user)
):
    """
    Bind queue to product-specific routing key
    Routing key format: product.{product_id}.*
    """
    try:
        # Validate product access
        # if not await has_product_access(current_user, product_id):
        #     raise HTTPException(status_code=403, detail="No access to this product")
        
        queue_name = binding.queue_name or f"user.{user_id}.queue"
        
        success = await manager.bind_queue_to_routing_key(
            queue_name=queue_name,
            routing_key=binding.routing_key
        )
        
        if success:
            return BindingResponse(
                success=True,
                message=f"Successfully bound to product routing key {binding.routing_key}",
                queue_name=queue_name
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create binding")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error binding product queue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@binding_router.post("/user/{user_id}/bind-multiple", response_model=BindingResponse)
async def bind_multiple_routing_keys(
    user_id: int,
    binding_request: MultipleBindingRequest,
    # current_user: dict = Depends(get_current_user)
):
    """
    Bind user's queue to multiple routing keys at once
    """
    try:
        queue_name = binding_request.queue_name or f"user.{user_id}.queue"
        success_count = 0
        
        for routing_key in binding_request.routing_keys:
            try:
                # Validate user can bind to this routing key
                # if (routing_key.startswith(f"user.{user_id}") or 
                #     await can_user_bind_to_routing_key(current_user, routing_key)):
                    
                success = await manager.bind_queue_to_routing_key(
                    queue_name=queue_name,
                    routing_key=routing_key
                )
                if success:
                    success_count += 1
                        
            except Exception as e:
                logger.warning(f"Failed to bind {routing_key}: {e}")
                continue
        
        return BindingResponse(
            success=success_count > 0,
            message=f"Successfully bound {success_count}/{len(binding_request.routing_keys)} routing keys",
            binding_count=success_count,
            queue_name=queue_name
        )
        
    except Exception as e:
        logger.error(f"Error in multiple binding: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@binding_router.delete("/user/{user_id}/unbind", response_model=BindingResponse)
async def unbind_routing_key(
    user_id: int,
    binding: BindingRequest,
    # current_user: dict = Depends(get_current_user)
):
    """
    Remove binding between queue and routing key
    """
    try:
        queue_name = binding.queue_name or f"user.{user_id}.queue"
        
        success = await manager.unbind_queue_from_routing_key(
            queue_name=queue_name,
            routing_key=binding.routing_key
        )
        
        if success:
            return BindingResponse(
                success=True,
                message=f"Successfully unbound from {binding.routing_key}",
                queue_name=queue_name
            )
        else:
            raise HTTPException(status_code=404, detail="Binding not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unbinding queue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@binding_router.get("/user/{user_id}/bindings", response_model=List[BindingInfo])
async def get_user_bindings(
    user_id: int,
):
    """
    Get all current bindings for user's queue
    """
    try:
        # Use the SAME queue name format as your WebSocket server
        queue_name = f"user.{user_id}.queue"
        bindings = await manager.get_queue_bindings(queue_name)
        
        return [
            BindingInfo(
                routing_key=binding.get('routing_key', ''),
                queue_name=binding.get('queue', queue_name),
                binding_key=binding.get('routing_key', '')
            )
            for binding in bindings
        ]
        
    except Exception as e:
        logger.error(f"Error getting user bindings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@binding_router.get("/routing-key/{routing_key}/subscribers")
async def get_routing_key_subscribers(routing_key: str):
    """
    Get all queues subscribed to a specific routing key
    (Admin/management endpoint)
    """
    try:
        subscribers = await manager.get_routing_key_subscribers(routing_key)
        return {"routing_key": routing_key, "subscribers": subscribers}
        
    except Exception as e:
        logger.error(f"Error getting routing key subscribers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


@binding_router.get("/debug/queues")
async def debug_list_all_queues():
    """Debug endpoint to list all queues and their bindings"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=AMQP_HOST,
                port=AMQP_PORT,
                virtual_host=AMQP_VIRTUAL_HOST,
                credentials=pika.PlainCredentials(AMQP_USER, AMQP_PASS)
            )
        )
        channel = connection.channel()
        
        # List all queues
        queues = channel.queue_declare(queue='', passive=False, durable=True, exclusive=True)
        
        # Get all queues using management API
        import aiohttp
        import base64
        
        credentials = base64.b64encode(f"{AMQP_USER}:{AMQP_PASS}".encode()).decode()
        
        # Get all queues
        async with aiohttp.ClientSession() as session:
            # List all queues
            queues_url = f"http://{AMQP_HOST}:15672/api/queues/{AMQP_VIRTUAL_HOST}"
            headers = {"Authorization": f"Basic {credentials}"}
            
            async with session.get(queues_url, headers=headers) as resp:
                if resp.status == 200:
                    all_queues = await resp.json()
                    
                    result = []
                    for queue in all_queues:
                        queue_name = queue.get('name')
                        # Get bindings for each queue
                        bindings_url = f"http://{AMQP_HOST}:15672/api/queues/{AMQP_VIRTUAL_HOST}/{queue_name}/bindings"
                        async with session.get(bindings_url, headers=headers) as bind_resp:
                            if bind_resp.status == 200:
                                bindings = await bind_resp.json()
                                result.append({
                                    "queue_name": queue_name,
                                    "messages": queue.get('messages', 0),
                                    "consumers": queue.get('consumers', 0),
                                    "bindings": [
                                        {
                                            "routing_key": b.get('routing_key'),
                                            "source_exchange": b.get('source')
                                        }
                                        for b in bindings
                                    ]
                                })
                    
                    connection.close()
                    return {"queues": result}
        
        connection.close()
        return {"error": "Could not fetch queues"}
        
    except Exception as e:
        logger.error(f"Debug error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@binding_router.get("/debug/user/{user_id}/diagnose")
async def diagnose_user_queue(user_id: int):
    """Diagnose what's wrong with user's queue"""
    try:
        queue_name = f"user.{user_id}.queue"
        
        import aiohttp
        import base64
        
        credentials = base64.b64encode(f"{AMQP_USER}:{AMQP_PASS}".encode()).decode()
        headers = {"Authorization": f"Basic {credentials}"}
        
        results = {
            "user_id": user_id,
            "queue_name": queue_name,
            "queue_exists": False,
            "bindings": [],
            "possible_matches": []
        }
        
        async with aiohttp.ClientSession() as session:
            # Check if queue exists
            queue_url = f"http://{AMQP_HOST}:15672/api/queues/{AMQP_VIRTUAL_HOST}/{queue_name}"
            async with session.get(queue_url, headers=headers) as resp:
                if resp.status == 200:
                    queue_info = await resp.json()
                    results["queue_exists"] = True
                    results["messages"] = queue_info.get('messages', 0)
                    results["consumers"] = queue_info.get('consumers', 0)
                    
                    # Get bindings
                    bindings_url = f"http://{AMQP_HOST}:15672/api/queues/{AMQP_VIRTUAL_HOST}/{queue_name}/bindings"
                    async with session.get(bindings_url, headers=headers) as bind_resp:
                        if bind_resp.status == 200:
                            results["bindings"] = await bind_resp.json()
                else:
                    # Queue doesn't exist, look for similar queues
                    all_queues_url = f"http://{AMQP_HOST}:15672/api/queues/{AMQP_VIRTUAL_HOST}"
                    async with session.get(all_queues_url, headers=headers) as all_resp:
                        if all_resp.status == 200:
                            all_queues = await all_resp.json()
                            results["possible_matches"] = [
                                q.get('name') for q in all_queues 
                                if 'user' in q.get('name', '') and str(user_id) in q.get('name', '')
                            ]
        
        return results
        
    except Exception as e:
        logger.error(f"Diagnose error: {e}")
        return {"error": str(e)}
    
@binding_router.get("/debug/manager-config")
async def debug_manager_config():
    """Debug endpoint to see what exchange the manager is using"""
    try:
        # Try to inspect what exchange the manager binds to
        # This requires you to add a getter method to your manager
        return {
            "manager_exchange": getattr(manager, 'exchange_name', 'unknown'),
            "manager_exchange_type": getattr(manager, 'exchange_type', 'unknown'),
            "note": "Make sure these match 'user_notifications' and 'direct'"
        }
    except Exception as e:
        return {"error": str(e)}