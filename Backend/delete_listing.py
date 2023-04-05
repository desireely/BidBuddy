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

@app.route('/deletelisting/<string:listingid>', methods=['DELETE'])
def reopen_listing(listingid):
  try:
      result = process_deletelisting(listingid)
      print('\n------------------------')
      print('\nresult: ', result)
      return jsonify(result), result["code"]

  except Exception as e:
      return jsonify(
          {
              "code": 500,
              "message": "An error occurred while deleting listing. " + str(e)
          }
      ), 500

def process_deletelisting(listingid):

    ###################### To store inform #############################
    print('\n-----Invoking listing microservice-----')
    listing_result = invoke_http(listing_URL + "/" + listingid, method='GET')
    print('listing_result:', listing_result)

    code = listing_result["code"]
    if code not in range(200, 300):
        return listing_result
    
    listing_name = listing_result['data']['listing_name']
    listing_description = listing_result['data']['listing_description']
    listing_image_url = listing_result['data']['listing_image_url']

    print('\n-----Invoking listing microservice-----')
    delete_result = invoke_http(listing_URL + "/" + listingid, method='DELETE')
    print('delete_result:', delete_result)


    ###################### inform Seller #############################
    print('\n-----Invoking user microservice-----')
    seller_id = listing_result['data']['userid']
    user_result = invoke_http(user_URL+'/'+seller_id, method='GET')
    email = user_result['data']['email']
    listing_name = listing_result['data']['listing_name']

    # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": [email],
            "subject": f"{listing_name} has been deleted",
            "html_body": f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Listing Deleted</title>
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
        <h1>Listing Deleted</h1>
      </div>
      <div class="description">
        <p>You have successfully deleted your listing for {listing_name}.</p>
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
    amqp_setup.check_setup()
    print('\n\n-----Publishing message-----')        
    amqp_setup.channel.basic_publish(
        exchange=amqp_setup.exchangename, 
        routing_key="send.email", 
        body=message_email, 
        properties=pika.BasicProperties(delivery_mode=2)
        )

    code = delete_result["code"]
    if code not in range(200, 300):
        return delete_result
    
    ###################### inform buyer #############################
    print('\n-----Invoking bid microservice-----')
    bid_result = invoke_http(bid_URL+'/listing/'+listingid, method='GET')

    # Check the listing result
    code = bid_result["code"]
    if code == 404:
        return delete_result

    user_ids = [bid['user_id'] for bid in bid_result['data']['listing']]


    print('\n-----Invoking user microservice-----')
    email_list = []
    for user_id in user_ids:
        user_result = invoke_http(user_URL+'/'+user_id, method='GET')
        email = user_result['data']['email']
        email_list.append(email)
    
    # Preparing message to send via AMQP for email
    message_email = json.dumps(
        {
            "user_emails": email_list,
            "subject": f"{listing_name} has been deleted",
            "html_body": f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Listing Deleted</title>
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
        <h1>Listing Deleted</h1>
      </div>
      <div class="description">
        <p>Sorry, the seller has recently deleted this listing :(</p>
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
    amqp_setup.check_setup()
    print('\n\n-----Publishing message-----')        
    amqp_setup.channel.basic_publish(
        exchange=amqp_setup.exchangename, 
        routing_key="send.email", 
        body=message_email, 
        properties=pika.BasicProperties(delivery_mode=2)
        )
        

    ###################### delete bid details #############################
    print('\n-----Invoking bid microservice-----')
    dbid_result = invoke_http(bid_URL+'/'+listingid, method='DELETE')

    return delete_result

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5025, debug=True)