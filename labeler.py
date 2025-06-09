import os
import base64
import re
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from phrases import REJECTION_PHRASES, INTERVIEW_PHRASES


class GmailLabeler:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    def __init__(self):
        self.service = self._authenticate()
        self.rejection_patterns = [self._phrase_to_regex(p) for p in REJECTION_PHRASES]
        self.interview_patterns = [self._phrase_to_regex(p) for p in INTERVIEW_PHRASES]

    def _authenticate(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return build('gmail', 'v1', credentials=creds)

    def _phrase_to_regex(self, phrase):
        pattern = r'\b' + re.sub(r'\s+', r'\\s+', re.escape(phrase)) + r'\b'
        return re.compile(pattern, re.IGNORECASE)

    def _fetch_messages(self, query):
        all_messages = []
        next_page_token = None

        while True:
            response = self.service.users().messages().list( #type :ingore
                userId='me', q=query, pageToken=next_page_token
            ).execute()

            all_messages.extend(response.get('messages', []))
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return all_messages

    def _get_or_create_label(self, label_name):
        labels = self.service.users().labels().list(userId='me').execute()
        for label in labels['labels']:
            if label['name'].lower() == label_name.lower():
                return label['id']
        label_body = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        return self.service.users().labels().create(userId='me', body=label_body).execute()['id']

    def _get_subject_and_body(self, msg_id):
        msg = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        headers = msg['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')

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

    def _is_rejection(self, subject, body):
        text = (subject + " " + body).lower()
        return any(p.search(text) for p in self.rejection_patterns)

    def _is_interview(self, subject, body):
        text = (subject + " " + body).lower()
        return any(p.search(text) for p in self.interview_patterns)

    def label_rejections(self):
        label_id = self._get_or_create_label("Unfortunately Jobs")
        messages = self._fetch_messages('newer_than:30d')

        for msg in messages:
            subject, body = self._get_subject_and_body(msg['id'])
            if self._is_rejection(subject, body):
                self.service.users().messages().modify(
                    userId='me',
                    id=msg['id'],
                    body={'addLabelIds': [label_id]}
                ).execute()
                print(f"Labeled as 'Unfortunately Jobs': {subject[:60]}...")

    def label_interviews(self):
        label_id = self._get_or_create_label("Interview Scheduled")
        messages = self._fetch_messages('newer_than:30d')

        for msg in messages:
            subject, body = self._get_subject_and_body(msg['id'])
            if self._is_interview(subject, body):
                self.service.users().messages().modify(
                    userId='me',
                    id=msg['id'],
                    body={'addLabelIds': [label_id]}
                ).execute()
                print(f"Labeled as 'Interview Scheduled': {subject[:60]}...")
