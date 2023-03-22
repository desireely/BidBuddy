import firebase_admin
from firebase_admin import credentials, firestore, storage
# import pyrebase

from flask import Flask, request, jsonify, render_template
import datetime
import time
from flask_cors import CORS
import uuid


#####################################
# INITIALISE FIREBASE APP AND DB
#####################################

# Use a service account.
cred = credentials.Certificate('../firebasekey.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()


# firebaseConfig = {
#   "apiKey": "AIzaSyD24Sfv8QG_YD1aaGMCOF-DlnGv6VWjnek",
#   "authDomain": "esd-project-listing.firebaseapp.com",
#   "projectId": "esd-project-listing",
#   "databaseURL": "https://esd-project-listing.firebaseio.com",
#   "storageBucket": "esd-project-listing.appspot.com",
#   "messagingSenderId": "877925820233",
#   "appId": "1:877925820233:web:0c468f7d123ccc39145c98",
#   "measurementId": "G-CZY44KZTDJ"
# }

# firebase = pyrebase.initialize_app(firebaseConfig)

# # database
# firebase.database()
# db = firebase.database()

# # storage
# storage = firebase.storage()



#####################################
# INITIALISE FLASK APP
#####################################
app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Hello world!"



#####################################
# IMAGE
#####################################

@app.route("/uploadimage", methods=['GET', 'POST'])
def upload_image():

    # Parse the image from the request
    image = request.files['image']

    # Process the image as desired
    storage_bucket_name = 'esd-project-listing.appspot.com'
    bucket = storage.bucket(storage_bucket_name)

    file_name_to_store_as = str(uuid.uuid4()) + '-' + image.filename
    blob = bucket.blob(file_name_to_store_as)
    blob.upload_from_string(image.read(), content_type=image.content_type)

    # download image from firebase storage
    storage.bucket(storage_bucket_name).blob(file_name_to_store_as).download_to_filename('downloaded4.jpg')

    return 'Image uploaded and downloaded successfully!'


# download image
@app.route("/retrieveimage", methods=['GET'])
def retrieve_image():

    storage_bucket_name = 'esd-project-listing.appspot.com'
    filename = 'downloaded.jpg'
    filename_to_save_as = 'downloaded5.jpg'

    bucket = storage.bucket(storage_bucket_name)
    bucket.blob(filename).download_to_filename(filename_to_save_as)

    return "<h1>Download successful</h1>"


# get image url
@app.route("/getimageurl")
def get_image_url():

    # image_url = storage.bucket('esd-project-listing.appspot.com').blob('images/example.jpg').path

    storage_bucket_name = 'esd-project-listing.appspot.com'
    image_filename_to_get = 'images/example.jpg'

    bucket = storage.bucket(storage_bucket_name)
    public_image_url = bucket.blob(image_filename_to_get).public_url

    print(public_image_url)

    return "<h1>Gotten image url successfully</h1>"


# delete image
@app.route("/deleteimage")
def delete_image():

    storage_bucket_name = 'esd-project-listing.appspot.com'
    image_filename_to_get = 'images/example.jpg'

    bucket = storage.bucket(storage_bucket_name)
    image_blob = bucket.blob(image_filename_to_get)
    
    image_blob.delete()

    return "<h1>Deleted image successfully from firebase storage</h1>"



#####################################
# LISTING
#####################################

# Get all listings
@app.route("/listing", methods=['GET'])
def get_all_listings():
    listings_collection_ref = db.collection(u'listings')

    try:
        listing_doc_ref = listings_collection_ref.stream()
        listings = [listing.to_dict() for listing in listing_doc_ref]

        if len(listings) == 0:
            return jsonify(
                {
                "code": 404,
                "message": "No listings found"
                }
            )

        # Have listings
        return jsonify(
            {
                "code": 200,
                "data": {
                    "listings": listings
                }
            }
        )

    except:
        return jsonify(
            {
                "code": 404,
                "message": "Error retrieving listings"
            }
        )


# Get a particular listing according to listingid
@app.route("/listing/<string:listingid>", methods=['GET'])
def get_listing_by_listingid(listingid):

    listings_collection_ref = db.collection(u'listings')
    listing_doc_ref = listings_collection_ref.document(listingid)

    try:
        listing = listing_doc_ref.get()
    except:
        return jsonify(
            {
                "code": 404,
                "message": "There is no listing with this listingid"
            }
        ), 404
    
    # user has listings
    return jsonify(
            {
                "code": 200,
                "data": listing.to_dict()
            }
        )



# Add a new listing
@app.route("/listing", methods=['POST'])
def add_listing():

    data = request.get_json()

    # !!!
    # add upload image to firebase storage, get filename and put in "listing_image_file_name" here after UI set up

    listing = {
        u"datetime_created": int(str(time.time()).split(".")[0]),
        u"auction_end_datetime": datetime.datetime.fromisoformat(data["auction_end_datetime"]).timestamp(),
        u"highest_current_bid": data["highest_current_bid"],
        u"highest_current_bidder_userid": data["highest_current_bidder_userid"],
        u"listing_description": data["listing_description"],
        u"listing_name": data["listing_name"],
        u"starting_bid": data["starting_bid"],
        u"status": data["status"],
        u"userid": data["userid"],
        u"transaction_end_datetime": data["transaction_end_datetime"],
        u"transaction_status": data["transaction_status"],
        u"listing_image_file_name": data["listing_image_file_name"]
    }

    try:
        db.collection(u'listings').add(listing)
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error has occurred while adding a listing"
            }
        ), 500
    
    return jsonify(
        {
            "code": 201,
            "data": data
        }
    )


