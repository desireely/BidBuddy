import pika
import time

# These module-level variables are initialized whenever a new instance of python interpreter imports the module;
# In each instance of python interpreter (i.e., a program run), the same module is only imported once (guaranteed by the interpreter).

hostname = "rabbitmq" # default hostname
port = 5672 # default port
# connect to the broker and set up a communication channel in the connection
username = 'guest'
password = 'guest'

connected = False
while not connected:
    try:
        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(hostname, port, '/', credentials, heartbeat=3600, blocked_connection_timeout=3600)
        connection = pika.BlockingConnection(parameters)
        connected = True
    except pika.exceptions.AMQPConnectionError as error:
        print(f"Failed to connect to RabbitMQ: {error}")
        time.sleep(5)

channel = connection.channel()
# Set up the exchange if the exchange doesn't exist
# - use a 'topic' exchange to enable interaction
exchangename="notification"
exchangetype="topic"
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)
    # 'durable' makes the exchange survive broker restarts

# Here can be a place to set up all queues needed by the microservices,
# - instead of setting up the queues using RabbitMQ UI.

############   send_email queue   #############
queue_name = 'send_email'
channel.queue_declare(queue=queue_name, durable=True) 
    # 'durable' makes the queue survive broker restarts

#bind new_listing queue
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.email') 
    # bind the queue to the exchange via the key
    # any routing_key with two words and ending with '.error' will be matched

############   send tele queue   #############
queue_name = 'send_tele'
channel.queue_declare(queue=queue_name, durable=True) 
    # 'durable' makes the queue survive broker restarts

#bind new_listing queue
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.tele') 
    # bind the queue to the exchange via the key
    # any routing_key with two words and ending with '.error' will be matched


    

"""
This function in this module sets up a connection and a channel to a local AMQP broker,
and declares a 'topic' exchange to be used by the microservices in the solution.
"""
def check_setup():
    # The shared connection and channel created when the module is imported may be expired, 
    # timed out, disconnected by the broker or a client;
    # - re-establish the connection/channel is they have been closed
    global connection, channel, hostname, port, exchangename, exchangetype

    if not is_connection_open(connection):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port, heartbeat=3600, blocked_connection_timeout=3600))
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)


def is_connection_open(connection):
    # For a BlockingConnection in AMQP clients,
    # when an exception happens when an action is performed,
    # it likely indicates a broken connection.
    # So, the code below actively calls a method in the 'connection' to check if an exception happens
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False