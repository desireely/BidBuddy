from datetime import datetime, timezone
import json
from os import environ

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from flask import Flask, request, jsonify
from flask_cors import CORS

cred = credentials.Certificate("./firebasekey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

@app.route("/bid", methods=['POST'])
def create_bid():
    newBid = request.json
    newBid["date"] = datetime.now(timezone.utc).astimezone()

    # highest_price = db.collection("bid").where("listing_id", "==", newBid["listing_id"]).order_by('bid_price', direction=firestore.Query.DESCENDING).limit(1).get()


    highest_price = newBid.pop('highest_current_bid')
    starting_bid = newBid.pop("starting_bid", None)
    
    if highest_price:
        if 0.01 <= highest_price and highest_price < 1:
            bid_increment = 0.05
        elif 1 <= highest_price and highest_price < 5:
            bid_increment = 0.25
        elif 5 <= highest_price and highest_price < 25:
            bid_increment = 0.50
        elif 25 <= highest_price and highest_price < 100:
            bid_increment = 1
        elif 100 <= highest_price and highest_price < 250:
            bid_increment = 2.5
        elif 250 <= highest_price and highest_price < 500:
            bid_increment = 5
        elif 500 <= highest_price and highest_price < 1000:
            bid_increment = 10
        elif 1000 <= highest_price and highest_price < 2500:
            bid_increment = 25
        elif 2500 <= highest_price and highest_price < 5000:
            bid_increment = 50
        elif highest_price >= 5000:
            bid_increment = 100

        try:
            if newBid["bid_price"]-highest_price < bid_increment:
                raise Exception(f"Minimum bid increment is ${'{:.2f}'.format(bid_increment)}.")

            doc_ref = db.collection("bid").document()
            doc_ref.set(newBid)

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while creating the bid. " + str(e)
                }
            ), 500
    else:
        try:            
            if newBid["bid_price"] >= starting_bid:
                doc_ref = db.collection("bid").document()
                doc_ref.set(newBid)
            else:
                raise Exception(f"Bid price is lower than the start price of ${'{:.2f}'.format(starting_bid)}.")

            doc_ref = db.collection("bid").document()
            doc_ref.set(newBid)

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while creating the bid. " + str(e)
                }
            ), 500


    newBid["date"] = newBid["date"].strftime('%Y-%m-%d %H:%M:%S') + " UTC" + newBid["date"].astimezone().strftime('%z')

    return jsonify(
        {
            "code": 201,
            "data": newBid
        }
    ), 201


@app.route("/bid/user/<string:user_id>", methods=['GET'])
def get_user_bids(user_id):
    query = db.collection("bid").where("user_id", "==", user_id)

    bids = query.get()
    userBids = []
    for bid in bids:
        bid = bid.to_dict()
        bid["date"] = bid["date"].astimezone().strftime('%Y-%m-%d %H:%M:%S') + " UTC" + bid["date"].astimezone().strftime('%z')
        userBids.append(bid)

    if len(bids):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bids": userBids
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {"user_id": user_id},
            "message": "There are no bids placed by the user."
        }
    ), 404


@app.route("/bid/listing/<string:listing_id>", methods=['GET'])
def get_listing_bids(listing_id):
    query = db.collection("bid").where("listing_id", "==", listing_id)

    listings = query.get()
    listingBids = []
    for listing in listings:
        listing = listing.to_dict()
        listing["date"] = listing["date"].astimezone().strftime('%Y-%m-%d %H:%M:%S') + " UTC" + listing["date"].astimezone().strftime('%z')
        listingBids.append(listing)

    if len(listings):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "listing": listingBids
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {"listing_id": listing_id},
            "message": "No bids have been placed on this listing."
        }
    ), 404


@app.route("/bid/<string:listing_id>/<string:user_id>", methods=['GET'])
def get_user_bids_for_listing(listing_id, user_id):
    query = db.collection("bid").where("listing_id", "==", listing_id).where("user_id", "==", user_id)

    bid = query.get()
    bid_list = []
    for doc in bid:
        doc = doc.to_dict()
        doc["date"] = doc["date"].astimezone().strftime('%Y-%m-%d %H:%M:%S') + " UTC" + doc["date"].astimezone().strftime('%z')
        bid_list.append(doc)

    if len(bid):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bids": bid_list
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "listing_id": listing_id,
                "user_id": user_id
            },
            "message": "User has not bid for this listing."
        }
    ), 404

@app.route("/bid/highest/<string:user_id>")
def get_user_highest_bids(user_id):
    query = db.collection("bid").where("user_id", "==", user_id).order_by('bid_price', direction=firestore.Query.DESCENDING)

    bids = query.get()
    unique_listing = []
    result = []
    for bid in bids:
        bid = bid.to_dict()
        bid["date"] = bid["date"].astimezone().strftime('%Y-%m-%d %H:%M:%S') + " UTC" + bid["date"].astimezone().strftime('%z')
        listing_id = bid["listing_id"]

        if listing_id not in unique_listing:
            unique_listing.append(listing_id)
            result.append(bid)

    if len(bids):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bids": result
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {"user_id": user_id},
            "message": "There are no bids placed by the user."
        }
    ), 404

@app.route("/bid", methods=['GET'])
def get_all_bids():
    bids = db.collection("bid").get()
    allBids = []
    for bid in bids:
        bid = bid.to_dict()
        bid["date"] = bid["date"].astimezone().strftime('%Y-%m-%d %H:%M:%S') + " UTC" + bid["date"].astimezone().strftime('%z')
        allBids.append(bid)

    if len(bids):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bids": allBids
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no bids."
        }
    ), 404

# @app.route("/bid/<string:listing_id>/<string:user_id>/<float:bid_price>", methods=['DELETE'])
# def delete_bid(listing_id, user_id, bid_price):
#     query = db.collection("bid").where("listing_id", "==", listing_id).where("user_id", "==", user_id).where("bid_price", "==", bid_price)

#     bid = query.get()
#     for doc in bid:
#         try:
#             delBid = doc.to_dict()
#             doc.reference.delete()
#         except Exception as e:
#             return jsonify(
#                 {
#                     "code": 500,
#                     "message": "An error occurred while deleting the bid. " + str(e)
#                 }
#             ), 500
#     return jsonify(
#         {
#             "code": 200,
#             "data": delBid,
#             "message": "Bid has been deleted successfully."
#         }
#     ), 200

@app.route("/bid/<string:listingid>", methods=['DELETE'])
def delete_bids(listingid):
    query = db.collection("bid").where("listing_id", "==", listingid)

    bids = query.get()
    
    try:
        for bid in bids:
            bid.reference.delete()
        return jsonify(
            {
                "code": 200,
                "message": "Bid has been deleted successfully."
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while deleting the bid. " + str(e)
            }
        ), 500
      
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5020, debug=True)
