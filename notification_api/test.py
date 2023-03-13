from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv.main import load_dotenv

load_dotenv()

message = Mail(
    from_email='bidbuddy2023@gmail.com',
    to_emails='oreoanytime@gmail.com',
    subject='Test email',
    html_content='<strong>Hello, this is a test email.</strong>')

sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
response = sg.send(message)

print(response)