# Update a listing
@app.route("/listing/<string:listingid>", methods=['PUT'])
def update_listing(listingid):

    listing_collection_ref = db.collection(u'listings')
    listing_doc_ref = listing_collection_ref.document(listingid)
    listing = listing_doc_ref.get()

    print(listing.to_dict())
    
    if listing_doc_ref:
        data = request.get_json()
        
        if 'auction_end_datetime' in data:
            listing_doc_ref.update({u'auction_end_datetime': data["auction_end_datetime"]})
        if "highest_current_bid" in data:
            listing_doc_ref.update({u'highest_current_bid': data["highest_current_bid"]})
        if "highest_current_bidder_userid" in data:
            listing_doc_ref.update({u'highest_current_bidder_userid': data["highest_current_bidder_userid"]})
        if "listing_name" in data:
            listing_doc_ref.update({u'listing_name': data["listing_name"]})
        if "starting_bid" in data:
            listing_doc_ref.update({u'starting_bid': data["starting_bid"]})
        if "status" in data:
            listing_doc_ref.update({u'status': data["status"]})
        if "userid" in data:
            listing_doc_ref.update({u'userid': data["userid"]})
        if "listing_image_file_name" in data:
            listing_doc_ref.update({u'listing_image_file_name': data["listing_image_file_name"]})

        return jsonify(
            {
                "code": 200,
                "data": listing.to_dict()
            }
        )
    
    return jsonify(
    {
        "code": 404,
        "data": {
            "listingid": listingid
        },
        "message": "Listing not found."
    }
    ), 404


# Delete a listing
@app.route("/listing/<string:listingid>", methods=['DELETE'])
def delete_listing(listingid):

    try:
        listing_collection_ref = db.collection(u'listings')
        listing_document_ref = listing_collection_ref.document(listingid)
        listing_document_ref.delete()
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error has occurred while deleting a listing"
            }
        ), 500
    
    return jsonify(
        {
            "code": 200,
            "message": "Listing successfully deleted"
        }
    )


# Get all listings that a user bidded for according to his userid
@app.route("/listing/user/<int:userid>", methods=['GET'])
def get_listings_according_userid(userid):

    listing_collection_ref = db.collection(u'listings')
    query_listings_according_userid_ref = listing_collection_ref.where(u'userid', u'==', userid)

    try:
        listings_according_userid = query_listings_according_userid_ref.stream()

        # for listing in listings_according_userid:
        #     print(f'{listing.id} => {listing.to_dict()}')

        listings = [listing.to_dict() for listing in listings_according_userid]

        if len(listings) == 0:
            return jsonify(
                {
                "code": 404,
                "message": "This userid has no listings found"
                }
            )

        # user has listings
        return jsonify(
                {
                    "code": 200,
                    "data": {
                        "listings": listings
                    }
                }
            )

    except:
        return jsonify(
            {
                "code": 404,
                "message": "Error retrieving listings"
            }
        ), 404


#####################################
# RUN SCRIPT
#####################################

if __name__ == "__main__":
    app.run(port=5000, debug=True)

