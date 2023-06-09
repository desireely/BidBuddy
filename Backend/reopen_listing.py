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

    listing_name = update_result['data']['listing_name']
    listing_description = update_result['data']['listing_description']
    listing_image_url = update_result['data']['listing_image_url']
    email_list = []
    print('\n-----Invoking user microservice-----')
    for user_id in user_ids:
        user_result = invoke_http(user_URL+'/'+user_id, method='GET')
        email = user_result['data']['email']
        email_list.append(email)
        

        # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": email_list,
            "subject": f"Hey bidders! {listing_name} is reopened for bidding!",
            "html_body": f"""
<html>
  <head>
    <meta charset="utf-8">
    <title>Reopened Listing</title>
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
        <h1>Hey bidders!</h1>
      </div>
      <div class="description">
        <p>The following listing has been reopened for bidding!</p>
      </div>
      <div class="listing-image">
        <img src="{listing_image_url}" alt="Listing Image">
      </div>
      <div class="listing-details">
        <h2>{listing_name}</h2>
        <p><strong>Description:</strong> {listing_description}</p>
      </div>
      <div class="title">
        <h1>Happy bidding!</h1>
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
        


    ###################### inform Seller #############################
    print('\n-----Invoking user microservice-----')
    seller_id = update_result['data']['userid']
    user_result = invoke_http(user_URL+'/'+seller_id, method='GET')
    username = user_result['data']['username']
    email = user_result['data']['email']
    teleid = user_result['data']['teleuser']
    listing_name = update_result['data']['listing_name']

    # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": [email],
            "subject": f"{listing_name} Reopened Successfully!",
            "html_body": f"""
<html>
  <head>
    <meta charset="utf-8">
    <title>Reopened Listing</title>
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
        <h1>Hi {username}!</h1>
      </div>
      <div class="description">
        <p>You have successfully reopened the following listing:</p>
      </div>
      <div class="listing-image">
        <img src="{listing_image_url}" alt="Listing Image">
      </div>
      <div class="listing-details">
        <h2>{listing_name}</h2>
        <p><strong>Description:</strong> {listing_description}</p>
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
    

    return createlisting_result

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5010, debug=True)