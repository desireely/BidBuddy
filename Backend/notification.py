from flask import Flask, jsonify, request
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import json
import amqp_setup
from dotenv.main import load_dotenv

load_dotenv()

app = Flask(__name__)


# TO DO

# listing created
# after bidding successful
# when someone overbid you
# when the auction is about to end
# when the auction end
# inform the seller and final highest bidder that bid is successful and they have 7 days to complete transaction
# reminder on the 6th day if transaction not completed
# transaction completed
# seller notified to resell or delete listing when fail

# @app.route('/notify_new_listing', methods=['POST'])

def receivedata():
    print("-----------------------------Notification Running---------------------------------------------")
    amqp_setup.check_setup()
        
    queue_name = 'send_email'
    
    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=send_email, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.



def send_email(channel,method,properties,body):
    # seller_data = request.get_json()
    data = json.loads(body) # needs to include user email, email html body, email eubject

    print(data)
    email = data['user_emails']
    email_subject = data['subject']
    html_body = data['html_body']

    
    # check if data needed is available 
    if data:
        message = Mail(
            from_email='bidbuddy2023@gmail.com',
            to_emails= email,
            subject= email_subject,
            html_content= html_body)
        
        # to edit: html content (email content)

        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        response = sg.send(message)

        print(response.status_code, response.body)
        print(response)
              
    #     return jsonify(
    #         {
    #             "code": 201,
    #             "message": "Email sent successfully"
    #         }
    #     ), 201
    
    # return jsonify(
    #     {
    #         "code": 400,
    #         "message": "Bad Request"
    #     }
    # ), 400

receivedata()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5018, debug=True)
