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



def create_consumer(queue_name, asyncio_queue, on_error=None, prefetch_count=50):
    """Factory to create a consumer thread"""
    from lib import OptimizedPikaConsumerThread
    consumer = OptimizedPikaConsumerThread(
        queue_name=queue_name,
        asyncio_queue=asyncio_queue,
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
        on_error: Optional[Callable[[Exception], None]] = None,
        prefetch_count: int = 50,
        reconnect_delay: float = 5.0,
        max_reconnect_attempts: int = 10
    ) -> None:
        self.queue_name = queue_name
        self.asyncio_queue = asyncio_queue
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
            
            # Declare queue with proper settings
            self._channel.queue_declare(
                queue=self.queue_name,
                durable=True,
                exclusive=False,
                auto_delete=True,
                arguments={
                    "x-message-ttl": 300000,
                    "x-expires": 3600000,
                }
            )
            
            self._reconnect_attempts = 0
            return True
            
        except Exception as e:
            logger.error(f"Failed to create RabbitMQ connection for {self.queue_name}: {e}")
            self._reconnect_attempts += 1
            return False

    def _on_message_thread(self, channel, method, properties, body):
        """Process incoming RabbitMQ messages"""
        start_time = time.time()
        try:
            # Use orjson for faster JSON parsing
            message = orjson.loads(body)
            
            # Push to asyncio queue in a thread-safe manner
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.call_soon_threadsafe(self.asyncio_queue.put_nowait, message)
            
            # Acknowledge message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as exc:
            logger.error(f"Error processing message for {self.queue_name}: {exc}")
            # Negative acknowledge and requeue for transient errors
            try:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception:
                pass
        finally:
            # MESSAGE_PROCESSING_TIME.observe(time.time() - start_time)
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

manager = ConnectionManager()

class RabbitMQManager:
    def __init__(self):
        self.connection_params = self._get_connection_params()
        self.exchange_name = "user_events"

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
            
            # This will raise an exception if queue doesn't exist
            channel.queue_declare(queue=queue_name, passive=True)
            channel.close()
            connection.close()
            return True
            
        except pika.exceptions.ChannelClosedByBroker:
            return False
        except Exception:
            return False

    def create_queue(self, queue_name: str) -> bool:
        """Create a queue with proper settings"""
        try:
            connection = self._get_connection()
            channel = connection.channel()
            
            channel.queue_declare(
                queue=queue_name,
                durable=True,
                exclusive=False,
                auto_delete=True,
                arguments={
                    "x-message-ttl": 300000,
                    "x-expires": 3600000,
                }
            )
            
            channel.close()
            connection.close()
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
                exchange_type='topic',
                durable=True
            )
            
            # Create binding
            channel.queue_bind(
                exchange=self.exchange_name,
                queue=queue_name,
                routing_key=routing_key
            )
            
            channel.close()
            connection.close()
            logger.info(f"Bound queue {queue_name} to {routing_key}")
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

    def get_queue_bindings(self, queue_name: str) -> List[dict]:
        """Get all bindings for a queue"""
        # This would require RabbitMQ management API or admin access
        # For now, return empty list - implement based on your setup
        return []

    def get_routing_key_subscribers(self, routing_key: str) -> List[str]:
        """Get all queues bound to a routing key"""
        # This would require RabbitMQ management API
        # For now, return empty list - implement based on your setup
        return []

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.consumers: Dict[str, OptimizedPikaConsumerThread] = {}
        self.rabbitmq_manager = RabbitMQManager()

    def get_or_create_queue(self, client_id: str) -> str:
        """Get or create user's dedicated queue"""
        queue_name = f"user.{client_id}.queue"
        
        # Ensure queue exists in RabbitMQ
        if not self.rabbitmq_manager.queue_exists(queue_name):
            self.rabbitmq_manager.create_queue(queue_name)
            
        return queue_name

    async def bind_queue_to_routing_key(self, queue_name: str, routing_key: str) -> bool:
        """Bind queue to routing key in RabbitMQ"""
        try:
            return self.rabbitmq_manager.bind_queue(
                queue_name=queue_name,
                routing_key=routing_key
            )
        except Exception as e:
            logger.error(f"Error binding queue {queue_name} to {routing_key}: {e}")
            return False

    async def unbind_queue_from_routing_key(self, queue_name: str, routing_key: str) -> bool:
        """Remove binding between queue and routing key"""
        try:
            return self.rabbitmq_manager.unbind_queue(
                queue_name=queue_name,
                routing_key=routing_key
            )
        except Exception as e:
            logger.error(f"Error unbinding queue {queue_name} from {routing_key}: {e}")
            return False

    async def get_queue_bindings(self, queue_name: str) -> List[dict]:
        """Get all bindings for a queue"""
        try:
            return self.rabbitmq_manager.get_queue_bindings(queue_name)
        except Exception as e:
            logger.error(f"Error getting bindings for {queue_name}: {e}")
            return []

    async def get_routing_key_subscribers(self, routing_key: str) -> List[str]:
        """Get all queues subscribed to a routing key"""
        try:
            return self.rabbitmq_manager.get_routing_key_subscribers(routing_key)
        except Exception as e:
            logger.error(f"Error getting subscribers for {routing_key}: {e}")
            return []

