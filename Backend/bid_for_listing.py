from flask import Flask, request, jsonify
import requests
from invokes import invoke_http
import json
import amqp_setup
import pika
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

listing_URL = "http://listing:5007/listing"
bid_URL = "http://bid:5020/bid"
user_URL = "http://user:5005/user"

# Creating / Updating bid for specific listing
@app.route("/bidforlisting", methods=['POST'])
def post_bid():
    if request.is_json:
        try:
            bid_details = request.get_json()

            result = processUserBid(bid_details)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            return jsonify({
                "code": 500,
                "message": "listing.py internal error: " + str(e)
            }), 500
        
    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processUserBid(bid_details):

    # Invoke the listing microservice
    # To get highest bid details (userid & bid price)
    listing_id = bid_details['listing_id']
    print('\n-----Invoking listing microservice-----')
    highest_result = invoke_http(listing_URL+'/'+listing_id, method='GET')
    listing_name = highest_result['data']['listing_name']

    # Add high_bid_price into bid_details
    bid_details['highest_current_bid'] = highest_result['data']['highest_current_bid']
    bid_details['starting_bid'] = highest_result['data']['starting_bid']

    # # Invoke the bid microservice
    # # Posting the bid 
    print('\n-----Invoking bid microservice-----')
    bid_result = invoke_http(bid_URL, method='POST', json=bid_details)

    # Check the bid result
    code = bid_result["code"]
    if code not in range(200, 300):
        return bid_result
    print(bid_details)
    
    # Invoke the listing microservice
    # Update the new highest bidder details
    
    # new_high = json.dumps({
    #     "highest_current_bid" : bid_result['data']['bid_price'],
    #     "highest_current_bidder_userid" : bid_result['data']['user_id']
    # })
    bid_details['highest_current_bid'] = bid_result['data']['bid_price']
    bid_details['highest_current_bidder_userid'] = bid_result['data']['user_id']


    print('\n-----Invoking listing microservice-----')
    listing_result = invoke_http(listing_URL+'/'+listing_id, method='PUT', json=bid_details)

    # Check the listing result
    code = listing_result["code"]
    if code not in range(200, 300):
        return listing_result
    
    #AMQP
    # Send notification for successful bidding
    print('\n-----Invoking user microservice-----')
    user_result = invoke_http(user_URL+'/'+bid_details['highest_current_bidder_userid'], method='GET')
    email = user_result['data']['email']
    teleid = user_result['data']['teleuser']

    # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": [email],
            "subject": f"{listing_name} Posted Successfully!",
            "html_body": "<strong>Hello, this is a test email.</strong>"
        }
    )

    print(message_email)

    # Preparing message to send via AMQP for tele
    # message_tele = json.dumps(
    #     {
    #         "user_teles": [teleid],
    #         "subject": f"{listing_name} Posted Successfully!",
    #         "body": "Hello, this is a test email."
    #     }
    # )

    # print(message_tele)


    # AMQP part

    print('\n\n-----Publishing message-----')        
    amqp_setup.channel.basic_publish(
        exchange=amqp_setup.exchangename, 
        routing_key="send.email", 
        body=message_email, 
        properties=pika.BasicProperties(delivery_mode=2)
        )
    
    # print('\n\n-----Publishing tele-----')        
    # amqp_setup.channel.basic_publish(
    #     exchange=amqp_setup.exchangename, 
    #     routing_key="sendtele", 
    #     body=message_tele, 
    #     properties=pika.BasicProperties(delivery_mode=2)
    #     )
    
    #AMQP
    # Inform previous bidder of outbid status
    # Use for send notification to previous high bidder
    if highest_result['data']['highest_current_bidder_userid'] != None:
        prev_high_id = highest_result['data']['highest_current_bidder_userid']
    
        print('\n-----Invoking user microservice-----')
        user_result = invoke_http(user_URL+'/'+prev_high_id, method='GET')
        email = user_result['data']['email']
        teleid = user_result['data']['teleuser']

        # Preparing message to send via AMQP for email
        message_email = json.dumps(
            {
                "user_emails": [email],
                "subject": f"{listing_name} Posted Successfully!",
                "html_body": "<strong>Hello, this is a test email.</strong>"
            }
        )

        print(message_email)

        # Preparing message to send via AMQP for tele
        # message_tele = json.dumps(
        #     {
        #         "user_teles": [teleid],
        #         "subject": f"{listing_name} Posted Successfully!",
        #         "body": "Hello, this is a test email."
        #     }
        # )

        # print(message_tele)


        # AMQP part
        print('\n\n-----Publishing message-----')        
        amqp_setup.channel.basic_publish(
            exchange=amqp_setup.exchangename, 
            routing_key="send.email", 
            body=message_email, 
            properties=pika.BasicProperties(delivery_mode=2)
            )
        
        # print('\n\n-----Publishing tele-----')        
        # amqp_setup.channel.basic_publish(
        #     exchange=amqp_setup.exchangename, 
        #     routing_key="sendtele", 
        #     body=message_tele, 
        #     properties=pika.BasicProperties(delivery_mode=2)
        #     )

    

    return bid_result

# Run script
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5015, debug=True)