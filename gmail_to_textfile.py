#just the email

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

def get_emails(service):
   """Get email IDs with specific subject."""
   query = 'subject:"Your 5K Training Plan!"'
   email_addresses = []  # Use a list to allow duplicates
   next_page_token = None

   try:
       while True:
           results = service.users().messages().list(userId='me', q=query, pageToken=next_page_token).execute()
           messages = results.get('messages', [])
           
           if not messages:
               break
           
           for message in messages:
               msg = service.users().messages().get(userId='me', id=message['id']).execute()
               headers = msg['payload']['headers']
               for header in headers:
                   if header['name'] == 'To':
                       email_addresses.append(header['value'])  # Append to list

           next_page_token = results.get('nextPageToken')
           if not next_page_token:
               break

       return email_addresses
   except Exception as e:
       print(f'An error occurred: {e}')
       return []

def write_emails_to_file(emails, file_path='emails.txt'):
   """Write email addresses to a text file."""
   try:
       with open(file_path, 'w') as f:
           for email in emails:
               f.write(f"{email}\n")
       print(f"Email addresses written to {file_path}")
   except Exception as e:
       print(f'An error occurred while writing to file: {e}')

def main():
   try:
       # Authenticate and build Gmail service
       gmail_service = authenticate('gmail')
       email_addresses = get_emails(gmail_service)

       if email_addresses:
           # Write the email addresses to a text file
           write_emails_to_file(email_addresses)

   except HttpError as error:
       print(f'An error occurred: {error}')

if __name__ == '__main__':
   main()




