from flask import Flask, request, jsonify
import requests
from invokes import invoke_http

app = Flask(__name__)


listing_URL = "http://127.0.0.1:5000/listing"
bid_URL = "http://127.0.0.1:5000/bid"
user_URL = "http://127.0.0.1:5005/user"


# Add a new listing
@app.route("/showdetailsofbids/<string:userid>")
def get_user_listing():
    try:
        user = request.get_json()
        buyerid = user['userid']
        headers = request.headers

        result = processUserListing(headers,buyerid)
        print('\n------------------------')
        print('\nresult: ', result)
        return jsonify(result), result["code"]
    
    except Exception as e:
        
        print(e)

        return jsonify({
            "code": 500,
            "message": "listing.py internal error: " + str(e)
        }), 500

def processUserListing(headers, buyerid):

    # Invoke the bid microservice
    ### Required to return unique listing with user highest bid ###
    print('\n-----Invoking bid microservice-----')
    bid_result = invoke_http(bid_URL+'/'+buyerid, method='GET')

    # To store user open listing, bid, user details
    open_list = []
    bid_loop = bid_result['data']['bids']

    for bid in bid_loop:
        # Invoke the listing microservice
        print('\n-----Invoking listing microservice-----')
        listingid = bid['listing_id']
        listing_result = invoke_http(listing_URL+'/'+listingid, method='GET')

        # Check the listing result
        code = listing_result["code"]
        if code not in range(200, 300):
            return listing_result
        
        # Get seller username
        sellerid = listing_result['userid']
        # Invoke the user microservice
        print('\n-----Invoking user microservice-----')
        user_result = invoke_http(user_URL+'/'+sellerid, method='GET', headers=headers)

        # Check the user result
        code = user_result["code"]
        if code not in range(200, 300):
            return user_result
        
        username = user_result['username']
        
        # Get all required field
        req_obj = {
            "listing_name" : listing_result['listing_name'],
            "auction_end_date_time" : listing_result['auction_end_date_time'],
            "seller_username" : username,
            "highest_bid_price" : listing_result['highest_bid_price'],
            "bid_price" : bid['bid_price']
        }
        open_list.append(req_obj)

    # Return all user open listing
    return jsonify(
            {
                "code": 200,
                "data": open_list
            }
    ), 200

# Run script
if __name__ == "__main__":
    app.run(port=5002, debug=True)
