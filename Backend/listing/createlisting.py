from flask import Flask, request, render_template, jsonify
import requests
from invokes import invoke_http
import amqp_setup
import pika
import json

app = Flask(__name__)


listing_URL = "http://127.0.0.1:5000/listing"


# Add a new listing
@app.route("/createlisting", methods=['POST'])
def add_listing():
    
    if request.is_json:

        try:
            listing = request.get_json()
            print("Received listing details in JSON order", listing)

            result = processListing(listing)
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


def processListing(listing):

    # Invoke the listing microservice
    print('\n-----Invoking listing microservice-----')
    # listing_result = requests.request(url = listing_URL, method='POST', json=listing)
    listing_result = invoke_http(listing_URL, method='POST', json=listing)
    print('listing_result:', listing_result)

    # all the data in listing_result
    auction_end_datetime = listing_result['data']['auction_end_datetime']
    highest_current_bid = listing_result['data']['highest_current_bid']
    listing_description = listing_result['data']['listing_description']
    listing_name = listing_result['data']['listing_name']
    starting_bid = listing_result['data']['starting_bid']
    status = listing_result['data']['status']
    userid = listing_result['data']['userid']
    listing_image_file_name = listing_result['data']['listing_image_file_name']
    transaction_end_datetime = listing_result['data']['transaction_end_datetime']
    transaction_status = listing_result['data']['transaction_status']

    # Preparing message to send via AMQP
    message = json.dumps(
        {
            "user_emails": "Testing",
            "subject": f"{listing_name} Posted Successfully!",
            "html_body": "<strong>Hello, this is a test email.</strong>"
        }
    )

    print(message)

    # AMQP part
    print('\n\n-----Publishing message-----')        
    amqp_setup.channel.basic_publish(
        exchange=amqp_setup.exchangename, 
        routing_key="sendemail", 
        body=message, 
        properties=pika.BasicProperties(delivery_mode=2)
        )

    return listing_result


# Run script
if __name__ == "__main__":
    app.run(port=5001, debug=True)