
import pika,ssl
import json
from datetime import datetime
from constants import *
from functools import wraps





class FlutterNotificationProducer:
    def __init__(self):
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

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        
        # Create user-specific queues for direct messaging
        self._setup_user_queues()
    
    def _setup_user_queues(self):
        """Setup exchanges, queues, and bindings for notifications"""
        
        # ========== EXCHANGES ==========
        # Direct exchange for user-specific notifications
        self.channel.exchange_declare(
            exchange='user_notifications',
            exchange_type='direct',
            durable=True
        )
        
        # Fanout exchange for broadcast notifications
        self.channel.exchange_declare(
            exchange='broadcast_notifications', 
            exchange_type='fanout',
            durable=True
        )

        # Topic exchange for restrained notifications
        self.channel.exchange_declare(
            exchange='restrained_notifications', 
            exchange_type='topic',
            durable=True
        )
        
        # ========== QUEUES AND BINDINGS ==========
        # User-specific queues (these will be created dynamically when users subscribe)
        # For now, create a dead letter queue for undelivered messages
        self.channel.queue_declare(
            queue='dead_letter_queue',
            durable=True
        )
        
        # Bind dead letter queue to all exchanges
        self.channel.queue_bind(
            exchange='user_notifications',
            queue='dead_letter_queue',
            routing_key='#'

        )
        self.channel.queue_bind(
            exchange='broadcast_notifications',
            queue='dead_letter_queue'
        )
        self.channel.queue_bind(
            exchange='restrained_notifications',
            queue='dead_letter_queue',
            routing_key='#'
        )


    def ensure_user_queue(self, user_id: int):
        """Ensure a queue exists for a specific user"""
        queue_name = f'user.{user_id}.queue'
        
        # Declare queue for this user
        self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                'x-max-priority': 10,  # Enable message priority
                'x-message-ttl': 604800000  # 7 days TTL (milliseconds)
            }
        )
        
        # Bind queue to user_notifications exchange
        self.channel.queue_bind(
            exchange='user_notifications',
            queue=queue_name,
            routing_key=f'user.{user_id}'
        )
        
        # Also bind to restrained_notifications for topic-based messages
        self.channel.queue_bind(
            exchange='restrained_notifications',
            queue=queue_name,
            routing_key=f'user.{user_id}.#'
        )
        
        return queue_name
    
    def send_to_user(self, user_id: int, notification_code: str, **params):
        """Send notification to a specific user's queue"""
        
        # Ensure user queue exists (create if not)
        self.ensure_user_queue(user_id)
        
        message = {
            'type': 'user_notification',
            'user_id': user_id,
            'notification_code': notification_code,
            'data': params,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Fix: Remove trailing dot from routing key
        routing_key = f'user.{user_id}'  # Changed: removed trailing dot
        
        try:
            self.channel.basic_publish(
                exchange='user_notifications',
                routing_key=routing_key,
                body=json.dumps(message, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json',
                    priority=params.get('priority', 5),
                    headers={
                        'notification_type': notification_code,
                        'user_id': str(user_id)
                    }
                )
            )
            print(f" [✓] Sent {notification_code} to user {user_id}")
            return True
        except Exception as e:
            print(f" [✗] Failed to send to user {user_id}: {e}")
            return False
    
    def send_to_supplier(self, supplier_id: int, notification_code: str, **params):
        """Send notification to all users of a supplier"""
        
        message = {
            'type': 'supplier_notification',
            'supplier_id': supplier_id,
            'notification_code': notification_code,
            'data': params,
            'timestamp': datetime.now().isoformat(),
        }

        routing_key = f"supplier.{supplier_id}"  # Changed: removed trailing dot
        
        try:
            self.channel.basic_publish(
                exchange='restrained_notifications',
                routing_key=routing_key,
                body=json.dumps(message, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                    headers={
                        'notification_type': notification_code,
                        'supplier_id': str(supplier_id)
                    }
                )
            )
            print(f" [✓] Sent {notification_code} to supplier {supplier_id}")
            return True
        except Exception as e:
            print(f" [✗] Failed to send to supplier {supplier_id}: {e}")
            return False

    def send_to_org(self, org_id: int, notification_code: str, **params):
        
        """Send notification to all users of an org"""
        message = {
            'type': 'org_notification',
            'org_id': org_id,
            'notification_code': notification_code,
            'data': params,
            'timestamp': datetime.now().isoformat(),
            # 'preformatted': self._preformat_notification(notification_code, params)
        }

        routing_key = f"org.{org_id}."
        
        self.channel.basic_publish(
            exchange='restrained_notifications',
            routing_key=routing_key,  # Topic uses a routing key
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        print(f" [→] Broadcast {notification_code} to org_{org_id}")

    def send_to_prod_subscribers(self, product_id: int, notification_code: str, **params):
        """Send notification to all users who subscribed"""
        message = {
            'type': 'product_sub_notification',
            'product_id': product_id,
            'notification_code': notification_code,
            'data': params,
            'timestamp': datetime.now().isoformat(),
            # 'preformatted': self._preformat_notification(notification_code, params)
        }

        routing_key = f"product.{product_id}."
        
        self.channel.basic_publish(
            exchange='restrained_notifications',
            routing_key=routing_key,  # Topic uses a routing key
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        print(f" [→] Broadcast {notification_code} to product_{product_id}")
    
    # def _preformat_notification(self, notification_code: str, params: dict) -> dict:
    #     """Pre-format notification for Flutter app"""
    #     # Use your existing notification builder
    #     params_json = NotificationFactory.order.order_received(**params) if notification_code == 'order_received' else json.dumps(params)
        
    #     return {
    #         'title': self._get_notification_title(notification_code, params),
    #         'body': self._get_notification_body(notification_code, params),
    #         'action': self._get_notification_action(notification_code),
    #         'icon': self._get_notification_icon(notification_code),
    #         'color': self._get_notification_color(notification_code),
    #         'route': self._get_notification_route(notification_code, params)
    #     }
    
    def _get_notification_title(self, code: str, params: dict) -> str:
        titles = {
            'order_received': 'New Order 📦',
            'product_stock_critical': 'Low Stock Alert ⚠️',
            'product_run_out': 'Out of Stock 🚫',
            'work_invitation': 'Work Invitation 👥',
            'rule_expiry': 'Rule Expiring Soon ⏰'
        }
        return titles.get(code, 'New Notification')
    
    def _get_notification_body(self, code: str, params: dict) -> str:
        # Use your existing formatting logic
        if code == 'order_received':
            return f"Order #{params.get('order_number', '')} for ${params.get('amount', 0)}"
        elif code == 'product_stock_critical':
            return f"Low stock: {params.get('product_name')} ({params.get('current_stock')} left)"
        # Add more cases...
        return "You have a new notification"
    
    def _get_notification_action(self, code: str) -> str:
        actions = {
            'order_received': 'View Order',
            'product_stock_critical': 'Check Stock',
            'work_invitation': 'Respond'
        }
        return actions.get(code, 'View')
    
    def _get_notification_icon(self, code: str) -> str:
        icons = {
            'order_received': '📦',
            'product_stock_critical': '⚠️',
            'product_run_out': '🚫',
            'work_invitation': '👥',
            'rule_expiry': '⏰'
        }
        return icons.get(code, '🔔')
    
    def _get_notification_color(self, code: str) -> str:
        colors = {
            'order_received': '#4CAF50',
            'product_stock_critical': '#FF9800', 
            'product_run_out': '#F44336',
            'work_invitation': '#9C27B0'
        }
        return colors.get(code, '#607D8B')
    
    def _get_notification_route(self, code: str, params: dict) -> str:
        routes = {
            'order_received': '/orders/${order_id}',
            'product_stock_critical': '/inventory',
            'work_invitation': '/invitations'
        }
        return routes.get(code, '/notifications')
    
    def close(self):
        self.connection.close()

# Usage in your API endpoints

# Global producer instance (singleton)
_producer = None

def get_producer() -> FlutterNotificationProducer:
    """Get or create the global producer instance"""
    global _producer
    if _producer is None:
        _producer = FlutterNotificationProducer()
    return _producer

# Modified decorator that uses the singleton
def amqp_connection_manager(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        producer = get_producer()  # Reuse existing connection
        kwargs['producer'] = producer
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # If connection is broken, reconnect and retry once
            if "connection" in str(e).lower():
                producer.reconnect()
                kwargs['producer'] = producer
                return func(*args, **kwargs)
            raise
    return wrapper


