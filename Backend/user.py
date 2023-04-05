import firebase_admin
from firebase_admin import credentials, firestore, auth

from flask import Flask, request, jsonify
from flask_cors import CORS

import re
email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

cred = credentials.Certificate("./firebasekey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

#To get details of user
@app.route("/user/<string:userid>")
def find_by_userid(userid):
    # if check_auth():
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
                "data" : '',
                "message": "User not found."
            }
        ), 404
    # else:
    #     return jsonify(
    #         {
    #             "code": 401,
    #             "message": "Unauthorised."
    #         }
    #     ), 401

#To get userid using teleuser
@app.route("/user/tele/<string:teleuser>")
def find_by_teleid(teleuser):
    query = db.collection('users').where("teleuser", "==", teleuser).limit(1)
    user = query.get()
    print("user: ", user[0].to_dict())
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
            "data" : '',
            "message": "No matching tele id."
        }
        ), 404

#To create a new user
@app.route("/user", methods=['POST'])
def create_user():
    data = request.get_json()
    #Check valid email and password
    if verify_info(data['email'],data['password']):
        #Set userid
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

            # Add user into firebase authentication
            auth.create_user(email=data['email'], password=data['password'])
            # Create new user
            user = auth.get_user_by_email(data['email'])
            user_id = user.uid
            #Set userid
            data['userid'] = user_id
            user_ref = db.collection('users').document()
            #Remove password from data
            data.pop('password')
            user_ref.set(data)

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
                    "message": "Invalid email or password less than 6 characters"
                }
            ), 400
    
    return jsonify(
        {
            "code": 201,
            "data": data
        }
    ), 201

#To update the user details
@app.route("/user/<string:userid>", methods=['PUT'])
def update_user(userid):
    # if check_auth():
        data = request.get_json()
        try:
            query = db.collection('users').where("userid", "==", userid).limit(1)
            user = query.get()
            docid = user[0].id
            user_ref = db.collection('users').document(docid)
            username = user_ref.get().to_dict()['username']

            #Update email in firestore
            user_ref.update(data)
            updated_user = user_ref.get()
        except:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "username": username
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
    # else:
    #     return jsonify(
    #         {
    #             "code": 401,
    #             "message": "Unauthorised."
    #         }
    #     ), 401

@app.route("/user/<string:userid>", methods=['DELETE'])
def delete_user(userid):
    # if check_auth():
        try:
            #Delete data from firestore
            query = db.collection('users').where("userid","==",userid).limit(1)
            user = query.get()
            docid = user[0].id
            user_ref = db.collection('users').document(docid)
            username = user_ref.get().to_dict()['username']
            user_ref.delete()

            #Delete data from firebase authentication
            auth.delete_user(userid)

            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "username": username
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
    # else:
    #     return jsonify(
    #         {
    #             "code": 401,
    #             "message": "Unauthorised."
    #         }
    #     ), 401
        

# def check_auth():
#     # Get the Firebase ID token from the request header
#     try:
#         # Verify the Firebase ID token
#         id_token = request.headers.get('Authorization')
#         auth.verify_id_token(id_token)
#         return True
#     except:
#         return False

def verify_info(email,password):
    if re.match(email_regex, email) and len(password) >= 6:
        return True
    else:
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)