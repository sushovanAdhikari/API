import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
  '''
  get data from gmail account after configuration in the google cloud.
  '''
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # documentation: https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.messages.html
    service = build("gmail", "v1", credentials=creds)
    # GET https://gmail.googleapis.com/gmail/v1/users/{userId}/messages
    results = service.users().messages().list(userId="me").execute()
    messages = results.get("messages", [])

    if not messages:
      print("No labels found.")
      return
    print("messages:")
    for message in messages:
      message = service.users().messages().get(userId="me", id = message['id'], format = 'full').execute()
      print(message['snippet'])

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()