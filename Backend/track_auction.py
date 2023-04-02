from flask import Flask, request, jsonify
import requests
from invokes import invoke_http
import amqp_setup
import json
import pika

app = Flask(__name__)

bid_URL = "http://bid:5020/bid"
user_URL = "http://user:5005/user"


# Show all user ongoing listing
@app.route("/trackauction", methods=['POST'])
def get_user_listing():
    if request.is_json:
        try:
            listing_detail = request.get_json()
            result = processTrackAuction(listing_detail)
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

def processTrackAuction(listing_detail):
    
    listing_id = listing_detail['listing_id']
    # listing_name = listing_detail['listing_name']
    # Invoke the bid microservice
    # Get all bidders details involved in the listing
    print('\n-----Invoking bid microservice-----')
    bid_result = invoke_http(bid_URL+'/listing/'+listing_id, method='GET')
    
    # Check the bid result
    code = bid_result["code"]
    if code not in range(200, 300):
        return bid_result
    
    print(bid_result)
    # Loop through bid result to get all extract their userid to get their contact details
    emails = []
    tele = []
    for bid in bid_result['data']['listing']:
        userid = bid['user_id']

        # Invoke the user microservice
        # Retrieve user email and tele
        print('\n-----Invoking user microservice-----')
        user_result = invoke_http(user_URL+'/'+userid, method='GET')

        # Check the user result
        code = user_result["code"]
        if code not in range(200, 300):
            return user_result
        
        emails.append(user_result['data']['email'])
        emails.append(user_result['data']['teleuser'])


        
    # # AMQP
    # # Inform all bidders listing ended

    # # Preparing message to send via AMQP for email
    # message_email = json.dumps(
    #     {
    #         "user_emails": [emails],
    #         "subject": f"{listing_name} Posted Successfully!",
    #         "html_body": "<strong>Hello, this is a test email.</strong>"
    #     }
    # )

    # print(message_email)

    # # Preparing message to send via AMQP for tele
    # # message_tele = json.dumps(
    # #     {
    # #         "user_teles": [teleid],
    # #         "subject": f"{listing_name} Posted Successfully!",
    # #         "body": "Hello, this is a test email."
    # #     }
    # # )

    # # print(message_tele)


    # # AMQP part
    # print('\n\n-----Publishing message-----')        
    # amqp_setup.channel.basic_publish(
    #     exchange=amqp_setup.exchangename, 
    #     routing_key="send.email", 
    #     body=message_email, 
    #     properties=pika.BasicProperties(delivery_mode=2)
    #     )
    
    # # print('\n\n-----Publishing tele-----')        
    # # amqp_setup.channel.basic_publish(
    # #     exchange=amqp_setup.exchangename, 
    # #     routing_key="sendtele", 
    # #     body=message_tele, 
    # #     properties=pika.BasicProperties(delivery_mode=2)
    # #     )

    return bid_result

@app.route("/trackauction1", methods=['GET'])
def test():
        return jsonify(
        {
            "code": 201,
            "data": 'Hello'
        }
    )

# Run script
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5017, debug=True)