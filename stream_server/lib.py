from pathlib import Path
import shutil
import pika
import threading
import ssl
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from typing import Any, Callable, Dict, List, Optional, Set
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
from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict

AMQP_HOST = os.getenv("AMQP_HOST", "rabbitmq")
AMQP_PORT = os.getenv("AMQP_PORT", "5672")
AMQP_VIRTUAL_HOST = os.getenv("AMQP_VIRTUAL_HOST", "/gluttex")
AMQP_USER = os.getenv("AMQP_USER", "dev_user")
AMQP_PASS = os.getenv("AMQP_PASS", "dev_pass")



def create_consumer(queue_name, asyncio_queue, loop=None, on_error=None, prefetch_count=50):
    """Factory to create a consumer thread"""
    from lib import OptimizedPikaConsumerThread
    
    # Get the current event loop if not provided
    if loop is None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # If no running loop, create a new one or use the main loop
            # You might need to pass the loop explicitly in this case
            raise RuntimeError("Must provide loop parameter when no running loop exists")
    
    consumer = OptimizedPikaConsumerThread(
        queue_name=queue_name,
        asyncio_queue=asyncio_queue,
        loop=loop,  # Pass the loop
        on_error=on_error,
        prefetch_count=prefetch_count
    )
    consumer.start()
    return consumer




class Settings(BaseSettings):
    host: str = "rabbitmq"
    port: int = 8000
    log_level: str = "INFO"
    max_connections: int = 10000
    prefetch_count: int = 50
    heartbeat_interval: int = 30
    connection_timeout: int = 10
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",  # optional prefix
         extra="ignore" 
    )

settings: Settings | None = None

def get_settings() -> Settings:
    global settings
    if settings is None:
        settings = Settings()
    return settings

logging.basicConfig(
    level=getattr(logging, get_settings().log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('websocket_server.log') if os.getenv('LOG_TO_FILE') else logging.NullHandler()
    ]
)

logger = logging.getLogger("ws-rmq-bridge")

class OptimizedPikaConsumerThread:
    """
    Highly optimized RabbitMQ consumer with connection pooling and error handling
    """

    def __init__(
        self,
        queue_name: str,
        asyncio_queue: asyncio.Queue,
        loop: asyncio.AbstractEventLoop,  # Add loop parameter
        on_error: Optional[Callable[[Exception], None]] = None,
        prefetch_count: int = 50,
        reconnect_delay: float = 5.0,
        max_reconnect_attempts: int = 10
    ) -> None:
        self.queue_name = queue_name
        self.asyncio_queue = asyncio_queue
        self.loop = loop  # Store the event loop
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.on_error = on_error
        self.prefetch_count = prefetch_count
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
        self._reconnect_attempts = 0

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._run, 
            daemon=True,
            name=f"RabbitConsumer-{self.queue_name}"
        )
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        logger.info(f"Stopping consumer for queue {self.queue_name}")
        self._stop_event.set()
        self._cleanup_connection()
        
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning(f"Consumer thread for {self.queue_name} didn't stop gracefully")

    def _cleanup_connection(self):
        """Clean up RabbitMQ connection safely"""
        try:
            if self._channel and self._channel.is_open:
                self._channel.close()
        except Exception:
            pass
        finally:
            self._channel = None

        try:
            if self._connection and self._connection.is_open:
                self._connection.close()
        except Exception:
            pass
        finally:
            self._connection = None

    def _create_connection(self) -> bool:
        """Create RabbitMQ connection with retry logic"""
        try:
            params = pika.ConnectionParameters(
                host=AMQP_HOST,
                port=int(AMQP_PORT),
                virtual_host=AMQP_VIRTUAL_HOST,
                credentials=pika.PlainCredentials(AMQP_USER, AMQP_PASS),
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            
            if AMQP_HOST != "rabbitmq":
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                params.ssl_options = pika.SSLOptions(ssl_context, server_hostname=AMQP_HOST)
            
            self._connection = pika.BlockingConnection(params)
            self._channel = self._connection.channel()
            self._channel.basic_qos(prefetch_count=self.prefetch_count)
            
            # Use passive=True to avoid redeclaring with different settings
            try:
                self._channel.queue_declare(
                    queue=self.queue_name,
                    passive=True,
                    durable=True
                )
                logger.debug(f"Queue {self.queue_name} already exists, using existing configuration")
            except Exception:
                self._channel.queue_declare(
                    queue=self.queue_name,
                    durable=True,
                    exclusive=False,
                    auto_delete=False,
                    arguments={
                        "x-message-ttl": 604800000,
                        "x-max-priority": 10
                    }
                )
                logger.info(f"Created new queue {self.queue_name}")
            
            self._reconnect_attempts = 0
            return True
            
        except Exception as e:
            logger.error(f"Failed to create RabbitMQ connection for {self.queue_name}: {e}")
            self._reconnect_attempts += 1
            return False

    def _on_message_thread(self, channel, method, properties, body):
        """Process incoming RabbitMQ messages"""
        try:
            # Parse message
            message = orjson.loads(body)
            
            # Use threadsafe method to put message into asyncio queue
            # Instead of trying to get the event loop, use call_soon_threadsafe with the stored loop
            self.loop.call_soon_threadsafe(
                self.asyncio_queue.put_nowait, 
                message
            )
            
            # Acknowledge message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as exc:
            logger.error(f"Error processing message for {self.queue_name}: {exc}")
            try:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception:
                pass

    def _run(self) -> None:
        """Main consumer loop with reconnection logic"""
        while not self._stop_event.is_set() and self._reconnect_attempts < self.max_reconnect_attempts:
            try:
                if not self._create_connection():
                    if self._stop_event.is_set():
                        break
                    time.sleep(self.reconnect_delay)
                    continue

                logger.info(f"Started consuming from queue {self.queue_name}")
                
                # Start consuming
                self._consumer_tag = self._channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self._on_message_thread,
                    auto_ack=False,
                )

                # Main consumption loop
                while not self._stop_event.is_set():
                    try:
                        self._connection.process_data_events(time_limit=0.1)
                    except pika.exceptions.ConnectionClosedByBroker:
                        logger.warning(f"Connection closed by broker for {self.queue_name}")
                        break
                    except pika.exceptions.AMQPChannelError as e:
                        logger.error(f"Channel error for {self.queue_name}: {e}")
                        break
                    except pika.exceptions.AMQPConnectionError:
                        logger.error(f"Connection error for {self.queue_name}")
                        break
                    except Exception as e:
                        logger.error(f"Unexpected error in consumer loop for {self.queue_name}: {e}")
                        break

            except Exception as e:
                logger.error(f"Consumer error for {self.queue_name}: {e}")
                if callable(self.on_error):
                    try:
                        self.on_error(e)
                    except Exception:
                        logger.exception("Error in on_error callback")
            
            finally:
                self._cleanup_connection()
                
                if not self._stop_event.is_set():
                    delay = self.reconnect_delay * (2 ** min(self._reconnect_attempts, 5))
                    logger.info(f"Reconnecting to RabbitMQ for {self.queue_name} in {delay}s")
                    time.sleep(delay)

        logger.info(f"Consumer stopped for queue {self.queue_name}")
