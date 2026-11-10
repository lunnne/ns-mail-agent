
from pathlib import Path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


def get_gmail_service():
    credentials = None
    token_path = BASE_DIR / "token.json"

    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_path), SCOPES
        )

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(BASE_DIR / "credentials.json"),
                SCOPES
            )
            credentials = flow.run_local_server(port=0)

        token_path.write_text(
            credentials.to_json(),
            encoding="utf-8"
        )

    return build("gmail", "v1", credentials=credentials)


def get_recent_emails(max_results=10):
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for message in messages:
        data = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        headers = {
            h["name"].lower(): h["value"]
            for h in data["payload"].get("headers", [])
        }

        def extract_body(part):
            if part.get("mimeType") == "text/plain":
                encoded = part.get("body", {}).get("data")
                if encoded:
                    return base64.urlsafe_b64decode(
                        encoded + "=" * (-len(encoded) % 4)
                    ).decode("utf-8", errors="replace")

            for child in part.get("parts", []):
                text = extract_body(child)
                if text:
                    return text

            return ""

        body = extract_body(data["payload"])

        emails.append({
            "id": message["id"],
            "thread_id": data["threadId"],
            "sender": headers.get("from", ""),
            "subject": headers.get("subject", "(No subject)"),
            "body": body or data.get("snippet", "")
        })

    return emails
