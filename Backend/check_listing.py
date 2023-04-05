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
        username = user_result['data']['username']
        teleid = user_result['data']['teleuser']
        listing_name = update_result['data']['listing_name']
        listing_description = update_result['data']['listing_description']
        listing_image_url = update_result['data']['listing_image_url']
        

        # Preparing message to send via AMQP for email
        message_email = json.dumps(
            {
                "user_emails": [email],
                "subject": f"{listing_name} Transaction Timeout",
                "html_body": f"""
<html>
  <head>
    <meta charset="utf-8">
    <title>Closed Listing</title>
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
      .re-open-link {{
        text-align: center;
        margin-top: 40px;
      }}
      .re-open-link a {{
        display: inline-block;
        padding: 10px 20px;
        background-color: #f44336;
        color: #fff;
        text-decoration: none;
        font-size: 16px;
        font-weight: bold;
        border-radius: 5px;
      }}
      .re-open-link a:hover {{
        background-color: #d32f2f;
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
    </style>
  </head>
  <body>
    <div class="container">
      <div class="title">
        <h1>Closed Listing</h1>
      </div>
      <div class="description">
        <p>Hi {username}, due to inactivity, we have closed the following listing:</p>
      </div>
      <div class="listing-image">
        <img src="{listing_image_url}" alt="Listing Image">
      </div>
      <div class="listing-details">
        <h2>{listing_name}</h2>
        <p><strong>Description:</strong> {listing_description}</p>
      </div>
      <div class="re-open-link">
        <p>If you wish to reopen the listing, you can click on this <a href="http://127.0.0.1/reopenlisting/{listingid}">link</a></p>
      </div>
    </div>
  </body>
</html>

"""
            }
        )

        print(message_email)


        # AMQP part
        amqp_setup.check_setup()
        print('\n\n-----Publishing message-----')        
        amqp_setup.channel.basic_publish(
            exchange=amqp_setup.exchangename, 
            routing_key="send.email", 
            body=message_email, 
            properties=pika.BasicProperties(delivery_mode=2)
            )

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