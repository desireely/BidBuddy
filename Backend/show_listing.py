from flask import Flask, request, jsonify
import requests
from invokes import invoke_http
# import amqp_setup
# import pika
# import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

listing_URL = "http://listing:5007/listing"
# listing_URL = "http://127.0.0.1:5007/listing"
user_URL = "http://user:5005/user"
# user_URL = "http://127.0.0.1:5005/user"


# Show all ongoing listing
@app.route("/showlisting")
def get_ongoing_listing():
        
    try:
        headers = request.headers

        result = processOpenListing()
        print('\n------------------------')
        print('\nresult: ', result)
        return jsonify(result), result["code"]

    except Exception as e:

        return jsonify({
            "code": 500,
            "message": "Error: " + str(e)
        }), 500

def processOpenListing():

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
            user_result = invoke_http(user_URL+'/'+userid, method='GET')

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
    app.run(host='0.0.0.0', port=5006, debug=True)