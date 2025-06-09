import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# Gmail API scope for read and label permissions
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# All rejection phrases
REJECTION_PHRASES = [
    "unfortunately",
    "we regret to inform you",
    "unfortunately, after careful consideration, we have determined",
    "unfortunately, we are unable to offer you a role at this time.",
    "after careful consideration, we regret to inform you that you have not been selected",
    "unfortunately, we cannot move forward with your candidacy.",
    "unfortunately, we will not be moving forward with your application",
    "unfortunately, you have not been selected",
    "unfortunately, we have decided to proceed with other candidates",
    "unfortunately, your qualifications do not match our current needs",
    "unfortunately, we will not be offering you the position",
    "unfortunately, we cannot offer you a position at this time",
    "unfortunately, we are unable to move forward with your candidacy",
    "we have decided to move forward with other candidates",
    "after careful consideration, we have decided not to move forward with your application.",
    "you have not been selected for this position.",
    "you were not chosen to move forward in the hiring process.",
    "we won’t be moving forward with your application.",
    "your background does not align with our current needs.",
    "your background does not meet our needs at this time",
    "another candidate has been selected for this role.",
    "another candidate has been chosen",
    "position has been filled.",
    "position has been filled with another applicant.",
    "this role has been closed.",
    "we have completed our hiring process.",
    "not selected",
    "your profile was not selected",
    "we are unable to proceed with your application.",
    "we have chosen a different candidate",
    "we have chosen to proceed with other applicants",
    "we are pursuing other candidates",
    "better aligned candidates",
    "we are not moving forward",
    "you will not be moving on to the next stage",
    "we will keep your resume on file for future opportunities",
    "we’ve decided to move forward with other candidates",
    "we are moving forward with other applicants",
    "moving forward with other candidates at this time",
    "we have chosen to proceed with other candidates",
    "we have selected other applicants for this role",
    "other candidates were a better fit for this position",
    "we’re proceeding with other individuals"
]

INTERVIEW_PHRASES = [
    # Body content phrases
    "i would love to set up a time to chat",
    "i would love to set up a time to chat with you",
    "i will contact you to schedule a telephone interview",
    "let me know when a good day/time for us is to talk",
    "do you have time to chat about the opportunity",
    "upon further review of your resume and qualifications, we would like to learn more about you and assess your potential fit for the role",
    "please select an open time in the next few days, if possible. i look forward to meeting with you soon",
    "i look forward to meeting you and reviewing your qualifications",
    "i’m impressed with your background and experience and would love to schedule",
    "invitation to meet",
    "invitation to interview",
    "interview invitation",
    "interview availability",
    "thank you for your interest…we’d like to invite you to a phone interview",
    "thank you for your interest…we’d like to invite you to a video interview",
    "thank you for your interest…we’d like to invite you to a first-round interview",
    "phone screen",
    "upon review of your resume, i would like to schedule a phone screen with you",
    "final interview",
    "interview request for",
    "interview request",
    "you’re invited to an interview",
    "we’d like to invite you to an interview",

    # Subject header phrases
    "subject: next steps",
    "let’s schedule a time to talk",
    "subject: interview invitation for",
    "subject: phone interview for",
    "subject: interview for",
    "subject: final round interview for",

    # Keywords to match in both subject and body
    "set up a time to chat",
    "schedule a telephone interview",
    "invited to an interview",
    "next steps",
]



def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_or_create_label(service, label_name):
    labels = service.users().labels().list(userId='me').execute()
    for label in labels['labels']:
        if label['name'].lower() == label_name.lower():
            return label['id']
    label_body = {'name': label_name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
    return service.users().labels().create(userId='me', body=label_body).execute()['id']

def get_message_subject_and_body(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = msg['payload'].get('headers', [])
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')

    # Extract text from payload
    parts = msg['payload'].get('parts', [])
    body = ""
    for part in parts:
        data = part['body'].get('data')
        if data:
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            if part['mimeType'] == 'text/plain':
                body += decoded
            elif part['mimeType'] == 'text/html':
                body += BeautifulSoup(decoded, 'html.parser').get_text()
    return subject, body

def is_rejection(subject, body):
    text = (subject + " " + body).lower()
    return any(phrase.lower() in text for phrase in REJECTION_PHRASES)

def label_rejection_emails(service):
    label_id = get_or_create_label(service, "Unfortunately Jobs")
    response = service.users().messages().list(userId='me', q='newer_than:30d').execute()
    messages = response.get('messages', [])

    for msg in messages:
        subject, body = get_message_subject_and_body(service, msg['id'])
        if is_rejection(subject, body):
            service.users().messages().modify(
                userId='me',
                id=msg['id'],
                body={'addLabelIds': [label_id]}
            ).execute()
            print(f"Labeled as 'Unfortunately Jobs': {subject[:60]}...")

if __name__ == '__main__':
    service = authenticate_gmail()
    label_rejection_emails(service)
