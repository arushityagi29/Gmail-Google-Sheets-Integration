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
