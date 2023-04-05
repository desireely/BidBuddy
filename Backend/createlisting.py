from flask import Flask, request, render_template, jsonify
import requests
from invokes import invoke_http
import amqp_setup
import pika
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

listing_URL = "http://listing:5007/listing"
# listing_URL = "http://127.0.0.1:5007/listing"
user_URL = "http://user:5005/user"
# user_URL = "http://127.0.0.1:5005/user"

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

    # Check the listing result
    code = listing_result["code"]
    if code not in range(200, 300):
        return listing_result
    # all the data in listing_result
    # auction_end_datetime = listing_result['data']['auction_end_datetime']
    # highest_current_bid = listing_result['data']['highest_current_bid']
    print(listing_result)
    listing_description = listing_result['data']['listing_description']
    listing_name = listing_result['data']['listing_name']
    starting_bid = listing_result['data']['starting_bid']
    # status = listing_result['data']['status']
    # userid = listing_result['data']['userid']
    listing_image_url = listing_result['data']['listing_image_url']
    # print(listing_image_url)
    # transaction_end_datetime = listing_result['data']['transaction_end_datetime']
    # transaction_status = listing_result['data']['transaction_status']

    # Invoke the user microservice
    print('\n-----Invoking user microservice-----')
    # listing_result = requests.request(url = listing_URL, method='POST', json=listing)
    userid = listing_result['data']['userid']
    user_result = invoke_http(user_URL+'/'+userid, method='GET')
    username = user_result['data']['username']
    email = user_result['data']['email']
    teleid = user_result['data']['teleuser']

    # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": [email],
            "subject": f"{listing_name} Posted Successfully!",
            "html_body":f"""
<html>
  <head>
    <meta charset="utf-8">
    <title>Listing Posted</title>
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
    </style>
  </head>
  <body>
    <div class="container">
      <div class="title">
        <h1>Listing Posted</h1>
      </div>
      <div class="listing-image">
        <img src="{listing_image_url}" alt="Listing Image">
      </div>
      <div class="listing-details">
        <h2>{listing_name}</h2>
        <p><strong>Description:</strong> {listing_description}</p>
        <p><strong>Starting Bid:</strong> {starting_bid}</p>
      </div>
      <div class="description">
        <p>Hello {username}, your listing has been successfully posted!</p>
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
    

    return listing_result


# Run script
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5001, debug=True)