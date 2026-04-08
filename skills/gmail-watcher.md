---
name: gmail-watcher
description: |
  Monitor Gmail for new emails and create action files in the vault.
  This skill integrates with Gmail API to fetch unread emails, analyze
  their content, and create structured markdown files for processing.

  When invoked, this skill will:
  1. Connect to Gmail API using stored credentials
  2. Fetch unread/important emails
  3. Filter based on priority keywords
  4. Create action files in /Needs_Action
  5. Mark emails as processed

  Use for: Email triage, lead capture, client communication monitoring
---

# Gmail Watcher - Agent Skill

## Overview

This skill enables Qwen Code to monitor Gmail and convert incoming emails
into actionable tasks in the Obsidian vault. It implements intelligent
filtering to prioritize important messages.

## Prerequisites

- Gmail API credentials configured
- Python with `google-api-python-client` installed
- OAuth 2.0 authorization completed
- Company_Handbook.md with email priority rules

## Setup

### Gmail API Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to secure location
6. Run initial auth to generate token

### Environment Variables

```bash
# .env file (never commit)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost:8080
VAULT_PATH=/path/to/vault
```

### Python Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Usage

### Run as Watcher Script

```bash
python watchers/gmail_watcher.py "/path/to/vault"
```

### Run via Qwen Code

```bash
qwen --cwd "/path/to/vault" --prompt "Check Gmail for new important emails"
```

### Scheduled Execution

```bash
# Cron (Linux/Mac) - every 5 minutes
*/5 * * * * cd /path && python watchers/gmail_watcher.py "/path/to/vault"

# Task Scheduler (Windows) - configure in GUI
```

## Email Filtering Rules

### Priority Keywords (High Priority)

```python
HIGH_PRIORITY_KEYWORDS = [
    'urgent', 'asap', 'invoice', 'payment',
    'deadline', 'contract', 'agreement',
    'meeting', 'call', 'interview',
    'complaint', 'issue', 'problem',
    'help', 'support', 'emergency'
]
```

### Known Senders (Auto-Process)

```python
KNOWN_SENDERS = [
    'client@company.com',
    'partner@business.com',
    # Add to /Vault/Contacts.md
]
```

### Spam Filter (Ignore)

```python
SPAM_KEYWORDS = [
    'lottery', 'winner', 'congratulations',
    'nigerian prince', 'inheritance',
    'work from home', 'make money fast'
]
```

## Email Action File Schema

```markdown
---
type: gmail_email
gmail_id: 18d4f2a3b5c6e7f8
from: sender@example.com
from_name: John Doe
subject: Urgent: Invoice Payment Required
received: 2026-03-29T10:30:00Z
priority: high | normal | low
labels: inbox, important, unread
has_attachment: true | false
attachment_count: 2
status: pending
---

# Gmail Email for Processing

## Email Metadata

| Field | Value |
|-------|-------|
| **From** | John Doe <sender@example.com> |
| **To** | you@yourcompany.com |
| **Subject** | Urgent: Invoice Payment Required |
| **Received** | 2026-03-29 10:30 AM |
| **Priority** | High |
| **Labels** | Inbox, Important |

## Email Content

```
Hi,

I hope this email finds you well.

I'm writing to follow up on the outstanding invoice #1234 
for $1,500 that was due last week.

Could you please process the payment at your earliest 
convenience?

Best regards,
John Doe
```

## Attachments

- invoice_1234.pdf (245 KB)
- payment_terms.pdf (89 KB)

## Suggested Actions

- [ ] Review email content
- [ ] Check invoice status in accounting
- [ ] Reply to sender
- [ ] Forward to accounts payable
- [ ] Mark as done after processing

## AI Analysis

**Sentiment**: Neutral, professional follow-up
**Urgency**: High (payment overdue)
**Required Response**: Yes, within 24 hours
**Category**: Accounts Payable

---
*Created by Gmail Watcher*
*Gmail ID: 18d4f2a3b5c6e7f8*
```

## Workflow

### Step 1: Connect to Gmail API

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_gmail_service(credentials_path):
    creds = Credentials.from_authorized_user_file(credentials_path)
    service = build('gmail', 'v1', credentials=creds)
    return service
```

### Step 2: Fetch Unread Emails

```python
def fetch_unread_emails(service, query='is:unread'):
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=50
    ).execute()
    return results.get('messages', [])
```

### Step 3: Get Email Details

```python
def get_email_details(service, message_id):
    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()
    
    # Extract headers
    headers = {h['name']: h['value'] for h in message['payload']['headers']}
    
    # Extract body
    body = extract_body(message['payload'])
    
    # Extract attachments
    attachments = extract_attachments(message['payload'])
    
    return {
        'id': message_id,
        'from': headers.get('From', ''),
        'to': headers.get('To', ''),
        'subject': headers.get('Subject', ''),
        'date': headers.get('Date', ''),
        'body': body,
        'attachments': attachments,
        'labels': [l['name'] for l in message.get('labelIds', [])]
    }
