from flask import Flask, request, jsonify
import requests
from invokes import invoke_http
# import amqp_setup
# import pika
# import json

app = Flask(__name__)


listing_URL = "http://127.0.0.1:5000/listing"
user_URL = "http://127.0.0.1:5005/user"


# Add a new listing
@app.route("/showlisting")
def get_ongoing_listing():
        
    try:
        headers = request.headers

        result = processOpenListing(headers)
        print('\n------------------------')
        print('\nresult: ', result)
        return jsonify(result), result["code"]

    except Exception as e:

        return jsonify({
            "code": 500,
            "message": "Error: " + str(e)
        }), 500

def processOpenListing(headers):

    # Invoke the listing microservice
    print('\n-----Invoking listing microservice-----')
    listing_result = invoke_http(listing_URL, method='GET')

    # all the data in listing_result
    open_list = []
    list_loop = listing_result['data']['listings']

    for list in list_loop:
         if list['status'] == 'open':
            # Invoke the user microservice
            print('\n-----Invoking user microservice-----')
            userid = list['userid']
            user_result = invoke_http(user_URL+'/'+userid, method='GET', headers=headers)

            # Check the order result
            code = user_result["code"]
            if code not in range(200, 300):
                return user_result
            
            # Add username to the listing
            list['username'] = user_result['data']['username']
            open_list.append(list)

    # Return all the open listing
    listing_result['data']['listings'] = open_list
    return listing_result


# Run script
if __name__ == "__main__":
    app.run(port=5001, debug=True)