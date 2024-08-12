###just the email
##
##import os.path
##from google.auth.transport.requests import Request
##from google.oauth2.credentials import Credentials
##from google_auth_oauthlib.flow import InstalledAppFlow
##from googleapiclient.discovery import build
##from googleapiclient.errors import HttpError
##
### Define SCOPES
##SCOPES = {
##    'gmail': ['https://www.googleapis.com/auth/gmail.readonly'],
##}
##
### Define file paths
##GMAIL_CREDENTIALS_FILE = 'gmail_credentials.json'
##TOKEN_FILE = 'token.json'
##
##def authenticate(service_name):
##    """Authenticate and return a service object."""
##    creds = None
##    if os.path.exists(TOKEN_FILE):
##        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES[service_name])
##    if not creds or not creds.valid:
##        if creds and creds.expired and creds.refresh_token:
##            creds.refresh(Request())
##        else:
##            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_FILE, SCOPES[service_name])
##            creds = flow.run_local_server(port=0)
##        with open(TOKEN_FILE, 'w') as token:
##            token.write(creds.to_json())
##    return build(service_name, 'v1', credentials=creds)
##
##def get_emails(service):
##    """Get email IDs with specific subject."""
##    query = 'subject:"Your 5K Training Plan!"'
##    email_addresses = []  # Use a list to allow duplicates
##    next_page_token = None
##
##    try:
##        while True:
##            results = service.users().messages().list(userId='me', q=query, pageToken=next_page_token).execute()
##            messages = results.get('messages', [])
##            
##            if not messages:
##                break
##            
##            for message in messages:
##                msg = service.users().messages().get(userId='me', id=message['id']).execute()
##                headers = msg['payload']['headers']
##                for header in headers:
##                    if header['name'] == 'To':
##                        email_addresses.append(header['value'])  # Append to list
##
##            next_page_token = results.get('nextPageToken')
##            if not next_page_token:
##                break
##
##        return email_addresses
##    except Exception as e:
##        print(f'An error occurred: {e}')
##        return []
##
##def write_emails_to_file(emails, file_path='emails.txt'):
##    """Write email addresses to a text file."""
##    try:
##        with open(file_path, 'w') as f:
##            for email in emails:
##                f.write(f"{email}\n")
##        print(f"Email addresses written to {file_path}")
##    except Exception as e:
##        print(f'An error occurred while writing to file: {e}')
##
##def main():
##    try:
##        # Authenticate and build Gmail service
##        gmail_service = authenticate('gmail')
##        email_addresses = get_emails(gmail_service)
##
##        if email_addresses:
##            # Write the email addresses to a text file
##            write_emails_to_file(email_addresses)
##
##    except HttpError as error:
##        print(f'An error occurred: {error}')
##
##if __name__ == '__main__':
##    main()
##
##


# first name AND email

import os.path
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import quopri
from bs4 import BeautifulSoup  # Install BeautifulSoup using `pip install beautifulsoup4`

# Define SCOPES
SCOPES = {
    'gmail': ['https://www.googleapis.com/auth/gmail.readonly'],
}

# Define file paths
GMAIL_CREDENTIALS_FILE = 'gmail_credentials.json'
TOKEN_FILE = 'token.json'

def authenticate(service_name):
    """Authenticate and return a service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES[service_name])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_FILE, SCOPES[service_name])
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build(service_name, 'v1', credentials=creds)

def decode_body(payload):
    if payload.get('body', {}).get('data'):
        body = payload['body']['data']
    else:
        parts = payload.get('parts', [])
        body = next((part['body']['data'] for part in parts if part.get('mimeType') == 'text/plain'), '')
    
    if not body:
        return ''
    
    # Decode from Base64
    decoded = base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8', errors='ignore')
    
    # If it's quoted-printable, decode it
    if '=?' in decoded or '=3D' in decoded:
        decoded = quopri.decodestring(decoded).decode('utf-8', errors='ignore')
    
    return decoded

def extract_first_name(email_body):
    """Extract the first name from the email body."""
    print("Cleaned email body:")
    print(email_body[:200])  # Print the first 200 characters to check the content
    match = re.search(r'Hi (\w+)!', email_body, re.IGNORECASE)
    if match:
        return match.group(1)
    return 'Unknown'


def get_emails(service):
    """Get email IDs with a specific subject and extract first names."""
    query = 'subject:"Your 5K Training Plan!"'
    email_data = []
    next_page_token = None

    try:
        while True:
            results = service.users().messages().list(userId='me', q=query, pageToken=next_page_token).execute()
            messages = results.get('messages', [])
            
            if not messages:
                break
            
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg.get('payload', {})
                
                body = decode_body(payload)
                
                # Debug print
                print("First 100 characters of email body:")
                print(body[:100])
                
                first_name = extract_first_name(body)
                
                # Debug print
                print(f"Extracted name: {first_name}")
                
                headers = payload.get('headers', [])
                to_email = next((header['value'] for header in headers if header['name'] == 'To'), 'Unknown')
                
                email_data.append((first_name, to_email))

            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

        return email_data
    except Exception as e:
        print(f'An error occurred while processing emails: {e}')
        return []

def write_emails_to_file(emails, file_path='emails.txt'):
    """Write email addresses and names to a text file."""
    try:
        with open(file_path, 'w') as f:
            for name, email in emails:
                f.write(f"{name} <{email}>\n")
        print(f"Email addresses and names written to {file_path}")
    except Exception as e:
        print(f'An error occurred while writing to file: {e}')

def main():
    try:
        # Authenticate and build Gmail service
        gmail_service = authenticate('gmail')
        email_data = get_emails(gmail_service)

        if email_data:
            # Write the email addresses and names to a text file
            write_emails_to_file(email_data)

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()


