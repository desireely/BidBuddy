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
    print(buyer_id)
    user_result = invoke_http(user_URL+'/'+buyer_id, method='GET')
    print(user_result)
    buyer_email = user_result['data']['email']
    print(listing_result)
    listing_name = update_result['data']['listing_name']
    listing_image_url = update_result['data']['listing_image_url']
    listing_description = update_result['data']['listing_description']

    # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": [buyer_email],
            "subject": f"{listing_name} Transaction",
            "html_body":  f"""
  <html>
    <head>
      <meta charset="UTF-8">
      <title>Listing Closed</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f5f5f5;
        }}
        .container {{
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          background-color: #fff;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        .title {{
          text-align: center;
          margin-bottom: 20px;
        }}
        .title h1 {{
          font-size: 36px;
          font-weight: bold;
          margin: 0;
          color: #333;
        }}
        .description {{
          font-size: 20px;
          color: #666;
          margin-bottom: 40px;
          text-align: center;
        }}
        .listing-details {{
          margin-bottom: 20px;
          padding: 20px;
          background-color: #f5f5f5;
          border: 1px solid #ddd;
          border-radius: 5px;
        }}
        .listing-details h2 {{
          font-size: 24px;
          font-weight: bold;
          margin-top: 0;
          margin-bottom: 10px;
          color: #333;
        }}
        .listing-details p {{
          font-size: 16px;
          color: #666;
          margin-top: 0;
        }}
        .listing-image {{
          text-align: center;
          margin-bottom: 20px;
        }}
        .listing-image img {{
          max-width: 100%;
          height: auto;
          border-radius: 5px;
        }}
      .no-bids {{
        font-size: 18px;
        text-align: center;
        color: #666;
        margin-top: 20px;
      }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="title">
          <h1>Transaction confirmed</h1>
        </div>
        <div class="description">
          <p>Successful transaction for {listing_name} </p>
        </div>
        <div class="listing-image">
          <img src="{listing_image_url}" alt="Listing Image">
        </div>
        <div class="listing-details">
          <h2>{listing_name}</h2>
          <p><strong>Description:</strong> {listing_description}</p>
        </div>
        <div class="no-bids">
          <p>Thank you for using BidBuddy!</p>
        </div>
      </div>
    </body>
  </html>     
  """
        }
    )

    print(message_email)


    # AMQP part
    print('\n\n-----Publishing message-----')
    amqp_setup.check_setup()   
    amqp_setup.channel.basic_publish(
        exchange=amqp_setup.exchangename, 
        routing_key="send.email", 
        body=message_email, 
        properties=pika.BasicProperties(delivery_mode=2)
        )
    

    ###################### inform Seller #############################
    print('\n-----Invoking user microservice-----')
    seller_id = data['seller_id']
    print(seller_id)
    user_result = invoke_http(user_URL+'/'+seller_id, method='GET')
    print(user_result)
    seller_email = user_result['data']['email']

    # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": [seller_email],
            "subject": f"{listing_name} Transaction",
            "html_body": f"""
  <html>
    <head>
      <meta charset="UTF-8">
      <title>Listing Closed</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f5f5f5;
        }}
        .container {{
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          background-color: #fff;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        .title {{
          text-align: center;
          margin-bottom: 20px;
        }}
        .title h1 {{
          font-size: 36px;
          font-weight: bold;
          margin: 0;
          color: #333;
        }}
        .description {{
          font-size: 20px;
          color: #666;
          margin-bottom: 40px;
          text-align: center;
        }}
        .listing-details {{
          margin-bottom: 20px;
          padding: 20px;
          background-color: #f5f5f5;
          border: 1px solid #ddd;
          border-radius: 5px;
        }}
        .listing-details h2 {{
          font-size: 24px;
          font-weight: bold;
          margin-top: 0;
          margin-bottom: 10px;
          color: #333;
        }}
        .listing-details p {{
          font-size: 16px;
          color: #666;
          margin-top: 0;
        }}
        .listing-image {{
          text-align: center;
          margin-bottom: 20px;
        }}
        .listing-image img {{
          max-width: 100%;
          height: auto;
          border-radius: 5px;
        }}
      .no-bids {{
        font-size: 18px;
        text-align: center;
        color: #666;
        margin-top: 20px;
      }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="title">
          <h1>Transaction confirmed</h1>
        </div>
        <div class="description">
          <p>Successful transaction for {listing_name} </p>
        </div>
        <div class="listing-image">
          <img src="{listing_image_url}" alt="Listing Image">
        </div>
        <div class="listing-details">
          <h2>{listing_name}</h2>
          <p><strong>Description:</strong> {listing_description}</p>
        </div>
        <div class="no-bids">
          <p>Thank you for using BidBuddy!</p>
        </div>
      </div>
    </body>
  </html>     
  """
        }
    )

    print(message_email)


    # AMQP part
    print('\n\n-----Publishing message-----')
    amqp_setup.check_setup()
    amqp_setup.channel.basic_publish(
        exchange=amqp_setup.exchangename, 
        routing_key="send.email", 
        body=message_email, 
        properties=pika.BasicProperties(delivery_mode=2)
        )
    

    return update_result

# Start the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5008)