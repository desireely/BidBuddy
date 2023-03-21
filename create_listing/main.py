from flask import Flask, jsonify, request
from flask_cors import CORS
from invokes import invoke_http
import pika
import os
import sys
sys.path.append('../notification_api')
import main
import amqp_setup


app = Flask(__name__)
CORS(app)

#book_URL = "http://localhost:5000/book"
order_URL = "http://localhost:5001/order"
shipping_record_URL = "http://localhost:5002/shipping_record"
#activity_log_URL = "http://localhost:5003/activity_log"
#error_URL = "http://localhost:5004/error"

@app.route("/publish_listing", methods=['POST'])


def place_order():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            listing_data = request.get_json()
            print("\nReceived an order in JSON:", order)

            # do the actual work
            # 1. Send order info {cart items}
            result = processPlaceOrder(order)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def send_notification():
    print('\n-----Invoking notification microservice-----')
    order_result = invoke_http(order_URL, method='POST', json=order)
    print('order_result:', order_result)
  


    code = order_result["code"]
    message = jsonify(
        {
                "user_emails": [],
                "subject": "Listing Posted Successfully!",
                "html_body": "<strong>Hello, this is a test email.</strong>"
            }
    ),201

    print('\n\n-----Publishing the (order info) message with routing_key=order.info-----')        

        # invoke_http(activity_log_URL, method="POST", json=order_result)            
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="send_email", 
        body=message)
    
    print("\nOrder published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails
