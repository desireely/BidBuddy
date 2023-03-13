from flask import Flask, jsonify, request
from utils import *
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv.main import load_dotenv

load_dotenv()

app = Flask(__name__)


# TO DO

# listing created
# after bidding successful
# when someone overbid you
# when the auction is about to end
# when the auction end
# inform the seller and final highest bidder that bid is successful and they have 7 days to complete transaction
# reminder on the 6th day if transaction not completed
# transaction completed
# seller notified to resell or delete listing when fail

@app.route('/notify_new_listing', methods=['POST'])
def notify_new_listing():

    # seller_data = request.get_json()

    seller_data = {
        "username" : "gay_seller",
        "listing_name" : "ball",
        "listing_description" : "stripes",
        "starting_bid" : 3000,
        "datetime_created" : 1647213165,
        "auction_end": 1647213166,
    }
    
    # check if data needed is available 
    if seller_data and check_attributes(seller_data, ["username", "listing_name", "listing_description", "starting_bid", "datetime_created", "auction_end"]):
        message = Mail(
            from_email='bidbuddy2023@gmail.com',
            to_emails='oreoanytime@gmail.com',
            subject='Listing Posted Successfully!',
            html_content='<strong>Hello, this is a test email.</strong>')
        
        # to edit: html content (email content)

        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        response = sg.send(message)

        # print(response.status_code, response.body)
        # print(response)
        
        return jsonify(
            {
                "code": 200,
                "data": seller_data['username']
            }
        )
    
    return jsonify(
        {
            "code": 400,
            "message": "bad"
        }
    ), 400

    # return if no data or missing data 

if __name__ == '__main__':
    app.run(port=5000, debug=True)
