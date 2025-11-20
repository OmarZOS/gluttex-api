

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
def send_to_product_subscribers(product_data, product_id: int, producer=None):
    producer.send_to_prod_subscribers(
        product_id=product_id,
        notification_code='product_updated',
        product_quantity=product_data['product_quantity'],
    )