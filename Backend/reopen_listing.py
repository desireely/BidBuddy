from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from invokes import invoke_http
import amqp_setup
import pika
import json


app = Flask(__name__)
CORS(app)

listing_URL = "http://listing:5007/listing"
bid_URL = "http://bid:5020/bid"
user_URL = "http://user:5005/user"
createlisting_URL = "http://createlisting:5001/createlisting"

@app.route('/reopenlisting/<string:listingid>', methods=['POST'])
def reopen_listing(listingid):
    if request.is_json:
        try:
            newEndDate = request.json["auction_end_datetime"]

            result = process_reopening(newEndDate, listingid)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while reopening listing. " + str(e)
                }
            ), 500
    else:
        return jsonify({
            "code": 400,
            "message": "Invalid JSON input: " + str(request.get_data())
        }), 400

def process_reopening(newEndDate, listingid):

    print('\n-----Invoking listing microservice-----')
    update_result = invoke_http(listing_URL + "/" + listingid, method='PUT', json={"can_reopen": False})
    print('update_result:', update_result)

    code = update_result["code"]
    if code not in range(200, 300):
        return update_result
    
    new_listing = {
        "listing_name" : update_result['data']['listing_name'],
        "listing_description" : update_result['data']['listing_description'],
        "listing_image_url" : update_result['data']['listing_image_url'],
        "auction_end_datetime" : newEndDate,
        "userid" : update_result['data']['userid'],
        "starting_bid" : update_result['data']['starting_bid'],
    }
    print(new_listing)

    print('\n-----Invoking createlisting microservice-----')
    createlisting_result = invoke_http(createlisting_URL, method='POST', json=new_listing)
    print('createlisting_result:', createlisting_result)

    code = createlisting_result["code"]
    if code not in range(200, 300):
        return createlisting_result
    
    ###################### inform buyer #############################
    print('\n-----Invoking bid microservice-----')
    bid_result = invoke_http(bid_URL+'/listing/'+listingid, method='GET')

    # Check the listing result
    code = bid_result["code"]
    if code not in range(200, 300):
        return bid_result

    user_ids = [bid['user_id'] for bid in bid_result['data']['listing']]

    print('\n-----Invoking user microservice-----')
    for user_id in user_ids:
        user_result = invoke_http(user_URL+'/'+user_id, method='GET')
        email = user_result['data']['email']
        teleid = user_result['data']['teleuser']
        listing_name = update_result['data']['listing_name']

        # Preparing message to send via AMQP for email
        message_email = json.dumps(
            {
                "user_emails": [email],
                "subject": f"{listing_name} Transaction",
                "html_body": f"{listing_name} Transaction Confirmed Successfully!"
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

    ###################### inform Seller #############################
    print('\n-----Invoking user microservice-----')
    seller_id = update_result['data']['userid']
    user_result = invoke_http(user_URL+'/'+seller_id, method='GET')
    email = user_result['data']['email']
    teleid = user_result['data']['teleuser']
    listing_name = update_result['data']['listing_name']

    # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": [email],
            "subject": f"{listing_name} Reopened",
            "html_body": f"{listing_name} Reopened Successfully!"
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

    return createlisting_result

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5010, debug=True)