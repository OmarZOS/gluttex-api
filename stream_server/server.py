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
from lib import OptimizedPikaConsumerThread, create_consumer, ConnectionManager, manager,logger
from binding_router import binding_router

def get_or_create_consumer(queue_name: str, incoming_q):
    if not manager.has_consumer(queue_name):
        consumer = create_consumer(
            queue_name=queue_name,
            asyncio_queue=incoming_q,
            on_error=lambda exc: logger.error(exc),
            prefetch_count=50
        )
        manager.register_consumer(queue_name, consumer)


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

    # create consumer if needed
    get_or_create_consumer(queue_name, incoming_q)

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