```

### Step 4: Determine Priority

```python
def determine_priority(email_data):
    subject_lower = email_data['subject'].lower()
    body_lower = email_data['body'].lower()
    
    # Check high priority keywords
    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword in subject_lower or keyword in body_lower:
            return 'high'
    
    # Check if from known sender
    sender = email_data['from'].lower()
    for known in KNOWN_SENDERS:
        if known.lower() in sender:
            return 'normal'
    
    # Check spam
    for spam in SPAM_KEYWORDS:
        if spam in subject_lower or spam in body_lower:
            return 'spam'
    
    return 'normal'
```

### Step 5: Create Action File

```python
def create_action_file(email_data, vault_path):
    timestamp = datetime.now().isoformat()
    safe_subject = email_data['subject'].replace(' ', '_')[:30]
    filename = f"GMAIL_{safe_subject}_{email_data['id']}.md"
    
    content = f"""---
type: gmail_email
gmail_id: {email_data['id']}
from: {email_data['from']}
from_name: {extract_name(email_data['from'])}
subject: {email_data['subject']}
received: {timestamp}
priority: {email_data['priority']}
labels: {', '.join(email_data['labels'])}
has_attachment: {email_data['has_attachment']}
status: pending
---

# Gmail Email for Processing

## Email Metadata

| Field | Value |
|-------|-------|
| **From** | {email_data['from']} |
| **Subject** | {email_data['subject']} |
| **Received** | {email_data['date']} |
| **Priority** | {email_data['priority']} |

## Email Content

{email_data['body']}

## Suggested Actions

- [ ] Review email content
- [ ] Determine required action
- [ ] Reply or forward
- [ ] Mark as done

## AI Analysis

<!-- AI to add analysis here -->

---
*Created by Gmail Watcher*
"""
    
    filepath = Path(vault_path) / 'Needs_Action' / filename
    filepath.write_text(content, encoding='utf-8')
    return filepath
```

### Step 6: Mark as Processed

```python
def mark_as_processed(service, message_id):
    # Remove UNREAD label
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()
    
    # Optionally add custom label
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'addLabelIds': ['AI_PROCESSED']}
    ).execute()
```

## Integration with Vault

### Contacts Management

Sync Gmail contacts with `/Vault/Contacts.md`:

```python
def update_contacts(email_data, contacts_file):
    # Extract sender info
    sender_email = extract_email(email_data['from'])
    sender_name = extract_name(email_data['from'])
    
    # Add to contacts if new
    contacts = load_contacts(contacts_file)
    if sender_email not in contacts:
        contacts[sender_email] = {
            'name': sender_name,
            'first_contact': email_data['date'],
            'source': 'gmail'
        }
        save_contacts(contacts_file, contacts)
```

### Email Thread Tracking

Track email threads in `/Vault/Email_Threads/`:

```markdown
---
thread_id: 18d4f2a3b5c6e7f8
subject: Project Discussion
participants: john@example.com, jane@client.com
messages: 5
last_updated: 2026-03-29T10:30:00Z
status: active
---

# Email Thread: Project Discussion

## Messages

1. 2026-03-25 - John: Initial inquiry
2. 2026-03-26 - Me: Response with quote
3. 2026-03-27 - John: Questions about timeline
4. 2026-03-28 - Me: Detailed timeline
5. 2026-03-29 - John: Ready to proceed

## Next Action

- [ ] Send contract for signature
```

## Error Handling

### API Quota Exceeded

```markdown
1. Log error with timestamp
2. Wait 60 seconds before retry
3. If still failing, pause for 1 hour
4. Create notification in /Needs_Action if critical
```

### Authentication Failed

```markdown
1. Log error with details
2. Create alert in /Needs_Action
3. Include re-authentication instructions
4. Pause Gmail monitoring until resolved
```

### Email Processing Failed

```markdown
1. Log failed email ID to skip list
2. Continue processing other emails
3. Create error report for failed email
4. Retry failed emails on next run
```

## Monitoring & Logging

### Log Format

```json
{
  "timestamp": "2026-03-29T10:30:00Z",
  "action": "gmail_fetch",
  "emails_found": 5,
  "emails_processed": 4,
  "emails_skipped": 1,
  "action_files_created": 4,
  "errors": []
}
```

### Metrics to Track

- Emails processed per day
- Average response time
- Priority distribution
- Spam detection accuracy

## Testing

### Test Connection

```bash
python -c "
from watchers.gmail_watcher import test_connection
test_connection('path/to/credentials.json')
"
```

### Test Email Processing

1. Send test email to yourself
2. Run Gmail Watcher
3. Verify action file created in `/Needs_Action`
4. Check email marked as processed

## Security Considerations

- Store credentials in environment variables
- Use OAuth 2.0 with minimal scopes
- Never log email content in plain text
- Rotate credentials monthly
- Enable 2FA on Gmail account

## Rate Limiting

To avoid Gmail API limits:

- Max 100 requests/second (quota)
- Max 1 billion requests/day (quota)
- Implement exponential backoff
- Cache results for 60 seconds

---

*Agent Skill v1.0 - Silver Tier*
*Last Updated: 2026-03-29*
