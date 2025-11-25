from pathlib import Path
import shutil
import pika
import threading
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from typing import Any, Callable, Dict, Optional, Set
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



AMQP_HOST = os.getenv("AMQP_HOST","rabbitmq")
AMQP_PORT = os.getenv("AMQP_PORT","5672")
AMQP_VIRTUAL_HOST = os.getenv("AMQP_VIRTUAL_HOST","/gluttex")
AMQP_USER = os.getenv("AMQP_USER","dev_user")
AMQP_PASS = os.getenv("AMQP_PASS","dev_pass")




# Configuration with environment variables
class Settings(BaseSettings):
    # rabbit_url: str = Field(default="amqp://dev_user:dev_pass@rabbitmq:5672/", env="RABBIT_URL")
    host: str = Field(default="rabbitmq", env="HOST")
    port: int = Field(default=8000, env="PORT")
    max_connections: int = Field(default=10000, env="MAX_CONNECTIONS")
    prefetch_count: int = Field(default=50, env="PREFETCH_COUNT")
    heartbeat_interval: int = Field(default=30, env="HEARTBEAT_INTERVAL")
    connection_timeout: int = Field(default=10, env="CONNECTION_TIMEOUT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"

settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level),
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
            self._connection = pika.BlockingConnection(
                pika.URLParameters(settings.rabbit_url)
            )
            self._channel = self._connection.channel()
            self._channel.basic_qos(prefetch_count=self.prefetch_count)
            
            # Declare queue with proper settings
            self._channel.queue_declare(
                queue=self.queue_name,
                durable=True,  # Changed to durable for production
                exclusive=False,
                auto_delete=True,  # Auto-delete when no consumers
                arguments={
                    "x-message-ttl": 300000,  # 5 minutes TTL
                    "x-expires": 3600000,     # Queue expires after 1 hour of inactivity
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
            RABBIT_MESSAGES_RECEIVED.inc()
            
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
            MESSAGE_PROCESSING_TIME.observe(time.time() - start_time)

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



# class PikaConsumerThread:
#     """
#     RabbitMQ consumer running in a separate thread to avoid blocking
#     """
#     def __init__(
#         self,
#         queue_name: str,
#         asyncio_queue: asyncio.Queue,
#         on_error: Optional[Callable[[Exception], None]] = None,
#         prefetch_count: int = 50
#     ) -> None:
#         self.queue_name = queue_name
#         self.asyncio_queue = asyncio_queue
#         self._stop_event = threading.Event()
#         self._thread: Optional[threading.Thread] = None
#         self.on_error = on_error
#         self.prefetch_count = prefetch_count
#         self._connection: Optional[pika.BlockingConnection] = None
#         self._channel: Optional[pika.channel.Channel] = None

#     def start(self) -> None:
#         """Start the consumer thread"""
#         self._thread = threading.Thread(
#             target=self._run_consumer_loop,
#             daemon=True,
#             name=f"RabbitConsumer-{self.queue_name}"
#         )
#         self._thread.start()
#         logger.info(f"Started RabbitMQ consumer thread for queue: {self.queue_name}")

#     def stop(self, timeout: float = 2.0) -> None:
#         """Stop the consumer thread gracefully"""
#         logger.info(f"Stopping consumer for queue {self.queue_name}")
#         self._stop_event.set()
#         self._cleanup_connection()
        
#         if self._thread and self._thread.is_alive():
#             self._thread.join(timeout=timeout)
#             if self._thread.is_alive():
#                 logger.warning(f"Consumer thread for {self.queue_name} didn't stop gracefully")

#     def _cleanup_connection(self):
#         """Clean up RabbitMQ connection safely"""
#         try:
#             if self._channel and self._channel.is_open:
#                 self._channel.close()
#         except Exception:
#             pass
#         finally:
#             self._channel = None

#         try:
#             if self._connection and self._connection.is_open:
#                 self._connection.close()
#         except Exception:
#             pass
#         finally:
#             self._connection = None

#     def _create_connection_params(self) -> pika.ConnectionParameters:
#         """Create RabbitMQ connection parameters"""
#         params = pika.ConnectionParameters(
#             host=AMQP_HOST,
#             port=int(AMQP_PORT),
#             virtual_host=AMQP_VIRTUAL_HOST,
#             credentials=pika.PlainCredentials(AMQP_USER, AMQP_PASS),
#             heartbeat=600,  # 10 minute heartbeat
#             blocked_connection_timeout=300,  # 5 minute timeout
#             connection_attempts=3,  # Retry attempts
#             retry_delay=5,  # Seconds between retries
#         )
        
#         # Add SSL if not local rabbitmq
#         if AMQP_HOST != "rabbitmq":
#             ssl_context = ssl.create_default_context()
#             ssl_context.check_hostname = False
#             ssl_context.verify_mode = ssl.CERT_NONE
#             params.ssl_options = pika.SSLOptions(ssl_context, server_hostname=AMQP_HOST)
        
#         return params

#     def _on_message_callback(self, channel, method, properties, body):
#         """
#         Callback executed in the RabbitMQ consumer thread when a message arrives
#         """
#         try:
#             # Parse message in the worker thread
#             message = orjson.loads(body)
            
#             # Push to asyncio queue in a thread-safe manner
#             loop = asyncio.get_event_loop()
#             if loop.is_running():
#                 # Use call_soon_threadsafe to avoid blocking
#                 loop.call_soon_threadsafe(
#                     self.asyncio_queue.put_nowait, 
#                     {"message": message, "delivery_tag": method.delivery_tag}
#                 )
#             else:
#                 logger.error("Event loop not running, cannot queue message")
#                 channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                
#         except Exception as exc:
#             logger.error(f"Error processing message in callback: {exc}")
#             try:
#                 channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
#             except Exception:
#                 pass

#     def _run_consumer_loop(self):
#         """
#         Main RabbitMQ consumer loop running in a separate thread
#         """
#         logger.info(f"Starting RabbitMQ consumer loop for {self.queue_name}")
        
#         while not self._stop_event.is_set():
#             try:
#                 # Create connection
#                 params = self._create_connection_params()
#                 self._connection = pika.BlockingConnection(params)
#                 self._channel = self._connection.channel()
                
#                 # Configure QoS
#                 self._channel.basic_qos(prefetch_count=self.prefetch_count)
                
#                 # Declare queue
#                 self._channel.queue_declare(
#                     queue=self.queue_name,
#                     durable=True,
#                     exclusive=False,
#                     auto_delete=True,
#                     arguments={
#                         "x-message-ttl": 300000,  # 5 minutes TTL
#                         "x-expires": 3600000,     # Queue expires after 1 hour
#                     }
#                 )
                
#                 logger.info(f"Successfully connected to RabbitMQ for queue {self.queue_name}")
                
#                 # Start consuming - this is the blocking call that runs in the thread
#                 self._consumer_tag = self._channel.basic_consume(
#                     queue=self.queue_name,
#                     on_message_callback=self._on_message_callback,
#                     auto_ack=False,  # We'll ack manually after processing
#                 )
                
#                 # Start the blocking consumption loop
#                 logger.info(f"Starting message consumption for {self.queue_name}")
#                 self._channel.start_consuming()
                
#             except pika.exceptions.ConnectionClosedByBroker:
#                 logger.warning(f"RabbitMQ connection closed by broker for {self.queue_name}")
#                 if not self._stop_event.is_set():
#                     time.sleep(5)  # Wait before reconnecting
                    
#             except pika.exceptions.AMQPConnectionError as e:
#                 logger.error(f"RabbitMQ connection error for {self.queue_name}: {e}")
#                 if not self._stop_event.is_set():
#                     time.sleep(10)  # Longer wait for connection errors
                    
#             except Exception as e:
#                 logger.error(f"Unexpected error in consumer loop for {self.queue_name}: {e}")
#                 if callable(self.on_error):
#                     try:
#                         self.on_error(e)
#                     except Exception:
#                         logger.exception("Error in on_error callback")
#                 if not self._stop_event.is_set():
#                     time.sleep(5)
                    
#             finally:
#                 self._cleanup_connection()
        
#         logger.info(f"RabbitMQ consumer loop stopped for {self.queue_name}")

class ConnectionManager:
    def __init__(self):
        self.client_queue: Dict[str, str] = {}
        self.queue_consumers: Dict[str, OptimizedPikaConsumerThread] = {}
        self.client_sockets: Dict[str, set[WebSocket]] = {}
        self._lock = threading.RLock()

    def get_or_create_queue(self, client_id: str) -> str:
        # Return existing queue if already created
        if client_id in self.client_queue:
            return self.client_queue[client_id]

        # Create new queue once
        queue_name = f"ws.{client_id}.{uuid.uuid4().hex}"
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
                    port=AMQP_PORT,
                    virtual_host=AMQP_VIRTUAL_HOST,  # or your custom vhost
                    # ssl_options=pika.SSLOptions(ssl_context, server_hostname=AMQP_HOST),
                    credentials=pika.PlainCredentials(AMQP_USER, AMQP_PASS)
                )
            if AMQP_HOST != "rabbitmq":
                ssl_context = ssl.create_default_context()
                options = pika.SSLOptions(ssl_context, server_hostname=AMQP_HOST)
                params.ssl_options = options
            print(AMQP_HOST)
            print(AMQP_PORT)
            print(AMQP_VIRTUAL_HOST)
            print(AMQP_USER)
            print(AMQP_PASS)
            self._connection = pika.BlockingConnection(params)
            self._channel = self._connection.channel()
            self._channel.basic_qos(prefetch_count=self.prefetch_count)
            
            # Declare queue with proper settings
            self._channel.queue_declare(
                queue=self.queue_name,
                durable=True,  # Changed to durable for production
                exclusive=False,
                auto_delete=True,  # Auto-delete when no consumers
                arguments={
                    "x-message-ttl": 300000,  # 5 minutes TTL
                    "x-expires": 3600000,     # Queue expires after 1 hour of inactivity
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
            # RABBIT_MESSAGES_RECEIVED.inc()
            
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
            MESSAGE_PROCESSING_TIME.observe(time.time() - start_time)

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


