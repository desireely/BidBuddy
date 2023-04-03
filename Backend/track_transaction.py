from flask import Flask, request, send_file, jsonify
from invokes import invoke_http
import base64
import qrcode
import io
from flask_cors import CORS
from cryptography.fernet import Fernet
import urllib.parse
import json
import os
import amqp_setup
import pika

# Create the Flask app and enable CORS
app = Flask(__name__)
CORS(app)

listing_URL = "http://listing:5007/listing"
# listing_URL = "http://127.0.0.1:5007/listing"
user_URL = "http://user:5005/user"
# user_URL = "http://127.0.0.1:5005/user"

KEY_FILE = "key.txt"

@app.route("/tracktransaction", methods=['POST'])
def tracktransaction():

    print("Track transaction invoked!")
    if request.is_json:
        try:
            print("Request is: ", request)
            listing_detail = request.get_json()
            print("Listing detail is: ", listing_detail)
        except Exception as e:
            print(e)

    return "Track transaction here!"

# Load the key from the file, or generate a new one if the file doesn't exist
def retrieveKey():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    return key

# Decrypt the data using the secret key
@app.route('/confirmtransaction', methods=['POST'])
def confirm_transaction():
    # Retrieve the encrypted data from the request URL
    if request.is_json:
        try:
            info = request.json
            print("Received transaction details in JSON order", info)
            key = retrieveKey()

            # Decrypt the data and convert it back to its original format
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(info["data"])
            original_data = decrypted_data.decode('utf-8')
            data = json.loads(original_data)
            print(data)

            if info["user_id"] != data["buyer_id"]:
                raise Exception("Invalid buyer confirmation.")        

            result = process_transaction(data)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while confirming transaction. " + str(e)
                }
            ), 500
    else:
        return jsonify({
            "code": 400,
            "message": "Invalid JSON input: " + str(request.get_data())
        }), 400

def process_transaction(data):

    print('\n-----Invoking listing microservice-----')
    listing_result = invoke_http(listing_URL + "/" + data["listing_id"], method='GET')
    print('listing_result:', listing_result)

    code = listing_result["code"]
    if code not in range(200, 300):
        return listing_result
    
    try:
        if data["seller_id"] != listing_result["data"]["userid"] or data["buyer_id"] != listing_result["data"]["highest_current_bidder_userid"]:
            raise Exception("Seller or buyer mismatch.")  
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while confirming transaction. " + str(e)
            }
        ), 500 

    print('\n-----Invoking listing microservice-----')
    update_result = invoke_http(listing_URL + "/" + data["listing_id"], method='PUT', json={"transaction_status": "closed"})
    print('update_result:', update_result)

    code = update_result["code"]
    if code not in range(200, 300):
        return update_result
    
    ###################### inform buyer #############################
    print('\n-----Invoking user microservice-----')
    buyer_id = data['buyer_id']
    user_result = invoke_http(user_URL+'/'+buyer_id, method='GET')
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
    seller_id = data['seller_id']
    user_result = invoke_http(user_URL+'/'+seller_id, method='GET')
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

# Start the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5008)