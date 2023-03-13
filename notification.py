from flask import Flask, request
import requests
import pika
import json
import smtplib

app = Flask(__name__)

@app.route('/create_listing', methods=['POST'])
def create_listing():
    # Create listing logic
    # ...

    # Send notification to user
    user_id = request.form['user_id']
    listing_id = request.form['listing_id']
    notification_message = f"Your listing with ID {listing_id} has been successfully created!"
    send_notification(user_id, notification_message)

    return 'Listing created successfully!'

def send_notification(user_id, message):
    # Replace with your notification service API endpoint
    notification_api_url = 'https://example.com/notifications'

    # Send notification request to the API endpoint
    response = requests.post(notification_api_url, json={
        'user_id': user_id,
        'message': message
    })

    if response.status_code != 200:
        # Handle failed notification
        raise Exception("Failed to send notification to user")
    

# In this example, we use a notification_queue to queue the notifications. We declare the queue with durable=True to ensure that messages are not lost if the RabbitMQ server restarts.

# The send_notification() function sends an email notification to the user. In this example, we use the smtplib Python library to send the email. The email and message parameters are obtained from the notification message payload.

# The callback() function is the message handler that is called each time a new message is consumed from the notification_queue. It parses the notification payload, calls send_notification() to send the email notification, and acknowledges the message with ch.basic_ack(delivery_tag=method.delivery_tag) to remove the message from the queue.

# Finally, we set up the consumer with channel.basic_qos(prefetch_count=1) to ensure that only one message is consumed at a time, and channel.basic_consume() to start consuming messages from the notification_queue.

# You can modify the send_notification() function to use your own email notification service or SMTP server. You can also modify the notification payload to include additional information, such as the listing ID, notification type, and so on.


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='notification_queue', durable=True)

def send_notification(notification):
    email = notification['email']
    message = notification['message']
    sender_email = 'your_email@example.com'
    sender_password = 'your_password'

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)

            subject = 'Notification from Bidding website'
            body = f'{message}'

            msg = f'Subject: {subject}\n\n{body}'

            smtp.sendmail(sender_email, email, msg)

            print(f'Notification sent to {email}')
    except Exception as e:
        print(f'Error sending notification to {email}: {str(e)}')

def callback(ch, method, properties, body):
    notification = json.loads(body)
    send_notification(notification)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='notification_queue', on_message_callback=callback)

print(' [*] Waiting for notifications. To exit press CTRL+C')
channel.start_consuming()