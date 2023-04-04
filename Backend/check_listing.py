from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from invokes import invoke_http
import amqp_setup
import pika
import json


app = Flask(__name__)
CORS(app)

listing_URL = "http://listing:5007/listing"
user_URL = "http://user:5005/user"

@app.route('/checklisting/<string:listingid>', methods=['POST'])
def check_listing(listingid):
    
    # when triggered invoke get request to retrive the listing record
    try:      

        result = process_listing_status(listingid)
        print('\n------------------------')
        print('\nresult: ', result)
        return jsonify(result), result["code"]

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while checking listing status. " + str(e)
            }
        ), 500

    # check the transaction status to see if it's != closed
    # if not closed, provide option to seller to either reopen or close listing (can be just redirect to anoter page with 2 buttons)

def process_listing_status(listingid):

    print('\n-----Invoking listing microservice-----')
    listing_result = invoke_http(listing_URL + "/" + listingid, method='GET')
    print('listing_result:', listing_result)

    code = listing_result["code"]
    if code not in range(200, 300):
        return listing_result
    
    if listing_result["data"]["transaction_status"] != "closed":
        print('\n-----Invoking listing microservice-----')
        update_result = invoke_http(listing_URL + "/" + listingid, method='PUT', json={"can_reopen": True})
        print('update_result:', update_result)

        code = update_result["code"]
        if code not in range(200, 300):
            return update_result
        
        ###################### inform Seller #############################
        print('\n-----Invoking user microservice-----')
        seller_id = listing_result['data']['userid']
        user_result = invoke_http(user_URL+'/'+seller_id, method='GET')
        email = user_result['data']['email']
        teleid = user_result['data']['teleuser']
        listing_name = update_result['data']['listing_name']

        # Preparing message to send via AMQP for email
        message_email = json.dumps(
            {
                "user_emails": [email],
                "subject": f"{listing_name} Transaction Timeout",
                "html_body": f"{listing_name} Transaction has timed out. If you would like to reopen your listing, please click on this link."
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
        # print('\n\n-----Publishing message-----')        
        # amqp_setup.channel.basic_publish(
        #     exchange=amqp_setup.exchangename, 
        #     routing_key="send.email", 
        #     body=message_email, 
        #     properties=pika.BasicProperties(delivery_mode=2)
        #     )
        
        # print('\n\n-----Publishing tele-----')        
        # amqp_setup.channel.basic_publish(
        #     exchange=amqp_setup.exchangename, 
        #     routing_key="sendtele", 
        #     body=message_tele, 
        #     properties=pika.BasicProperties(delivery_mode=2)
        #     )

        return update_result
    else:
        return jsonify(
            {
                "code": 200,
                "message": "Transaction is closed. "
            }
        ), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5011, debug=True)