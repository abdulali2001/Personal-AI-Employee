#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new emails and creates action files.

This watcher monitors Gmail for unread/important emails and creates
markdown action files in the Needs_Action folder for Qwen Code to process.

Setup:
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials.json to project directory
6. Run this script - it will open browser for authentication
7. Grant permissions and complete OAuth flow

Usage:
    python gmail_watcher.py /path/to/vault

Example:
    python gmail_watcher.py "D:/Hackathon 0/Personal-AI-Employee/AI_Employee_Vault"
"""

import sys
import os
import pickle
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from email import message_from_bytes
from email.header import decode_header

# Import base class
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher, load_processed_ids, save_processed_ids

# Gmail API libraries
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError as e:
    GMAIL_AVAILABLE = False
    print(f"Warning: Gmail libraries not installed: {e}")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']

# Priority keywords
HIGH_PRIORITY_KEYWORDS = [
    'urgent', 'asap', 'invoice', 'payment', 'deadline',
    'contract', 'agreement', 'meeting', 'call', 'interview',
    'complaint', 'issue', 'problem', 'help', 'support',
    'emergency', 'important', 'action required', 'respond'
]

SPAM_KEYWORDS = [
    'lottery', 'winner', 'congratulations', 'nigerian prince',
    'inheritance', 'work from home', 'make money fast', 'crypto giveaway'
]


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new emails and creates action files.

    When an email is detected, it:
    1. Fetches email details (sender, subject, body, attachments)
    2. Determines priority based on keywords
    3. Creates a markdown action file in Needs_Action
    4. Marks email as processed
    """

    def __init__(self, vault_path: str, credentials_path: str,
                 check_interval: int = 120):
        """
        Initialize the Gmail watcher.

        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail OAuth credentials.json
            check_interval: How often to check for new emails (seconds)
        """
        super().__init__(vault_path, check_interval)

        if not GMAIL_AVAILABLE:
            raise RuntimeError("Gmail libraries not installed")

        self.credentials_path = Path(credentials_path)
        self.token_path = self.vault_path / '.gmail_token.pickle'
        self.service = None

        # Load processed email IDs
        self.processed_ids = load_processed_ids(str(self.vault_path), 'gmail')

        # Initialize Gmail service
        self._authenticate()

        self.logger.info(f'Credentials path: {self.credentials_path}')

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        creds = None

        # Load existing token
        if self.token_path.exists():
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
                self.logger.debug('Loaded existing token')
            except Exception as e:
                self.logger.error(f'Error loading token: {e}')

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info('Refreshed expired token')
                except Exception as e:
                    self.logger.error(f'Token refresh failed: {e}')
                    creds = None

            if not creds:
                self.logger.info('Starting OAuth flow...')
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=8080, open_browser=True)

                    # Save token
                    with open(self.token_path, 'wb') as token:
                        pickle.dump(creds, token)
                    self.logger.info('OAuth completed, token saved')

                except Exception as e:
                    self.logger.error(f'OAuth flow failed: {e}')
                    raise

        # Build service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Gmail service initialized')
        except Exception as e:
            self.logger.error(f'Failed to build Gmail service: {e}')
            raise

    def _decode_header(self, header_value: str) -> str:
        """Decode MIME header value"""
        if not header_value:
            return ''

        decoded_parts = decode_header(header_value)
        decoded_str = ''

        for content, encoding in decoded_parts:
            if isinstance(content, bytes):
                try:
                    decoded_str += content.decode(encoding or 'utf-8', errors='replace')
                except:
                    decoded_str += content.decode('latin-1', errors='replace')
            else:
                decoded_str += content

        return decoded_str

    def _extract_email_body(self, payload: dict) -> str:
        """Extract plain text body from email payload"""
        body = ''

        # Try multipart
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        import base64
                        data = base64.urlsafe_b64decode(part['body']['data'])
                        body = data.decode('utf-8', errors='replace')
                        break
                elif part['mimeType'] == 'multipart/alternative':
                    body = self._extract_email_body(part)
                    if body:
                        break

        # Try single part
        elif payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
            import base64
            data = base64.urlsafe_b64decode(payload['body']['data'])
            body = data.decode('utf-8', errors='replace')

        # Fallback to HTML (stripped)
        if not body and payload['mimeType'] == 'text/html':
            if 'data' in payload['body']:
                import base64
                import re
                data = base64.urlsafe_b64decode(payload['body']['data'])
                html = data.decode('utf-8', errors='replace')
                # Strip HTML tags
                body = re.sub(r'<[^>]+>', '', html)[:1000]

        return body[:5000]  # Limit body length

    def _has_attachments(self, payload: dict) -> bool:
        """Check if email has attachments"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] not in ['text/plain', 'text/html']:
                    if 'attachmentId' in part.get('body', {}):
                        return True
                elif 'parts' in part:
                    if self._has_attachments(part):
                        return True
        return False

    def _count_attachments(self, payload: dict) -> int:
        """Count number of attachments"""
        count = 0
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] not in ['text/plain', 'text/html']:
                    if 'attachmentId' in part.get('body', {}):
                        count += 1
                elif 'parts' in part:
                    count += self._count_attachments(part)
        return count

    def _determine_priority(self, subject: str, body: str, sender: str) -> str:
        """Determine email priority based on content"""
        text = (subject + ' ' + body).lower()
        sender_lower = sender.lower()

        # Check spam first
        for keyword in SPAM_KEYWORDS:
            if keyword in text:
                return 'spam'

        # Check high priority
        for keyword in HIGH_PRIORITY_KEYWORDS:
            if keyword in text:
                return 'high'

        return 'normal'

    def _extract_name(self, email_address: str) -> str:
        """Extract name from email address"""
        if '<' in email_address:
            return email_address.split('<')[0].strip().strip('"\'')
        return email_address.split('@')[0]

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail for new unread emails.

        Returns:
            List of email info dictionaries
        """
        if not self.service:
            self.logger.error('Gmail service not initialized')
            return []

        emails = []

        try:
            # Fetch unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=25
            ).execute()

            messages = results.get('messages', [])
            self.logger.debug(f'Found {len(messages)} unread messages')

            for msg in messages:
                msg_id = msg['id']

                # Skip already processed
                if msg_id in self.processed_ids:
                    continue

                # Fetch full message
                try:
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg_id,
                        format='full'
                    ).execute()

                    # Extract headers
                    headers = {h['name']: h['value']
                              for h in message['payload']['headers']}

                    from_email = headers.get('From', 'Unknown')
                    subject = self._decode_header(headers.get('Subject', 'No Subject'))
                    date = headers.get('Date', '')

                    # Extract body
                    body = self._extract_email_body(message['payload'])

                    # Check attachments
                    has_attachment = self._has_attachments(message['payload'])
                    attachment_count = self._count_attachments(message['payload'])

                    # Determine priority
                    priority = self._determine_priority(
                        subject, body, from_email
                    )

                    # Skip spam
                    if priority == 'spam':
                        self.logger.info(f'Skipping spam: {subject}')
                        self.processed_ids.add(msg_id)
                        continue

                    emails.append({
                        'gmail_id': msg_id,
                        'from': from_email,
                        'from_name': self._extract_name(from_email),
                        'to': headers.get('To', ''),
                        'subject': subject,
                        'date': date,
                        'body': body,
                        'priority': priority,
                        'has_attachment': has_attachment,
                        'attachment_count': attachment_count,
                        'snippet': message.get('snippet', '')
                    })

                except HttpError as e:
                    self.logger.error(f'Error fetching message {msg_id}: {e}')
                    continue

        except HttpError as e:
            self.logger.error(f'Error listing messages: {e}')
            if e.resp.status == 401:
                self.logger.info('Token expired, re-authenticating...')
                try:
                    self._authenticate()
                except:
                    pass

        return emails

    def create_action_file(self, email_data: Dict[str, Any]) -> Path:
        """
        Create a markdown action file for a Gmail message.

        Args:
            email_data: Email info dictionary

        Returns:
            Path to the created action file
        """
        timestamp = datetime.now().isoformat()
        safe_subject = email_data['subject'].replace(' ', '_')[:30]
        safe_subject = ''.join(c for c in safe_subject if c.isalnum() or c in '_-')

        filename = self.generate_filename(
            'EMAIL',
            f"{safe_subject}_{email_data['from_name'].replace(' ', '_')[:15]}"
        )

        # Generate suggested actions based on priority
        suggested_actions = ['- [ ] Review email content']
        if email_data['priority'] == 'high':
            suggested_actions.extend([
                '- [ ] Respond within 24 hours',
                '- [ ] Flag for follow-up'
            ])
        if email_data['has_attachment']:
            suggested_actions.append('- [ ] Review attachments')

        content = f'''---
type: gmail_email
gmail_id: {email_data['gmail_id']}
from: {email_data['from']}
from_name: {email_data['from_name']}
subject: {email_data['subject']}
received: {timestamp}
priority: {email_data['priority']}
has_attachment: {email_data['has_attachment']}
attachment_count: {email_data['attachment_count']}
status: pending
---

# Gmail Email for Processing

## Email Metadata

| Field | Value |
|-------|-------|
| **From** | {email_data['from_name']} <{email_data['from']}> |
| **To** | {email_data['to']} |
| **Subject** | {email_data['subject']} |
| **Received** | {email_data['date']} |
| **Priority** | {email_data['priority'].upper()} |
| **Attachments** | {email_data['attachment_count']} file(s) |

## Email Content

```
{email_data['body'][:3000] if email_data['body'] else '[No text content - may be HTML only]'}
```

## Suggested Actions

{chr(10).join(suggested_actions)}
- [ ] Move to /Done when complete

## AI Analysis

<!-- AI Employee: Add your analysis here -->

**Sentiment**: [Analyze tone]
**Intent**: [What does sender want?]
**Urgency**: [Response timeframe]
**Category**: [Business/Personal/Other]

---
*Created by Gmail Watcher*
*Gmail ID: {email_data['gmail_id']}*
'''

        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')

        # Mark as processed
        self.processed_ids.add(email_data['gmail_id'])
        save_processed_ids(str(self.vault_path), 'gmail', self.processed_ids)

        # Mark as read in Gmail (remove UNREAD label)
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_data['gmail_id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.debug(f'Marked email {email_data["gmail_id"]} as read')
        except Exception as e:
            self.logger.error(f'Failed to mark as read: {e}')

        self.logger.info(f'Created action file: {filename}')
        return filepath


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python gmail_watcher.py <vault_path> [credentials_path]")
        print("\nExample:")
        print('  python gmail_watcher.py "D:/Vault" "credentials.json"')
        print("\nFirst run will open browser for OAuth authentication.")
        sys.exit(1)

    vault_path = sys.argv[1]
    credentials_path = sys.argv[2] if len(sys.argv) > 2 else 'credentials.json'

    # Check credentials file
    if not Path(credentials_path).exists():
        print(f"\nError: Credentials file not found: {credentials_path}")
        print("\nTo get Gmail credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        print("6. Place in project directory")
        sys.exit(1)

    print(f"📧 AI Employee Gmail Watcher")
    print(f"============================")
    print(f"Vault: {vault_path}")
    print(f"Credentials: {credentials_path}")
    print(f"\nMonitoring Gmail for new emails...")
    print(f"Press Ctrl+C to stop\n")

    try:
        watcher = GmailWatcher(vault_path, credentials_path)
        watcher.run()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
