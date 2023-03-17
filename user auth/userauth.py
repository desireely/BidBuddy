import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from flask import Flask, request, jsonify
from flask_cors import CORS

import hashlib

cred = credentials.Certificate("../user/userCred.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

#To authenticate user 
@app.route("/user/login", methods=['POST'])
def user_auth():
    data = request.get_json()

    # Check if user already exists
    query = db.collection("users").where("email", "==", data['email']).limit(1)
    user = query.get()
    if user:
        user = user[0].to_dict()
        if user['password'] == hashlib.sha256(data["password"].encode('utf-8')).hexdigest():
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "userid" : user['userid'],
                        "user": user['username']
                    },
                    "message": "Successful Logged In."
                }
            ), 200
    return jsonify(
        {
            "code": 400,
            "data": {
                "email": data['email']
            },
            "message": "Invalid Email Or Password"
        }
    ), 400
        
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5100, debug=True)