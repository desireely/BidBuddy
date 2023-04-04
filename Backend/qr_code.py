from flask import Flask, request, send_file, jsonify
import base64
import qrcode
import io
from flask_cors import CORS
from cryptography.fernet import Fernet
import urllib.parse
import json
import os

# Create the Flask app and enable CORS
app = Flask(__name__)
CORS(app)

KEY_FILE = "key.txt"

# Load the key from the file, or generate a new one if the file doesn't exist
def retrieveKey():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    return key

# Generate a QR code from the encrypted or unencrypted data
@app.route('/qrcode', methods=['POST'])
def generate_qrcode():
    if request.is_json:
        try:
            cipher = Fernet(retrieveKey())

            # Retrieve seller ID and listing ID from the request
            transactionInfo = request.json

            paramsJSON = {"seller_id": transactionInfo["seller_id"], "buyer_id": transactionInfo["buyer_id"], "listing_id": transactionInfo["listing_id"] }
            params = json.dumps(paramsJSON)

            # Encrypt the data and convert it to a URL-safe format
            encrypted_data = cipher.encrypt(params.encode())
            encoded_data = urllib.parse.quote_plus(encrypted_data.decode())

            # base_url = 'http://127.0.0.1:5173/confirmtransaction'
            base_url = 'http://localhost:5173/confirmtransaction'
            listing_id = transactionInfo["listing_id"]

            # Use the encrypted or unencrypted data to create the URL
            url = f"{base_url}?listingID={listing_id}&data={encoded_data}"

            # Generate the QR code image and encode it in base64
            qr = qrcode.QRCode(version=1, box_size=2, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            encoded_string = base64.b64encode(img_io.getvalue()).decode('utf-8')

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while generating the QR Code. " + str(e)
                }
            ), 500
    else:
        return jsonify({
            "code": 400,
            "message": "Invalid JSON input: " + str(request.get_data())
        }), 400

    return jsonify(
        {
            "code": 200,
            "data": encoded_string
        }
    ), 200

# Start the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5009)