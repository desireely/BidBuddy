from flask import Flask, request, jsonify
import requests
from invokes import invoke_http
import amqp_setup
import json
import pika
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

bid_URL = "http://bid:5020/bid"
# bid_URL = "http://127.0.0.1:5020/bid"
user_URL = "http://user:5005/user"
# user_URL = "http://127.0.0.1:5005/user"
listing_URL = "http://listing:5007/listing"


# Show all user ongoing listing
@app.route("/trackauction", methods=['POST'])
def get_user_listing():
    print("trackauction invoked!")
    if request.is_json:
        try:
            print("Request is: ", request)
            listing_detail = request.get_json()
            print("Listing detail is: ", listing_detail)
            listing_id = listing_detail['listing_id'].split("/")[1]
            result = processTrackAuction(listing_id)
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

def processTrackAuction(listing_id):
    
    # listing_id = listing_detail['listing_id']
    # listing_name = listing_detail['listing_name']
    # Invoke the bid microservice
    
    # INFORM SELLER
    print('\n-----Invoking listing microservice-----')
    listing_result = invoke_http(listing_URL+'/'+listing_id, method='GET')
    listing_name = listing_result['data']['listing_name']
    listing_description = listing_result['data']['listing_description']
    listing_closing_time = listing_result['data']['auction_end_datetime']
    listing_image_url = listing_result['data']['listing_image_url']

    winnerid = listing_result['data']['highest_current_bidder_userid']

    if winnerid == None:
      sellerid = listing_result['data']['userid']
      print('\n-----Invoking user microservice-----')
      seller_result = invoke_http(user_URL+'/'+sellerid, method='GET')
      seller_email = seller_result['data']['email']
      seller_username = seller_result['data']['username']


      # # Preparing message to send via AMQP for email
      message_email = json.dumps(
          {
              "user_emails": [seller_email],
              "subject": f"Bidding closed for {listing_name}",
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
          <h1>Listing Closed</h1>
        </div>
        <div class="description">
          <p>Hi {seller_username}, Your {listing_name} is now closed.</p>
        </div>
        <div class="listing-image">
          <img src="{listing_image_url}" alt="Listing Image">
        </div>
        <div class="listing-details">
          <h2>{listing_name}</h2>
          <p><strong>Description:</strong> {listing_description}</p>
          <p><strong>Closing Time:</strong> {datetime.datetime.fromtimestamp(listing_closing_time).astimezone().strftime('%Y/%m/%d %H:%M:%S')}</p>
        </div>
        <div class="no-bids">
          <p>Sorry, no one bid for your listing.</p>
        </div>
      </div>
    </body>
  </html>     
  """
          }
      )

      print(message_email)

      # # AMQP part
      print('\n\n-----Publishing message-----')       
      amqp_setup.check_setup() 
      amqp_setup.channel.basic_publish(
          exchange=amqp_setup.exchangename, 
          routing_key="send.email", 
          body=message_email, 
          properties=pika.BasicProperties(delivery_mode=2)
          )  

    else:
      # Get all bidders details involved in the listing
      print('\n-----Invoking bid microservice-----')
      bid_result = invoke_http(bid_URL+'/listing/'+listing_id, method='GET')
      
      listing_highest_price = listing_result['data']['highest_current_bid']

      # Check the bid result
      code = bid_result["code"]
      if code not in range(200, 300):
          return bid_result
      
      print(bid_result)
      # Loop through bid result to get all extract their userid to get their contact details
      print('\n-----Invoking user microservice-----')
      winner_result = invoke_http(user_URL+'/'+winnerid, method='GET')
      win_email = winner_result['data']['email']
      win_username = winner_result['data']['username']

      sellerid = listing_result['data']['userid']
      print('\n-----Invoking user microservice-----')
      seller_result = invoke_http(user_URL+'/'+sellerid, method='GET')
      seller_email = seller_result['data']['email']
      seller_username = seller_result['data']['username']

      # # Preparing message to send via AMQP for email to buyer
      message_email = json.dumps(
          {
              "user_emails": [win_email],
              "subject": f"Congratulations! you have the winning bid for {listing_name}",
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
      .contact-seller {{
        text-align: center;
        margin-top: 30px;
      }}
      .contact-seller p {{
        font-size: 18px;
        color: #333;
        margin-top: 0;
        margin-bottom: 10px;
      }}
      .contact-seller a {{
        font-size: 16px;
        color: #0066cc;
        text-decoration: none;
        font-weight: bold;
      }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="title">
          <h1>Listing Closed</h1>
        </div>
        <div class="description">
          <p>Hi {win_username}, you are the highest bidder for {listing_name}!</p>
        </div>
        <div class="listing-image">
          <img src="{listing_image_url}" alt="Listing Image">
        </div>
        <div class="listing-details">
          <h2>{listing_name}</h2>
          <p><strong>Description:</strong> {listing_description}</p>
          <p><strong>Closing Time:</strong> {datetime.datetime.fromtimestamp(listing_closing_time).astimezone().strftime('%Y/%m/%d %H:%M:%S')}</p>
          <p><strong>Winning Bid:</strong> {listing_highest_price}</p>
        </div>
        <div class="contact-seller">
          <p>Please contact the seller at <a href="mailto:{seller_email}">{seller_email}</a> to arrange the transaction within the next 7 days.</p>
        </div>
      </div>
    </body>
  </html>     
  """
          }
      )

      print(message_email)

      # # AMQP part
      print('\n\n-----Publishing message-----') 
      amqp_setup.check_setup()       
      amqp_setup.channel.basic_publish(
          exchange=amqp_setup.exchangename, 
          routing_key="send.email", 
          body=message_email, 
          properties=pika.BasicProperties(delivery_mode=2)
          )


      # # Preparing message to send via AMQP for email to seller
      message_email = json.dumps(
          {
              "user_emails": [seller_email],
              "subject": f"Bidding closed for {listing_name}. Your listing have a winning bid!",
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
      </style>
    </head>
    <body>
      <div class="container">
        <div class="title">
          <h1>Listing Closed</h1>
        </div>
        <div class="description">
          <p>Hi {seller_username}, Your {listing_name} is now closed. Your listing have a winning bid!</p>
        </div>
        <div class="listing-image">
          <img src="{listing_image_url}" alt="Listing Image">
        </div>
        <div class="listing-details">
          <h2>{listing_name}</h2>
          <p><strong>Description:</strong> {listing_description}</p>
          <p><strong>Closing Time:</strong> {datetime.datetime.fromtimestamp(listing_closing_time).astimezone().strftime('%Y/%m/%d %H:%M:%S')}</p>
          <p><strong>Winning Bid:</strong> {listing_highest_price}</p>
        </div>
        <div class="contact-buyer">
          <p>Please contact the bidder at <a href="mailto:{win_email}">{win_email}</a> to arrange the transaction within the next 7 days.</p>
        </div>
      </div>
    </body>
  </html>     
  """
          }
      )

      print(message_email)

      # # AMQP part
      print('\n\n-----Publishing message-----')   
      amqp_setup.check_setup()     
      amqp_setup.channel.basic_publish(
          exchange=amqp_setup.exchangename, 
          routing_key="send.email", 
          body=message_email, 
          properties=pika.BasicProperties(delivery_mode=2)
          )

      emails = []
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
  

      print("Emails: ", list(set(emails)))

      
      # # AMQP
      # # Inform all bidders listing ended

      # # Preparing message to send via AMQP for email
      message_email = json.dumps(
          {
              "user_emails": list(set(emails)),
              "subject": f"Bidding closed for {listing_name}",
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
      </style>
    </head>
    <body>
      <div class="container">
        <div class="title">
          <h1>Listing Closed</h1>
        </div>
        <div class="description">
          <p>Hi bidders, we're sorry to inform you that bidding for {listing_name} is now closed.</p>
        </div>
        <div class="listing-image">
          <img src="{listing_image_url}" alt="Listing Image">
        </div>
        <div class="listing-details">
          <h2>{listing_name}</h2>
          <p><strong>Description:</strong> {listing_description}</p>
          <p><strong>Closing Time:</strong> {datetime.datetime.fromtimestamp(listing_closing_time).astimezone().strftime('%Y/%m/%d %H:%M:%S')}</p>
        </div>
      </div>
    </body>
  </html>     
  """
          }
      )

      print(message_email)

      # # AMQP part
      print('\n\n-----Publishing message-----')        
      amqp_setup.check_setup()
      amqp_setup.channel.basic_publish(
          exchange=amqp_setup.exchangename, 
          routing_key="send.email", 
          body=message_email, 
          properties=pika.BasicProperties(delivery_mode=2)
          )
    



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