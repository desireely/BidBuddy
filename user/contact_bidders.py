from flask import Flask, request, jsonify
import requests
from invokes import invoke_http
import amqp_setup
import pika
import json

app = Flask(__name__)

user_URL = "http://127.0.0.1:5005/user"

# Notify bidder for successful bid and prev high bidder that he got outbid 
@app.route("/bidforlisting/", method=['POST'])
def post_bid():
    if request.is_json:
        try:
            users_details = request.get_json()
            headers = request.headers

            result = processUserBid(headers, users_details)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            
            print(e)

            return jsonify({
                "code": 500,
                "message": "listing.py internal error: " + str(e)
            }), 500
        
    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processUserBid(headers, users_details):

    new_userid = users_details['data']['userid']
    # Invoke the user microservice
    print('\n-----Invoking listing microservice-----')
    new_result = invoke_http(user_URL+'/'+new_userid, method='GET', headers=headers)

    # Check the listing result
    code = new_result["code"]
    if code not in range(200, 300):
        return new_result
    

    new_email = new_result['email']
    # Preparing message to send via AMQP
    message = json.dumps(
        {
            "user_emails": "Testing",
            "subject": f"{new_email} Posted Successfully!",
            "html_body": "<strong>Hello, this is a test email.</strong>"
        }
    )

    # AMQP part
    print('\n\n-----Publishing message-----')        
    amqp_setup.channel.basic_publish(
        exchange=amqp_setup.exchangename, 
        routing_key="sendemail", 
        body=message, 
        properties=pika.BasicProperties(delivery_mode=2)
    )

    prev_userid = users_details['data']['high_current_bid_userid']
    # Invoke the user microservice
    print('\n-----Invoking listing microservice-----')
    prev_result = invoke_http(user_URL+'/'+prev_userid, method='GET', headers=headers)

    # Check the listing result
    code = prev_result["code"]
    if code not in range(200, 300):
        return prev_result
    
    prev_email = prev_result['email']
    # Preparing message to send via AMQP
    message = json.dumps(
        {
            "user_emails": "Testing",
            "subject": f"{prev_email} Posted Successfully!",
            "html_body": "<strong>Hello, this is a test email.</strong>"
        }
    )

    # AMQP part
    print('\n\n-----Publishing message-----')        
    amqp_setup.channel.basic_publish(
        exchange=amqp_setup.exchangename, 
        routing_key="sendemail", 
        body=message, 
        properties=pika.BasicProperties(delivery_mode=2)
    )


# Run script
if __name__ == "__main__":
    app.run(port=5020, debug=True)
