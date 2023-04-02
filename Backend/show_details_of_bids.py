from flask import Flask, request, jsonify
import requests
from invokes import invoke_http

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

listing_URL = "http://listing:5007/listing"
bid_URL = "http://bid:5020/bid"
user_URL = "http://user:5005/user"


# Show all user ongoing listing
@app.route("/showdetailsofbids/<string:userid>")
def get_user_listing(userid):
    try:
        buyerid = userid

        result = processUserListing(buyerid)
        print('\n------------------------')
        print('\nresult: ', result)
        return jsonify(result), result["code"]
    
    except Exception as e:
        
        print(e)

        return jsonify({
            "code": 500,
            "message": "listing.py internal error: " + str(e)
        }), 500

def processUserListing(buyerid):

    # Invoke the bid microservice
    ### Required to return unique listing with user highest bid ###
    print('\n-----Invoking bid microservice-----')
    bid_result = invoke_http(bid_URL+'/highest/'+buyerid, method='GET')

    # To store user open listing, bid, user details
    open_list = []
    bid_loop = bid_result['data']['bids']

    # Check the listing result
    code = bid_result["code"]
    if code not in range(200, 300):
        return bid_result

    for bid in bid_loop:
        # Invoke the listing microservice
        ### Only display ongoing listing ###
        print('\n-----Invoking listing microservice-----')
        listingid = bid['listing_id']
        listing_result = invoke_http(listing_URL+'/'+listingid, method='GET')

        # Check the listing result
        code = listing_result["code"]
        if code not in range(200, 300):
            return listing_result
    
        
        if listing_result['data']['status'] == 'open':
            # Get seller username
            sellerid = listing_result['data']['userid']
            # Invoke the user microservice
            print('\n-----Invoking user microservice-----')
            user_result = invoke_http(user_URL+'/'+sellerid, method='GET')

            # Check the user result
            code = user_result["code"]
            if code not in range(200, 300):
                return user_result
            
            username = user_result['data']['username']
            
            # Get all required field
            req_obj = {
                "listing_name" : listing_result['data']['listing_name'],
                "auction_end_datetime" : listing_result['data']['auction_end_datetime'],
                "username" : username,
                "highest_current_bid" : listing_result['data']['highest_current_bid'],
                "starting_bid" : listing_result['data']['starting_bid'],
                "listingid" : listing_result['data']['listingid'],
                "listing_image_url" : listing_result['data']['listing_image_url']
            }
            open_list.append(req_obj)


    # Return all user open listing
    return {
        "code": 200,
        "data": open_list
    }

# Run script
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)