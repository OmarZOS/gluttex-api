
import pika
import json
from datetime import datetime
from notification_builder import NotificationFactory

class FlutterNotificationProducer:
    def __init__(self, rabbitmq_url: str = "amqp://localhost:5672"):
        self.connection = pika.BlockingConnection(
            pika.URLParameters(rabbitmq_url)
        )
        self.channel = self.connection.channel()
        
        # Create user-specific queues for direct messaging
        self._setup_user_queues()
    
    def _setup_user_queues(self):
        """Setup exchanges and user-specific queues"""
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
    
    def send_to_user(self, user_id: int, notification_code: str, **params):
        """Send notification to a specific user's queue"""
        message = {
            'type': 'user_notification',
            'user_id': user_id,
            'notification_code': notification_code,
            'data': params,
            'timestamp': datetime.utcnow().isoformat(),
            'preformatted': self._preformat_notification(notification_code, params)
        }
        
        self.channel.basic_publish(
            exchange='user_notifications',
            routing_key=f'user_{user_id}',  # User-specific routing key
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                content_type='application/json',
                headers={
                    'notification_type': notification_code,
                    'user_id': str(user_id)
                }
            )
        )
        print(f" [→] Sent {notification_code} to user_{user_id}")
    
    def send_to_supplier(self, supplier_id: int, notification_code: str, **params):
        """Send notification to all users of a supplier"""
        message = {
            'type': 'supplier_notification',
            'supplier_id': supplier_id,
            'notification_code': notification_code,
            'data': params,
            'timestamp': datetime.utcnow().isoformat(),
            'preformatted': self._preformat_notification(notification_code, params)
        }
        
        self.channel.basic_publish(
            exchange='broadcast_notifications',
            routing_key='',  # Fanout doesn't use routing key
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        print(f" [→] Broadcast {notification_code} to supplier_{supplier_id}")
    
    def _preformat_notification(self, notification_code: str, params: dict) -> dict:
        """Pre-format notification for Flutter app"""
        # Use your existing notification builder
        params_json = NotificationFactory.order.order_received(**params) if notification_code == 'order_received' else json.dumps(params)
        
        return {
            'title': self._get_notification_title(notification_code, params),
            'body': self._get_notification_body(notification_code, params),
            'action': self._get_notification_action(notification_code),
            'icon': self._get_notification_icon(notification_code),
            'color': self._get_notification_color(notification_code),
            'route': self._get_notification_route(notification_code, params)
        }
    
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
def notify_order_received(order_data: dict, user_id: int):
    producer = FlutterNotificationProducer()
    
    producer.send_to_user(
        user_id=user_id,
        notification_code='order_received',
        order_id=order_data['id'],
        order_number=order_data['number'],
        amount=order_data['amount'],
        supplier_name=order_data['supplier_name']
    )
    
    producer.close()
