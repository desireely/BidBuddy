from flask import Flask, request, jsonify
import requests
from invokes import invoke_http

app = Flask(__name__)


listing_URL = "http://127.0.0.1:5000/listing"
bid_URL = "http://127.0.0.1:5000/bid"
user_URL = "http://127.0.0.1:5005/user"
# Subjected to Change
contact_bidders_URL = "http://127.0.0.1:5010/contactbidders"


# Creating / Updating bid for specific listing
@app.route("/bidforlisting/<string:userid>", method=['POST'])
def post_bid(userid):
    if request.is_json:
        try:
            bid_details = request.get_json()
            # Add userid into bid_details
            bid_details['data']['userid'] = userid
            headers = request.headers

            result = processUserBid(headers,bid_details)
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

def processUserBid(headers, bid_details):

    # Invoke the listing microservice
    # To get highest bid details (userid & bid price)
    listing_id = bid_details['data']['listing_details']
    print('\n-----Invoking listing microservice-----')
    ### bid microservice do not required to filter highest bid ###
    highest_result = invoke_http(listing_URL+'/'+listing_id, method='GET')
    high_bid_price = highest_result['highest_current_bid']
    # Add high_bid_price into bid_details
    bid_details['data']['highest_price'] = high_bid_price
    # Use for send notification to previous high bidder
    high_bid_id = highest_result['highest_current_bidder_userid']

    # Invoke the bid microservice
    # Posting the bid 
    print('\n-----Invoking bid microservice-----')
    bid_result = invoke_http(bid_URL, method='POST', json=bid_details)

    # Check the listing result
    code = bid_result["code"]
    if code not in range(200, 300):
        return bid_result
    
    # Invoke the listing microservice
    # Update the new highest bidder details
    new_high = jsonify({
        "highest_current_bid" : bid_result['data']['bid_price'],
        "highest_current_bidder_userid" : bid_result['data']['userid']
    })
    print('\n-----Invoking listing microservice-----')
    listing_result = invoke_http(listing_URL+'/'+listing_id, method='PUT', json=new_high)

    # Check the listing result
    code = listing_result["code"]
    if code not in range(200, 300):
        return listing_result
    
    # Add previous highest bidder id
    ### Do we still need to send highest current bid price since it is the same as bid price ###
    bid_result['data']['high_current_bid_userid'] = high_bid_id # Should we name it prev high bidder?

    # Invoke the contact bidders microservice
    print('\n-----Invoking contact bidders microservice-----')
    listing_result = invoke_http(contact_bidders_URL, method='POST', json=bid_result)


# Run script
if __name__ == "__main__":
    app.run(port=5015, debug=True)