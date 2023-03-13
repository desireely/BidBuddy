from datetime import datetime, timezone
import pytz
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from flask import Flask, request, jsonify
from flask_cors import CORS

cred = credentials.Certificate("bidCred.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

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


@app.route("/bid", methods=['POST'])
def create_bid():
    newBid = request.json
    newBid["date"] = datetime.now(timezone.utc).astimezone()

    try:
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
    print(newBid)

    return jsonify(
        {
            "code": 201,
            "data": newBid
        }
    ), 201


@app.route("/bid/<int:user_id>", methods=['GET'])
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


@app.route("/bid/listing/<int:listing_id>", methods=['GET'])
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


@app.route("/bid/<int:listing_id>/<int:user_id>", methods=['GET'])
def get_user_bids_for_listing(listing_id, user_id):
    query = db.collection("bid").where("listing_id", "==", listing_id).where("user_id", "==", user_id)

    bid = query.get()
    bid_list = []
    for doc in bid:
        doc = doc.to_dict()
        bid_list.append(doc)
        doc["date"] = doc["date"].astimezone().strftime('%Y-%m-%d %H:%M:%S') + " UTC" + doc["date"].astimezone().strftime('%z')

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
