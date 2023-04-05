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

    
    prev_highest_bidder_bid = highest_result['data']['highest_current_bid']
    listing_image_url = highest_result['data']['listing_image_url']

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
    username = user_result['data']['username']
    email = user_result['data']['email']
    bid_price = bid_details['bid_price']
    print(bid_price)

    teleid = user_result['data']['teleuser']

    # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": [email],
            "subject": f"Successful bid!",
            "html_body": f"""
<html>
  <head>
    <meta charset="utf-8">
    <title>Bid Successfully Posted</title>
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
      .title strong {{
        font-size: 36px;
        font-weight: bold;
        margin: 0;
        color: #333;
        display: block;
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
        max-width: 500px;
        margin: 0 auto;
        display: block;
      }}
      .image-wrapper {{
        text-align: center;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="title">
        <strong>Hi {username}! Your recent bid for {listing_name} is successful!</strong>
      </div>
      <div class="image-wrapper">
        <img class="listing-image" src="{listing_image_url}" alt="Listing Image">
      </div>
      <div class="listing-details">
        <h2>{listing_name}</h2>
        <p><strong>Your Bid:</strong> {bid_price}</p>
      </div>
      <div class="description">
        <p>You are currently the highest bidder for this listing.</p>
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
    
    
    #AMQP
    # Inform previous bidder of outbid status
    # Use for send notification to previous high bidder
    if highest_result['data']['highest_current_bidder_userid'] != None:
        prev_high_id = highest_result['data']['highest_current_bidder_userid']
    
        print('\n-----Invoking user microservice-----')
        user_result = invoke_http(user_URL+'/'+prev_high_id, method='GET')
        prev_highest_bidder_name = user_result['data']['username']
        email = user_result['data']['email']
        teleid = user_result['data']['teleuser']

        # Preparing message to send via AMQP for email
        message_email = json.dumps(
            {
                "user_emails": [email],
                "subject": "You have been outbidded!",
                "html_body":f"""
<html>
  <head>
    <meta charset="UTF-8">
    <title>Outbid Notification</title>
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
        max-width: 500px;
        margin: 0 auto;
        display: block;
      }}
      .listing-image {{
        max-width: 500px;
        margin: 0 auto;
        display: block;
      }}
      .image-wrapper {{
        text-align: center;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="title">
        <h1>Outbid Notification</h1>
      </div>
      <div class="description">
        <p>Hi {prev_highest_bidder_name}, your bid for {listing_name} has been outbid!</p>
      </div>
      <div class="image-wrapper">
        <img class="listing-image" src="{listing_image_url}" alt="Listing Image">
      </div>
      <div class="listing-details">
        <h2>{listing_name}</h2>
        <p><strong>Your Bid:</strong> {prev_highest_bidder_bid}</p>
        <p><strong>Current Highest Bid:</strong> {bid_price}</p>
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
    

    return bid_result

# Run script
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5015, debug=True)