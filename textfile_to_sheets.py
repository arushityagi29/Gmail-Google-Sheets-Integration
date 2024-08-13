import re
import gspread
from google.oauth2.service_account import Credentials

def extract_emails_from_text_file(file_path):
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Regex to match email patterns
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_regex, content)
    
    # Remove duplicates by converting the list to a set, then back to a list
    return list(set(emails))

def authenticate_google_sheets(credentials_file, sheet_name):
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    # Create credentials using the service account file
    creds = Credentials.from_service_account_file(credentials_file, scopes=scope)

    # Authorize the client
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open(sheet_name).sheet1
    return sheet

def write_emails_to_sheet(sheet, emails):
    # Prepare data to write
    cell_list = sheet.range(1, 1, len(emails), 1)
    for i, cell in enumerate(cell_list):
        cell.value = emails[i]
    sheet.update_cells(cell_list)


def main(file_path, credentials_file, sheet_name):
    # Extract emails from the text file
    emails = extract_emails_from_text_file(file_path)

    # Authenticate and get the sheet
    sheet = authenticate_google_sheets(credentials_file, sheet_name)

    # Write emails to the Google Sheet
    write_emails_to_sheet(sheet, emails)

# Example usage
if __name__ == "__main__":
    file_path = "emails.txt"  # Replace with the path to your text file
    credentials_file = 'text_to_sheets.json'  # Replace with the path to your credentials file
    sheet_name = 'Emails'  # Replace with your Google Sheet name

    main(file_path, credentials_file, sheet_name)
