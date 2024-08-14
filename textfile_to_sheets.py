import re
import gspread
from google.oauth2.service_account import Credentials

# Function to extract names and emails from the text file
def extract_names_and_emails_from_text_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Regex to match "Name <email@example.com>"
    name_email_regex = r'([^<]+) <([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>'
    matches = re.findall(name_email_regex, content)

    # Create a dictionary to filter duplicate emails
    unique_emails = {}
    for name, email in matches:
        if email not in unique_emails:
            unique_emails[email] = name.strip()
    
    # Convert the dictionary to a list of tuples (name, email)
    return list(unique_emails.items())

# Function to authenticate with Google Sheets
def authenticate_google_sheets(credentials_file, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 
             'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]

    creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

# Function to write names and emails to the Google Sheet in batch
def write_names_and_emails_to_sheet(sheet, data):
    # Prepare the data for batch update
    cell_data = []
    for i, (name, email) in enumerate(data, start=1):
        cell_data.append({'range': f'A{i}', 'values': [[name]]})  # Name in the first column
        cell_data.append({'range': f'B{i}', 'values': [[email]]})  # Email in the second column

    # Perform the batch update
    sheet.batch_update(cell_data)

def main(file_path, credentials_file, sheet_name):
    # Extract names and emails from the text file
    data = extract_names_and_emails_from_text_file(file_path)

    # Authenticate and get the sheet
    sheet = authenticate_google_sheets(credentials_file, sheet_name)

    # Write names and emails to the Google Sheet
    write_names_and_emails_to_sheet(sheet, data)

# Example usage
if __name__ == "__main__":
    file_path = "emails_and_names.txt"  # Replace with the path to your text file
    credentials_file = 'text_to_sheets.json'  # Replace with the path to your credentials file
    sheet_name = '5k Training Emails'  # Replace with your Google Sheet name

    main(file_path, credentials_file, sheet_name)
