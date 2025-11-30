

from communication.wrappers.amqp import amqp_connection_manager

@amqp_connection_manager
def notify_order_received(order_data: dict, user_id: int, producer=None):
    # Use the passed producer
    producer.send_to_user(
        user_id=user_id,
        notification_code='order_received',
        order_id=order_data['id'],
        order_number=order_data['number'],
        amount=order_data['amount'],
        supplier_name=order_data['supplier_name']
    )

@amqp_connection_manager
def notify_invitation_to_role_received(invitation_data: dict, user_id: int, producer=None):
    # Use the passed producer
    producer.send_to_user(
        user_id=user_id,
        notification_code='role_invitation',
        rule_id=invitation_data['rule_id'],
        role=invitation_data['role'],
        provider_id=invitation_data['provider_id'],
        organization_id=invitation_data['organization_id'],
        invited_by=invitation_data['invited_by']
    )

@amqp_connection_manager
def notify_rule_to_role_received(invitation_data: dict, user_id: int, producer=None):
    # Use the passed producer
    producer.send_to_user(
        user_id=user_id,
        notification_code='new_rule_added',
        rule_id=invitation_data['rule_id'],
        rule_name=invitation_data['rule_name'],
        rule_type=invitation_data['rule_type'],
        added_by=invitation_data['added_by']
    )

@amqp_connection_manager
def send_to_product_subscribers(product_data, product_id: int, producer=None):
    producer.send_to_prod_subscribers(
        product_id=product_id,
        notification_code='product_updated',
        product_quantity=product_data['product_quantity'],
    )

@amqp_connection_manager
def send_to_product_subscribers(product_data, product_id: int, producer=None):
    producer.send_to_prod_subscribers(
        product_id=product_id,
        notification_code='product_updated',
        product_quantity=product_data['product_quantity'],
    )