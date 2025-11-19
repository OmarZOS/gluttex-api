import ssl, pika


def test_connection():
    ssl_context = ssl.create_default_context()
    # ssl_context.check_hostname = False
    # ssl_context.verify_mode = ssl.CERT_NONE

    params = pika.ConnectionParameters(
        host='amqp.gluttex.com',
        port=5671,
        virtual_host='/',  # or your custom vhost
        ssl_options=pika.SSLOptions(ssl_context, server_hostname='amqp.gluttex.com'),
        credentials=pika.PlainCredentials('prod_user', 'NewStrongPassword123!')
    )

    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='test')
    channel.basic_publish(exchange='', routing_key='test', body='Hello')
    print("Message sent successfully!")
    connection.close()
def pass_gen():
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(secrets.choice(alphabet) for _ in range(24))
    print(password)

test_connection()
# pass_gen()