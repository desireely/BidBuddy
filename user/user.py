import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from flask import Flask, request, jsonify
from flask_cors import CORS

import hashlib

import re
email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

cred = credentials.Certificate("./userCred.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

#To get details of user
@app.route("/user/<int:userid>")
def find_by_userid(userid):
    query = db.collection('users').where("userid", "==", userid).limit(1)
    user = query.get()
    if len(user):
        return jsonify(
            {
                "code": 200,
                "data": user[0].to_dict()
            }
        )   
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404

#To create a new user
@app.route("/user", methods=['POST'])
def create_user():
    data = request.get_json()
    #Check valid email
    match = re.match(email_regex, data['email'])
    if match:
        #Set userid
        user_ref = db.collection('users').get()
        if user_ref:
            userid = len(user_ref) + 1
            data['userid'] = userid
        else:
            userid = 1
            data['userid'] = userid

        try:
            # Check if user already exists
            query = db.collection("users").where("email", "==", data['email']).limit(1)
            result = query.get()

            if result:
                return jsonify(
                    {
                        "code": 400,
                        "data": {
                            "email": data['email']
                        },
                        "message": "Email is already registered."
                    }
                ), 400

            # Create new user
            users = db.collection('users').document()
            hashed_password = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()
            data["password"] = hashed_password
            users.set(data)

        except:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "email": data['email']
                    },
                    "message": "An error occurred creating the user."
                }
            ), 500
    else:
        return jsonify(
                {
                    "code": 400,
                    "data": {
                        "email": data['email']
                    },
                    "message": "Invalid email entered."
                }
            ), 400
    
    return jsonify(
        {
            "code": 201,
            "data": data
        }
    ), 201

#To update the user details
@app.route("/user/<int:userid>", methods=['PUT'])
def update_user(userid):
    data = request.get_json()
    if data.get('password'):
        data["password"] = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()
    if data.get('email'):
        match = re.match(email_regex, data["email"])
        if not match:
            return jsonify(
                {
                    "code": 400,
                    "data": {
                        "email": data["email"]
                    },
                    "message": "Invalid email entered."
                }
            ), 400
        
    try:
        query = db.collection('users').where("userid", "==", userid).limit(1)
        user = query.get()
        docid = user[0].id
        user_ref = db.collection('users').document(docid)
        user_ref.update(data)
        updated_user = user_ref.get()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "email": data['email']
                },
                "message": "An error occurred updating the user."
            }
        ), 500
    return jsonify(
        {
            "code": 200,
            "data": updated_user.to_dict()
        }
    )

@app.route("/user/<int:userid>", methods=['DELETE'])
def delete_user(userid):
    try:
        query = db.collection('users').where("userid","==",userid).limit(1)
        user = query.get()
        docid = user[0].id
        user_ref = db.collection('users').document(docid)
        user_ref.delete()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "userid": userid
                },
                "message": "User deleted successfully."
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "userid": userid
                },
                "message": f"An error occurred while deleting user: {str(e)}"
            }
        ), 500

    
if __name__ == '__main__':
    app.run(port=5000, debug=True)