class ConnectionManager:
    def __init__(self):
        self.client_queue: Dict[str, str] = {}
        self.queue_consumers: Dict[str, OptimizedPikaConsumerThread] = {}
        self.client_sockets: Dict[str, Set[WebSocket]] = {}
        self._lock = threading.RLock()

    def get_or_create_queue(self, client_id: str) -> str:
        # Return existing queue if already created
        if client_id in self.client_queue:
            return self.client_queue[client_id]

        # Create new queue - use consistent naming with your binding endpoints
        queue_name = f"user.{client_id}.queue"
        self.client_queue[client_id] = queue_name
        return queue_name

    def add_websocket(self, client_id: str, websocket: WebSocket):
        with self._lock:
            if client_id not in self.client_sockets:
                self.client_sockets[client_id] = set()
            self.client_sockets[client_id].add(websocket)

    def remove_websocket(self, client_id: str, websocket: WebSocket):
        with self._lock:
            if client_id in self.client_sockets:
                self.client_sockets[client_id].discard(websocket)

                # If no more sockets -> optional queue cleanup
                if len(self.client_sockets[client_id]) == 0:
                    self._cleanup_client(client_id)

    def register_consumer(self, queue_name: str, consumer):
        with self._lock:
            self.queue_consumers[queue_name] = consumer

    def has_consumer(self, queue_name: str) -> bool:
        return queue_name in self.queue_consumers

    def unregister_consumer(self, queue_name: str):
        with self._lock:
            if queue_name in self.queue_consumers:
                del self.queue_consumers[queue_name]

    def _cleanup_client(self, client_id: str):
        """Called only when all client sockets are gone."""
        queue = self.client_queue.pop(client_id, None)
        if not queue:
            return

        consumer = self.queue_consumers.pop(queue, None)
        if consumer:
            consumer.stop(timeout=2.0)

    async def broadcast_to_client(self, client_id: str, message: str):
        """Send a message to all live sockets of this client."""
        with self._lock:
            sockets = list(self.client_sockets.get(client_id, []))

        for ws in sockets:
            try:
                await ws.send_text(message)
            except:
                # socket likely dead
                self.remove_websocket(client_id, ws)


