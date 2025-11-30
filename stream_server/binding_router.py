




from fastapi import APIRouter, HTTPException, Depends

from typing import List, Optional
from lib import logger
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
    # current_user: dict = Depends(get_current_user)
):
    """
    Get all current bindings for user's queue
    """
    try:
        queue_name = f"user.{user_id}.queue"
        bindings = await manager.get_queue_bindings(queue_name)
        
        return [
            BindingInfo(
                routing_key=binding['routing_key'],
                queue_name=binding['queue'],
                binding_key=binding['routing_key']  # In RabbitMQ, binding key = routing key for direct exchanges
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
    

