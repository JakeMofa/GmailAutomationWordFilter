# Gmail Rejection & Interview Labeler

## Why This Project?
Are you tired of digging through countless rejection emails or trying to manually set up Gmail filters that never quite work?

I built this script to automatically label job rejections and interview invitations — making it easier to focus only on the emails that matter. Instead of relying on Gmail’s basic filters, this tool uses regex, keyword matching, and the Gmail API to scan and label your inbox with precision.

Given how tough the job market is, I thought I’d contribute something small but useful to the community. This is my first release, based on initial testing — but I plan to expand this open-source project with more features, better modularization, and additional automation tools over time.

Stay tuned — and feel free to contribute, fork, or follow along.


## SAMPLE OF how it works, would Add UI in future releases
https://github.com/user-attachments/assets/b6b2ba8f-2cf3-4c82-bb1a-8d926dc1cfbd

# Gmail Rejection & Interview Labeler

This Python script connects to your Gmail account, scans emails from the last 30 days of which you can change, and automatically labels messages that contain:

- Rejection keywords → **“Unfortunately Jobs”**
- Interview invites → **“Interview Scheduled”**

## Features

- Gmail API integration via OAuth2
-  Regex + keyword matching
-  Pagination across all emails (not just the first 100)
-  Label creation or reuse
-  Works locally with VSCode or terminal

## Setup

1. Clone the repo:



```bash
git clone https://github.com/yourusername/gmail-labeler.git
cd gmail-labeler 
```

2. Install Dependencies
``` bash
pip install -r requirements.txt
or
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib beautifulsoup4
```

3. Set up Gmail API credentials:
Go to Google Cloud Console

Enable Gmail API

Create OAuth 2.0 Client ID (type: Desktop App)

Download credentials.json and place it in the project directory, you may need to create a file called credentials.json and then copy and paste your own token inside.

4. Run the script:
python main.py

## Notes
Make sure to add your own Gmail as a Test User in the Google Cloud OAuth Consent Screen

You can change the search window by editing 'newer_than:30d' in the code

credentials.json and token.json should be ignored via .gitignore




## 🙌 Credits & Attribution

This project was created by **Jake Mofa**.

If you find it helpful, please consider tagging me or linking back:
- GitHub: [@JakeMofa](https://github.com/JakeMofa)
- LinkedIn: [Jake Mofa](https://www.linkedin.com/in/jakemofa)
- 





I appreciate the acknowledgment and connections!
