from flask import Flask, request, send_file, jsonify
import base64
import qrcode
import io
from flask_cors import CORS
from cryptography.fernet import Fernet
import urllib.parse
import json

app = Flask(__name__)
CORS(app)

@app.route('/test', methods=['GET', 'POST'])
def test_function():
    return jsonify({"data":"the test has succeeded"})

@app.route('/test1', methods=['GET', 'POST'])
def decrypting():
    # Decrypt the data from the URL
    key = Global_key

    data = request.get_json()
    url = data["url"]

    print(url)

    
    # Parse the query string from the URL
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    print("")
    print(query_params)

    # Extract the encrypted data from the query string
    encrypted_str_data = query_params.get('data', [''])[0]
    print("")
    print(encrypted_str_data)
    print(type(encrypted_str_data))

    encrypted_byte_data = encrypted_str_data.encode('utf-8')

    print("")
    print(encrypted_byte_data)
    print(type(encrypted_byte_data))

    # return ""
    # # Convert the encrypted data from a string to bytes
    # encrypted_data = bytes.fromhex(encrypted_data)

    # Create a Fernet object with the encryption key
    fernet = Fernet(key)

    # Decrypt the data using the Fernet object
    decrypted_data = fernet.decrypt(encrypted_byte_data)

    # Convert the decrypted data back to its original format
    original_data = decrypted_data.decode('utf-8')

    # return decrypted_data
    return original_data


@app.route('/qrcode', methods=['GET', 'POST'])
def generate_qrcode():

    encoded_data = encrypt()

    base_url = request.args.get('url', 'http://localhost/project/Clem/Version_1.6/login')
    url = f"{base_url}?data={encoded_data}"



    # Generate QR code as an in-memory image file
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    # Encode image data in base64
    encoded_string = base64.b64encode(img_io.getvalue()).decode('utf-8')
    html = f'<img src="data:image/png;base64,{encoded_string}" />'
    # Return the image file as a response with appropriate content type
    return html

def generate_key():
    # Generate a secret key
    key = Fernet.generate_key()

    return key

Global_key = generate_key()

def encrypt():
    Global_key

    # Create a Fernet cipher object with the secret key
    cipher = Fernet(Global_key)

    # Get data and URL from query parameters
    seller_id = request.args.get('data', '12345')
    listing_id = request.args.get('data', '67890')
    paramsJSON = {"seller_id": seller_id, "listing_id": listing_id }
    params = json.dumps(paramsJSON)
    # encoded_params = urllib.parse.urlencode(params)

    # Encrypt the data
    encrypted_data = cipher.encrypt(params.encode())

    # Convert the encrypted data to a URL-safe format
    encoded_data = urllib.parse.quote_plus(encrypted_data.decode())

    return encoded_data



if __name__ == "__main__":
    app.run(debug=True)