class RabbitMQManager:
    def __init__(self):
        self.connection_params = self._get_connection_params()
        self.exchange_name = "user_notifications"
        self.exchange_type = "direct"

    def _get_connection_params(self):
        """Get RabbitMQ connection parameters"""
        params = pika.ConnectionParameters(
            host=AMQP_HOST,
            port=int(AMQP_PORT),
            virtual_host=AMQP_VIRTUAL_HOST,
            credentials=pika.PlainCredentials(AMQP_USER, AMQP_PASS),
            heartbeat=600,
            blocked_connection_timeout=300,
        )
        
        if AMQP_HOST != "rabbitmq":
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            params.ssl_options = pika.SSLOptions(ssl_context, server_hostname=AMQP_HOST)
            
        return params

    def _get_connection(self) -> pika.BlockingConnection:
        """Get RabbitMQ connection"""
        return pika.BlockingConnection(self.connection_params)

    def queue_exists(self, queue_name: str) -> bool:
        """Check if queue exists"""
        try:
            connection = self._get_connection()
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, passive=True, durable=True)
            channel.close()
            connection.close()
            return True
        except Exception:
            return False

    def create_queue(self, queue_name: str) -> bool:
        """Create a queue with proper settings matching your existing queue"""
        try:
            connection = self._get_connection()
            channel = connection.channel()
            
            channel.queue_declare(
                queue=queue_name,
                durable=True,
                exclusive=False,
                auto_delete=False,
                arguments={
                    "x-message-ttl": 604800000,
                    "x-max-priority": 10
                }
            )
            
            channel.close()
            connection.close()
            logger.info(f"Created queue {queue_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating queue {queue_name}: {e}")
            return False

    def bind_queue(self, queue_name: str, routing_key: str) -> bool:
        """Bind queue to routing key on the exchange"""
        try:
            connection = self._get_connection()
            channel = connection.channel()
            
            # Ensure exchange exists
            channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type=self.exchange_type,
                durable=True
            )
            
            # Ensure queue exists
            try:
                channel.queue_declare(queue=queue_name, passive=True)
            except Exception:
                channel.queue_declare(
                    queue=queue_name,
                    durable=True,
                    arguments={
                        "x-message-ttl": 604800000,
                        "x-max-priority": 10
                    }
                )
            
            # Create binding
            channel.queue_bind(
                exchange=self.exchange_name,
                queue=queue_name,
                routing_key=routing_key
            )
            
            channel.close()
            connection.close()
            logger.info(f"Bound queue {queue_name} to {self.exchange_name}/{routing_key}")
            return True
        except Exception as e:
            logger.error(f"Error binding queue {queue_name} to {routing_key}: {e}")
            return False

    def unbind_queue(self, queue_name: str, routing_key: str) -> bool:
        """Remove binding between queue and routing key"""
        try:
            connection = self._get_connection()
            channel = connection.channel()
            
            channel.queue_unbind(
                exchange=self.exchange_name,
                queue=queue_name,
                routing_key=routing_key
            )
            
            channel.close()
            connection.close()
            logger.info(f"Unbound queue {queue_name} from {routing_key}")
            return True
        except Exception as e:
            logger.error(f"Error unbinding queue {queue_name} from {routing_key}: {e}")
            return False

    async def get_queue_bindings_async(self, queue_name: str) -> List[dict]:
        """Get all bindings for a queue - ASYNC version (call from FastAPI)"""
        try:
            import httpx
            import base64
            
            credentials = base64.b64encode(f"{AMQP_USER}:{AMQP_PASS}".encode()).decode()
            headers = {"Authorization": f"Basic {credentials}"}
            
            bindings_url = f"http://{AMQP_HOST}:15672/api/queues/{AMQP_VIRTUAL_HOST}/{queue_name}/bindings"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(bindings_url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Failed to get bindings: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error getting queue bindings: {e}")
            return []

    def get_queue_bindings_sync(self, queue_name: str) -> List[dict]:
        """Get all bindings for a queue - SYNC version (for internal use)"""
        try:
            import requests
            import base64
            
            credentials = base64.b64encode(f"{AMQP_USER}:{AMQP_PASS}".encode()).decode()
            headers = {"Authorization": f"Basic {credentials}"}
            
            bindings_url = f"http://{AMQP_HOST}:15672/api/queues/{AMQP_VIRTUAL_HOST}/{queue_name}/bindings"
            
            response = requests.get(bindings_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get bindings: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting queue bindings: {e}")
            return []

    async def get_routing_key_subscribers_async(self, routing_key: str) -> List[str]:
        """Get all queues bound to a routing key - ASYNC version"""
        try:
            import httpx
            import base64
            
            credentials = base64.b64encode(f"{AMQP_USER}:{AMQP_PASS}".encode()).decode()
            headers = {"Authorization": f"Basic {credentials}"}
            
            bindings_url = f"http://{AMQP_HOST}:15672/api/bindings/{AMQP_VIRTUAL_HOST}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(bindings_url, headers=headers)
                if response.status_code == 200:
                    all_bindings = response.json()
                    subscribers = []
                    for binding in all_bindings:
                        if (binding.get('routing_key') == routing_key and 
                            binding.get('source') == self.exchange_name):
                            subscribers.append(binding.get('destination', ''))
                    return subscribers
                return []
        except Exception as e:
            logger.error(f"Error getting routing key subscribers: {e}")
            return []


class WebSocketConnectionManager(ConnectionManager):
    """
    Extended ConnectionManager with RabbitMQ binding capabilities.
    Inherits all WebSocket and consumer management from ConnectionManager.
    """
    
    def __init__(self):
        super().__init__()  # This initializes client_queue, queue_consumers, client_sockets, _lock
        self.rabbitmq_manager = RabbitMQManager()
        # Track bindings locally for GET endpoint
        self._bindings: Dict[str, List[str]] = {}  # queue_name -> [routing_keys]
        logger.info("WebSocketConnectionManager initialized with binding capabilities")

    def get_or_create_queue(self, client_id: str) -> str:
        """Get or create user's dedicated queue - overrides parent"""
        # First, check if already in parent's client_queue
        if client_id in self.client_queue:
            return self.client_queue[client_id]

        # Create new queue
        queue_name = f"user.{client_id}.queue"
        
        # Ensure queue exists in RabbitMQ
        if not self.rabbitmq_manager.queue_exists(queue_name):
            self.rabbitmq_manager.create_queue(queue_name)
        
        # Store in parent's tracking
        self.client_queue[client_id] = queue_name
        logger.info(f"Created/retrieved queue {queue_name} for client {client_id}")
        return queue_name

    def get_consumer(self, queue_name: str) -> Optional[OptimizedPikaConsumerThread]:
        """Get consumer for a queue if it exists"""
        with self._lock:
            return self.queue_consumers.get(queue_name)

    def has_consumer(self, queue_name: str) -> bool:
        """Check if a consumer exists for the queue"""
        with self._lock:
            return queue_name in self.queue_consumers

    def register_consumer(self, queue_name: str, consumer: OptimizedPikaConsumerThread):
        """Register a consumer for a queue"""
        with self._lock:
            self.queue_consumers[queue_name] = consumer
            logger.info(f"Registered consumer for queue {queue_name}")

    def unregister_consumer(self, queue_name: str):
        """Unregister a consumer"""
        with self._lock:
            if queue_name in self.queue_consumers:
                del self.queue_consumers[queue_name]
                logger.info(f"Unregistered consumer for queue {queue_name}")

    async def bind_queue_to_routing_key(self, queue_name: str, routing_key: str) -> bool:
        """Bind queue to routing key in RabbitMQ and track locally"""
        try:
            # First, create the binding in RabbitMQ
            result = self.rabbitmq_manager.bind_queue(
                queue_name=queue_name,
                routing_key=routing_key
            )
            
            if result:
                # Track the binding locally for GET endpoint
                if queue_name not in self._bindings:
                    self._bindings[queue_name] = []
                if routing_key not in self._bindings[queue_name]:
                    self._bindings[queue_name].append(routing_key)
                logger.info(f"Tracked binding: {queue_name} -> {routing_key}")
            
            return result
        except Exception as e:
            logger.error(f"Error binding queue {queue_name} to {routing_key}: {e}")
            return False

    async def unbind_queue_from_routing_key(self, queue_name: str, routing_key: str) -> bool:
        """Remove binding between queue and routing key"""
        try:
            result = self.rabbitmq_manager.unbind_queue(
                queue_name=queue_name,
                routing_key=routing_key
            )
            
            if result:
                # Remove from local tracking
                if queue_name in self._bindings:
                    if routing_key in self._bindings[queue_name]:
                        self._bindings[queue_name].remove(routing_key)
                    if not self._bindings[queue_name]:
                        del self._bindings[queue_name]
                logger.info(f"Removed binding tracking: {queue_name} -> {routing_key}")
            
            return result
        except Exception as e:
            logger.error(f"Error unbinding queue {queue_name} from {routing_key}: {e}")
            return False

    async def get_queue_bindings(self, queue_name: str) -> List[dict]:
        """Get all bindings for a queue - from local tracking"""
        bindings = []
        if queue_name in self._bindings:
            for routing_key in self._bindings[queue_name]:
                bindings.append({
                    "routing_key": routing_key,
                    "queue": queue_name,
                    "source_exchange": self.rabbitmq_manager.exchange_name
                })
        
        logger.info(f"Returning {len(bindings)} bindings for {queue_name} (from local tracking)")
        return bindings

    async def get_routing_key_subscribers(self, routing_key: str) -> List[str]:
        """Get all queues bound to a routing key - from local tracking"""
        subscribers = []
        for queue_name, keys in self._bindings.items():
            if routing_key in keys:
                subscribers.append(queue_name)
        return subscribers

