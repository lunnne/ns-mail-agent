
from pathlib import Path
import base64

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent
TOKEN_PATH = BASE_DIR / "token.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

REAUTH_GUIDE = "터미널에서 `uv run python gmail_service.py`를 실행해 다시 인증하세요."


class GmailAuthError(Exception):
    """앱이 직접 해결할 수 없고, 사장님이 다시 인증해야 하는 상황"""


def authorize():
    # 브라우저 로그인은 이 함수에서만 실행한다 (터미널에서 1회)
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_PATH),
        SCOPES
    )
    credentials = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(
        credentials.to_json(),
        encoding="utf-8"
    )
    return credentials


def load_credentials():
    if not TOKEN_PATH.exists():
        raise GmailAuthError(f"Gmail 인증 정보가 없습니다. {REAUTH_GUIDE}")

    # scopes를 넘기지 않아야 token.json에 실제로 저장된 권한을 읽는다
    credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH))

    if not credentials.has_scopes(SCOPES):
        raise GmailAuthError(f"Gmail 권한이 바뀌었습니다. {REAUTH_GUIDE}")

    if not credentials.valid:
        if not credentials.refresh_token:
            raise GmailAuthError(f"Gmail 인증이 만료되었습니다. {REAUTH_GUIDE}")

        try:
            credentials.refresh(Request())
        except RefreshError as e:
            raise GmailAuthError(
                f"Gmail 인증을 갱신하지 못했습니다. {REAUTH_GUIDE}"
            ) from e

        TOKEN_PATH.write_text(
            credentials.to_json(),
            encoding="utf-8"
        )

    return credentials


def get_gmail_service():
    return build("gmail", "v1", credentials=load_credentials())


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
            # Gmail이 메일을 받은 시각 (Unix epoch 밀리초)
            "received_at": int(data["internalDate"]),
            "body": body or data.get("snippet", "")
        })

    return emails


if __name__ == "__main__":
    # 터미널에서 단독 실행할 때도 app.py와 같은 인증서 저장소를 쓴다
    import truststore
    truststore.inject_into_ssl()

    authorize()
    print("Gmail 인증 완료: token.json을 저장했습니다.")
