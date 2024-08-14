# names and emails of all of them:

import os
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import socket
import re

# Function to authenticate with Gmail API
def authenticate_gmail_api():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    SERVICE_ACCOUNT_FILE = '/Users/arushityagi/Documents/oauth2_client_id.json'

    # Create the flow using the client secrets file
    flow = InstalledAppFlow.from_client_secrets_file(SERVICE_ACCOUNT_FILE, SCOPES)
    creds = flow.run_local_server(port=0)  # Opens a browser for user authentication

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service

# Function to clean and extract the name and email
def extract_name_and_email(body, email):
    # Remove HTML entities from the body
    body = body.replace('&amp;', '&')

    # Extract name part
    match = re.search(r'Hi\s+([^!]+)', body)
    name = match.group(1).strip() if match else 'Unknown'

    # Ensure the email is correctly formatted
    email_match = re.search(r'<([^>]+)>', email)
    email = email_match.group(1) if email_match else email

    return f"{name} <{email}>"

# Function to fetch emails from Gmail with a specific subject
def fetch_emails(service, subject, batch_size=50, delay_seconds=1):
    try:
        emails_and_names = []
        page_token = None
        max_retries = 5
        excluded_email = 'anushkafit.partner@gmail.com'

        while True:
            for retry in range(max_retries):
                try:
                    results = service.users().messages().list(
                        userId='me',
                        q=f'subject:"{subject}"',
                        pageToken=page_token,
                        maxResults=batch_size
                    ).execute()
                    break
                except (HttpError, socket.timeout) as error:
                    wait_time = (2 ** retry) + (retry % 2)  # Exponential backoff
                    print(f"Error occurred: {error}, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
            else:
                print("Max retries reached. Exiting.")
                break

            messages = results.get('messages', [])

            if not messages:
                print('No more messages found.')
                break

            for message in messages:
                for retry in range(max_retries):
                    try:
                        msg = service.users().messages().get(userId='me', id=message['id']).execute()
                        break
                    except (HttpError, socket.timeout) as error:
                        wait_time = (2 ** retry) + (retry % 2)
                        print(f"Error occurred: {error}, retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                else:
                    print("Max retries reached for a message. Skipping.")
                    continue

                body = msg['snippet']  # Using snippet for simplicity
                headers = msg['payload']['headers']

                email = None
                for header in headers:
                    if header['name'] == 'To':
                        email = header['value']
                        break

                # Skip emails to the excluded address
                if excluded_email in email:
                    continue

                # Extract the name and email
                if 'Hi ' in body:
                    email_and_name = extract_name_and_email(body, email)
                    emails_and_names.append(email_and_name)

            # Check if there is another page of results
            page_token = results.get('nextPageToken')
            if not page_token:
                break

            # Delay to avoid rate limiting
            time.sleep(delay_seconds)

        return emails_and_names

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

# Function to write emails to a text file
def write_emails_to_file(emails_and_names, filename):
    with open(filename, 'w') as file:
        for entry in emails_and_names:
            file.write(f"{entry}\n")

def main():
    # Authenticate and get the Gmail service
    gmail_service = authenticate_gmail_api()

    # Fetch emails with the specific subject
    subject = "Your 5K Training Plan!"
    emails_and_names = fetch_emails(gmail_service, subject, batch_size=50, delay_seconds=1)

    print(f"Fetched Emails and Names: {emails_and_names}")

    # Write emails and names to a text file
    text_file = 'emails_and_names.txt'
    write_emails_to_file(emails_and_names, text_file)
    print(f"Emails and Names have been written to {text_file}.")

if __name__ == '__main__':
    main()





# just the first 20 test:

##import os
##import time
##from googleapiclient.discovery import build
##from googleapiclient.errors import HttpError
##from google_auth_oauthlib.flow import InstalledAppFlow
##import socket
##import re
##
### Increase the default socket timeout
##socket.setdefaulttimeout(600)  # Set to 10 minutes
##
### Function to authenticate with Gmail API
##def authenticate_gmail_api():
##    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
##    SERVICE_ACCOUNT_FILE = '/Users/arushityagi/Documents/oauth2_client_id.json'
##
##    # Create the flow using the client secrets file
##    flow = InstalledAppFlow.from_client_secrets_file(SERVICE_ACCOUNT_FILE, SCOPES)
##    creds = flow.run_local_server(port=0)  # Opens a browser for user authentication
##
##    # Build the Gmail service
##    service = build('gmail', 'v1', credentials=creds)
##    return service
##
### Function to fetch the first 10 emails and extract first names and email addresses
##def fetch_emails_and_names(service, subject, max_emails=10):
##    try:
##        emails_and_names = []
##        page_token = None
##        email_count = 0
##
##        while email_count < max_emails:
##            results = service.users().messages().list(
##                userId='me',
##                q=f'subject:"{subject}"',
##                pageToken=page_token,
##                maxResults=max_emails
##            ).execute()
##
##            messages = results.get('messages', [])
##
##            if not messages:
##                print('No messages found.')
##                break
##
##            for message in messages:
##                if email_count >= max_emails:
##                    break
##
##                msg = service.users().messages().get(userId='me', id=message['id']).execute()
##                headers = msg['payload']['headers']
##                body_data = msg['snippet']
##
##                email_address = None
##                first_name = None
##
##                for header in headers:
##                    if header['name'] == 'To':
##                        email_address = header['value']
##
##                # Extract the first name from the email body
##                match = re.search(r'Hi (\w+)!', body_data)
##                if match:
##                    first_name = match.group(1)
##
##                if email_address and first_name:
##                    emails_and_names.append((first_name, email_address))
##                    email_count += 1
##
##            # Check if there is another page of results
##            page_token = results.get('nextPageToken')
##            if not page_token:
##                break
##
##        return emails_and_names
##
##    except HttpError as error:
##        print(f'An error occurred: {error}')
##        return []
##
### Function to write emails and names to a text file
##def write_emails_and_names_to_file(emails_and_names, filename):
##    with open(filename, 'w') as file:
##        for first_name, email in emails_and_names:
##            file.write(f"{first_name} <{email}>\n")
##
##def main():
##    # Authenticate and get the Gmail service
##    gmail_service = authenticate_gmail_api()
##
##    # Fetch emails with the specific subject and extract first names and emails
##    subject = "Your 5K Training Plan!"
##    emails_and_names = fetch_emails_and_names(gmail_service, subject, max_emails=20)
##
##    print(f"Fetched Emails and Names: {emails_and_names}")
##
##    # Write emails and names to a text file
##    text_file = 'emails_and_names.txt'
##    write_emails_and_names_to_file(emails_and_names, text_file)
##    print(f"Emails and names have been written to {text_file}.")
##
##if __name__ == '__main__':
##    main()



# reading with batches:
##
##import os
##import time
##from googleapiclient.discovery import build
##from googleapiclient.errors import HttpError
##from google_auth_oauthlib.flow import InstalledAppFlow
##
### Function to authenticate with Gmail API
##def authenticate_gmail_api():
##    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
##    SERVICE_ACCOUNT_FILE = '/Users/arushityagi/Documents/oauth2_client_id.json'
##
##    # Create the flow using the client secrets file
##    flow = InstalledAppFlow.from_client_secrets_file(SERVICE_ACCOUNT_FILE, SCOPES)
##    creds = flow.run_local_server(port=0)  # Opens a browser for user authentication
##
##    # Build the Gmail service
##    service = build('gmail', 'v1', credentials=creds)
##    return service
##
### Function to fetch emails from Gmail with a specific subject
##def fetch_emails(service, subject, batch_size=100):
##    try:
##        emails = []
##        page_token = None
##
##        while True:
##            results = service.users().messages().list(
##                userId='me',
##                q=f'subject:"{subject}"',
##                pageToken=page_token,
##                maxResults=batch_size
##            ).execute()
##
##            messages = results.get('messages', [])
##
##            if not messages:
##                print('No messages found.')
##                break
##
##            for message in messages:
##                msg = service.users().messages().get(userId='me', id=message['id']).execute()
##                headers = msg['payload']['headers']
##                for header in headers:
##                    if header['name'] == 'To':
##                        emails.append(header['value'])
##
##            # Check if there is another page of results
##            page_token = results.get('nextPageToken')
##            if not page_token:
##                break
##
##        return list(set(emails))  # Remove duplicates
##
##    except HttpError as error:
##        print(f'An error occurred: {error}')
##        return []
##
### Function to write emails to a text file
##def write_emails_to_file(emails, filename):
##    with open(filename, 'w') as file:
##        for email in emails:
##            file.write(f"{email}\n")
##
##def main():
##    # Authenticate and get the Gmail service
##    gmail_service = authenticate_gmail_api()
##
##    # Fetch emails with the specific subject
##    subject = "Your 5K Training Plan!"
##    emails = fetch_emails(gmail_service, subject)
##
##    print(f"Fetched Emails: {emails}")
##
##    # Write emails to a text file
##    text_file = 'emails.txt'
##    write_emails_to_file(emails, text_file)
##    print(f"Emails have been written to {text_file}.")
##
##if __name__ == '__main__':
##    main()



# reading without batches

##import os
##from googleapiclient.discovery import build
##from googleapiclient.errors import HttpError
##from google_auth_oauthlib.flow import InstalledAppFlow
##
### Function to authenticate with Gmail API
##def authenticate_gmail_api():
##    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
##    SERVICE_ACCOUNT_FILE = '/Users/arushityagi/Documents/oauth2_client_id.json'
##
##    # Create the flow using the client secrets file
##    flow = InstalledAppFlow.from_client_secrets_file(SERVICE_ACCOUNT_FILE, SCOPES)
##    creds = flow.run_local_server(port=0)  # Opens a browser for user authentication
##
##    # Build the Gmail service
##    service = build('gmail', 'v1', credentials=creds)
##    return service
##
### Function to fetch emails from Gmail with a specific subject
##def fetch_emails(service, subject):
##    try:
##        emails = []
##        page_token = None
##
##        while True:
##            results = service.users().messages().list(
##                userId='me',
##                q=f'subject:"{subject}"',
##                pageToken=page_token
##            ).execute()
##            
##            messages = results.get('messages', [])
##
##            if not messages:
##                print('No messages found.')
##                break
##
##            for message in messages:
##                msg = service.users().messages().get(userId='me', id=message['id']).execute()
##                headers = msg['payload']['headers']
##                for header in headers:
##                    if header['name'] == 'To':
##                        emails.append(header['value'])
##
##            # Check if there is another page of results
##            page_token = results.get('nextPageToken')
##            if not page_token:
##                break
##
##        return list(set(emails))  # Remove duplicates
##
##    except HttpError as error:
##        print(f'An error occurred: {error}')
##        return []
##
### Function to write emails to a text file
##def write_emails_to_file(emails, filename):
##    with open(filename, 'w') as file:
##        for email in emails:
##            file.write(f"{email}\n")
##
##def main():
##    # Authenticate and get the Gmail service
##    gmail_service = authenticate_gmail_api()
##
##    # Fetch emails with the specific subject
##    subject = "Your 5K Training Plan!"
##    emails = fetch_emails(gmail_service, subject)
##
##    print(f"Number of Emails Fetched: {len(emails)}")
##
##    # Write emails to a text file
##    text_file = 'emails.txt'
##    write_emails_to_file(emails, text_file)
##    print(f"Emails have been written to {text_file}.")
##
##if __name__ == '__main__':
##    main()
