import asyncio
import json
import logging
import os

import time
import uuid
from typing import Any, Callable, Dict, Optional, Set
import signal
import psutil
import orjson

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
# from prometheus_client import Counter, Histogram, Gauge, generate_latest
from pydantic import  Field
from pydantic_settings import BaseSettings
from lib import OptimizedPikaConsumerThread, settings,ConnectionManager, manager,logger
from binding_router import binding_router

# Configure structured logging

# Metrics for monitoring
# WS_CONNECTIONS = Gauge('websocket_active_connections', 'Active WebSocket connections')
# RABBIT_MESSAGES_RECEIVED = Counter('rabbitmq_messages_received_total', 'Total messages received from RabbitMQ')
# RABBIT_MESSAGES_SENT = Counter('rabbitmq_messages_sent_total', 'Total messages sent to WebSocket clients')
# MESSAGE_PROCESSING_TIME = Histogram('message_processing_seconds', 'Time spent processing messages')
# CONNECTION_ERRORS = Counter('connection_errors_total', 'Total connection errors')

# Connection manager for graceful shutdown

app = FastAPI(
    openapi_url="/stream/openapi.json",  # Move Openstream to `/stream/openapi.json`
    docs_url="/stream/docs",  # Keep Swagger UI at `/docs`
    redoc_url="/stream/redoc"  # Keep ReDoc at `/redoc`
)

app.include_router(binding_router,prefix="/stream", )

# Health check endpoint
@app.get("/stream/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        # "active_connections": WS_CONNECTIONS._value.get(),
        "memory_usage": psutil.Process().memory_info().rss / 1024 / 1024
    }




@app.websocket("/stream/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()

    # Always reuse the same queue
    queue_name = manager.get_or_create_queue(client_id)

    incoming_q = asyncio.Queue(maxsize=2000)

    # Start consumer once per client
    if not manager.has_consumer(queue_name):
        consumer = OptimizedPikaConsumerThread(
            queue_name=queue_name,
            asyncio_queue=incoming_q,
            on_error=lambda exc: logger.error(exc),
            prefetch_count=settings.prefetch_count
        )
        consumer.start()
        manager.register_consumer(queue_name, consumer)

    # Add this websocket to the client group
    manager.add_websocket(client_id, websocket)

    # Send connection info
    await websocket.send_text(json.dumps({
        "type": "connected",
        "queue": queue_name,
        "client_id": client_id
    }))

    try:
        # Main loop
        while True:
            msg = await incoming_q.get()
            await websocket.send_text(json.dumps(msg))

    except WebSocketDisconnect:
        pass

    finally:
        # Remove only this socket, keep queue alive if others remain
        manager.remove_websocket(client_id, websocket)

# @app.get("/stream")
# async def root():
#     return {"message": "WebSocket-RabbitMQ Bridge is running"}



# @app.websocket("/stream/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: str):
#     await websocket.accept()

#     # Always reuse the same queue
#     queue_name = manager.get_or_create_queue(client_id)

#     incoming_q = asyncio.Queue(maxsize=2000)

#     # Start consumer once per client
#     if not manager.has_consumer(queue_name):
#         consumer = OptimizedPikaConsumerThread(
#             queue_name=queue_name,
#             asyncio_queue=incoming_q,
#             on_error=lambda exc: logger.error(exc),
#             prefetch_count=settings.prefetch_count
#         )
#         consumer.start()
#         manager.register_consumer(queue_name, consumer)

#     # Add this websocket to the client group
#     manager.add_websocket(client_id, websocket)

#     # Send connection info
#     await websocket.send_text(json.dumps({
#         "type": "connected",
#         "queue": queue_name,
#         "client_id": client_id
#     }))

#     try:
#         # Main loop
#         while True:
#             msg = await incoming_q.get()
#             await websocket.send_text(msg)

#     except WebSocketDisconnect:
#         pass

#     finally:
#         # Remove only this socket, keep queue alive if others remain
#         manager.remove_websocket(client_id, websocket)


# async def _send_websocket_message(websocket: WebSocket, message: Any, queue_name: str):
#     """Send message to WebSocket with error handling"""
#     try:
#         payload = orjson.dumps({
#             "type": "message",
#             "from_queue": queue_name,
#             "payload": message,
#             "timestamp": time.time()
#         }).decode()
        
#         await websocket.send_text(payload)
        
#     except Exception as exc:
#         logger.error(f"Failed to send message to {queue_name}: {exc}")
#         raise WebSocketDisconnect()

# async def _cleanup_connection(queue_name: str, consumer: OptimizedPikaConsumerThread, websocket: WebSocket):
#     """Clean up connection resources"""
#     try:
#         consumer.stop()
#     except Exception as e:
#         logger.error(f"Error stopping consumer for {queue_name}: {e}")
    
#     manager.unregister_consumer(queue_name)
#     manager.disconnect(queue_name)
    
#     try:
#         await websocket.close()
#     except Exception:
#         pass

# # Health check endpoint
# @app.get("/stream/health")
# async def health_check():
#     return {
#         "status": "healthy", 
#         "timestamp": time.time(),
#         "active_connections": len(manager.active_connections)
#     }