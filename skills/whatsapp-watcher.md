---
name: whatsapp-watcher
description: |
  Monitor WhatsApp messages via WhatsApp Web automation using Playwright.
  This skill detects important messages based on keywords and creates
  action files in the vault for processing.

  When invoked, this skill will:
  1. Launch WhatsApp Web in headless browser
  2. Scan chat list for unread messages
  3. Filter messages by priority keywords
  4. Create action files in /Needs_Action
  5. Mark messages as read (optional)

  Use for: Lead capture, urgent message detection, client communication

  WARNING: Respect WhatsApp Terms of Service. Use only for personal/business
  accounts you own. Consider official WhatsApp Business API for production.
---

# WhatsApp Watcher - Agent Skill

## Overview

This skill enables Qwen Code to monitor WhatsApp Web for incoming messages
and convert them into actionable tasks. It uses Playwright for browser
automation to interact with WhatsApp Web.

## Prerequisites

- WhatsApp Web account (personal or business)
- Python with Playwright installed
- Browser installed (Chromium recommended)
- Company_Handbook.md with message priority rules

## Setup

### Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Initial WhatsApp Web Login

```bash
# First run requires manual QR code scan
python watchers/whatsapp_watcher.py "/path/to/vault" --initial-login
```

This will:
1. Open WhatsApp Web in visible browser
2. Display QR code
3. Scan with your phone
4. Save session to persistent storage
5. Close browser

### Session Storage

```bash
# Session stored in:
~/.whatsapp_session/

# Contains:
- Local Storage data
- Cookies
- Authentication tokens
```

## Usage

### Run as Watcher Script

```bash
python watchers/whatsapp_watcher.py "/path/to/vault"
```

### Run via Qwen Code

```bash
qwen --cwd "/path/to/vault" --prompt "Check WhatsApp for urgent messages"
```

### With Custom Keywords

```bash
python watchers/whatsapp_watcher.py "/path/to/vault" --keywords "urgent,invoice,payment,help"
```

## Message Filtering Rules

### Priority Keywords

```python
PRIORITY_KEYWORDS = {
    'high': [
        'urgent', 'asap', 'emergency', 'help',
        'invoice', 'payment', 'money', 'bank',
        'deadline', 'today', 'now', 'immediately',
        'problem', 'issue', 'broken', 'error',
        'call me', 'call back', 'meeting'
    ],
    'normal': [
        'hello', 'hi', 'question', 'info',
        'update', 'status', 'progress',
        'tomorrow', 'later', 'when', 'how'
    ],
    'low': [
        'thanks', 'ok', 'bye', 'good',
        'lol', 'haha', 'emoji'
    ]
}
```

### VIP Contacts

```python
VIP_CONTACTS = [
    'Spouse',
    'Business Partner',
    'Key Client',
    'Family Emergency'
    # Add to /Vault/Contacts.md
]
```

Messages from VIP contacts always get high priority.

## Message Action File Schema

```markdown
---
type: whatsapp_message
chat_id: 1234567890@c.us
chat_name: John Doe
from: +1234567890
message_id: ABC123XYZ
received: 2026-03-29T10:30:00Z
priority: high | normal | low
is_group: false
keyword_match: urgent, invoice
status: pending
---

# WhatsApp Message for Processing

## Message Metadata

| Field | Value |
|-------|-------|
| **From** | John Doe (+1234567890) |
| **Chat** | Individual |
| **Received** | 2026-03-29 10:30 AM |
| **Priority** | High |
| **Keywords** | urgent, invoice |

## Message Content

```
Hi! Hope you're doing well.

Just wanted to follow up on the invoice I sent last week.
It's quite urgent as I need to process payment by Friday.

Can you please check and let me know?

Thanks!
```

## Message Type

- [x] Text
- [ ] Image
- [ ] Document
- [ ] Voice Note
- [ ] Video
- [ ] Location

## Suggested Actions

- [ ] Review message content
- [ ] Check invoice status
- [ ] Reply via WhatsApp
- [ ] Forward to accounts
- [ ] Mark as done

## AI Analysis

**Intent**: Payment follow-up
**Urgency**: High (deadline mentioned)
**Sentiment**: Polite, professional
**Required Response**: Yes, within 24 hours
**Suggested Channel**: WhatsApp (same as incoming)

## Reply Draft

```
Hi John! Thanks for following up. I'll check on the invoice
status right away and get back to you within the hour.
```

---
*Created by WhatsApp Watcher*
*Chat ID: 1234567890@c.us*
```

## Workflow

### Step 1: Launch WhatsApp Web

```python
from playwright.sync_api import sync_playwright

def launch_whatsapp(session_path):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=session_path,
        headless=True,
        args=['--disable-gpu', '--no-sandbox']
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto('https://web.whatsapp.com')
    return browser, page
```

### Step 2: Wait for Authentication

```python
def wait_for_login(page, timeout=60):
    """Wait for WhatsApp to be authenticated"""
    try:
        # Wait for chat list to appear
        page.wait_for_selector('[data-testid="chat-list"]', timeout=timeout*1000)
        return True
    except:
        print("Not logged in. Please scan QR code.")
        # Wait for QR code to be scanned
        page.wait_for_selector('[data-testid="chat-list"]', timeout=300*1000)
        return True
```

### Step 3: Find Unread Chats

```python
def get_unread_chats(page):
    """Find all chats with unread messages"""
    unread_chats = []
    
    # Find unread chat indicators
    unread_elements = page.query_selector_all(
        '[aria-label*="unread"], [data-testid="unread-message-count"]'
    )
    
    for element in unread_elements:
        try:
            chat_info = element.get_attribute('aria-label')
            if chat_info:
                unread_chats.append({
                    'element': element,
                    'label': chat_info
                })
        except:
            continue
    
    return unread_chats
```

### Step 4: Extract Message Content

```python
def get_message_content(page, chat_element):
    """Extract message content from chat"""
    # Click on chat to open it
    chat_element.click()
    page.wait_for_timeout(1000)
    
    # Get chat name
    chat_name = page.query_selector('[data-testid="conversation-info-header"]')
    chat_name = chat_name.inner_text() if chat_name else 'Unknown'
    
    # Get recent messages
    messages = page.query_selector_all('[data-testid="message-in"]')
    recent_messages = []
    
    for msg in messages[-5:]:  # Last 5 messages
        try:
            content = msg.query_selector('[data-testid="message-text"]')
            if content:
                recent_messages.append(content.inner_text())
        except:
            continue
    
    return {
        'chat_name': chat_name,
        'messages': recent_messages
    }
```

### Step 5: Determine Priority

```python
def determine_priority(message_data, vip_contacts):
    """Determine message priority based on content and sender"""
    text = ' '.join(message_data['messages']).lower()
    sender = message_data['chat_name'].lower()
    
    # Check VIP contacts
    for vip in vip_contacts:
        if vip.lower() in sender:
            return 'high'
    
    # Check priority keywords
    for keyword in PRIORITY_KEYWORDS['high']:
        if keyword in text:
            return 'high'
    
    for keyword in PRIORITY_KEYWORDS['normal']:
        if keyword in text:
            return 'normal'
    
    return 'low'
```

### Step 6: Create Action File

```python
def create_action_file(message_data, vault_path):
    """Create markdown action file for WhatsApp message"""
    timestamp = datetime.now().isoformat()
    safe_name = message_data['chat_name'].replace(' ', '_')[:20]
    filename = f"WHATSAPP_{safe_name}_{timestamp[:10]}.md"
    
    content = f"""---
type: whatsapp_message
chat_id: {message_data.get('chat_id', 'unknown')}
chat_name: {message_data['chat_name']}
from: {message_data.get('phone', 'Unknown')}
received: {timestamp}
priority: {message_data['priority']}
keyword_match: {message_data.get('keywords', '')}
status: pending
---

# WhatsApp Message for Processing

## Message Metadata

| Field | Value |
|-------|-------|
| **From** | {message_data['chat_name']} |
| **Received** | {timestamp} |
| **Priority** | {message_data['priority']} |

## Message Content

```
{chr(10).join(message_data['messages'])}
```

## Suggested Actions

- [ ] Review message
- [ ] Determine required action
- [ ] Reply via WhatsApp
- [ ] Mark as done

## AI Analysis

<!-- AI to add analysis here -->

---
*Created by WhatsApp Watcher*
"""
    
    filepath = Path(vault_path) / 'Needs_Action' / filename
    filepath.write_text(content, encoding='utf-8')
    return filepath
```

### Step 7: Mark as Read (Optional)

```python
def mark_as_read(page, chat_element):
    """Mark chat as read"""
    try:
        chat_element.click()
        page.wait_for_timeout(500)
        # WhatsApp auto-marks as read when opened
        return True
    except Exception as e:
        print(f"Error marking as read: {e}")
        return False
```

## Reply via WhatsApp

### Send Reply Function

```python
def send_whatsapp_reply(page, chat_name, reply_text):
    """Send a reply to a WhatsApp chat"""
    # Find the chat
    search_box = page.query_selector('[data-testid="search"]')
    search_box.fill(chat_name)
    page.wait_for_timeout(500)
    
    # Click on chat
    chat_list = page.query_selector('[data-testid="chat-list"]')
    chat_item = chat_list.query_selector(f'text="{chat_name}"')
    chat_item.click()
    page.wait_for_timeout(500)
    
    # Type and send reply
    message_box = page.query_selector('[data-testid="compose-input"]')
    message_box.fill(reply_text)
    
    # Find and click send button
    send_button = page.query_selector('[data-testid="compose-btn-send"]')
    send_button.click()
    
    page.wait_for_timeout(1000)
    return True
```

### MCP Integration (Future)

For Silver/Gold tier, integrate with WhatsApp MCP server:

```python
# MCP call format
{
  "action": "whatsapp_send",
  "to": "+1234567890",
  "message": "Hi! Thanks for your message..."
}
```

## Error Handling

### Session Expired

```markdown
1. Detect QR code on screen
2. Create alert in /Needs_Action
3. Include instructions: "Please scan QR code to re-authenticate"
4. Pause monitoring until re-authenticated
```

### Message Extraction Failed

```markdown
1. Log error with chat info
2. Screenshot current state for debugging
3. Continue with next chat
4. Retry failed chat on next run
```

### Browser Crash

```markdown
1. Catch browser exception
2. Log error with details
3. Attempt browser restart
4. If still failing, create system alert
```

## Integration with Vault

### Contacts Sync

```python
def update_whatsapp_contacts(message_data, contacts_file):
    """Sync WhatsApp contacts with vault"""
    contacts = load_contacts(contacts_file)
    
    chat_name = message_data['chat_name']
    if chat_name not in contacts:
        contacts[chat_name] = {
            'phone': message_data.get('phone', 'Unknown'),
            'source': 'whatsapp',
            'first_contact': message_data['received']
        }
        save_contacts(contacts_file, contacts)
```

### Message History

Track conversation history in `/Vault/WhatsApp_History/`:

```markdown
---
contact: John Doe
phone: +1234567890
total_messages: 45
last_message: 2026-03-29T10:30:00Z
---

# WhatsApp History: John Doe

## Recent Conversations

### 2026-03-29
- 10:30 AM - John: "Hi! About that invoice..."
- 10:35 AM - Me: "Hi John! Let me check..."

### 2026-03-25
- 3:00 PM - John: "Can we schedule a call?"
- 3:15 PM - Me: "Sure, how about tomorrow?"
```

## Testing

### Test Connection

```bash
python -c "
from watchers.whatsapp_watcher import test_connection
test_connection('~/.whatsapp_session')
"
```

### Test Message Detection

1. Send yourself a WhatsApp message from another device
2. Include keyword "urgent"
3. Run WhatsApp Watcher
4. Verify action file created in `/Needs_Action`

## Security Considerations

- Session data stored locally only
- Never upload to cloud
- Use dedicated browser profile
- Log out when not in use
- Monitor for suspicious activity

## Rate Limiting

To avoid WhatsApp bans:

- Max 1 message/second when sending
- Max 100 messages/hour
- 5-second delay between chat accesses
- Respect WhatsApp ToS

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code always shows | Session expired, re-scan QR code |
| Messages not detected | Check selector updates, WhatsApp may have changed DOM |
| Browser crashes | Increase timeout, reduce headless restrictions |
| Rate limited | Wait 24 hours, reduce polling frequency |

---

*Agent Skill v1.0 - Silver Tier*
*Last Updated: 2026-03-29*

**Disclaimer**: This skill is for educational/personal use. For production,
consider official WhatsApp Business API: https://business.whatsapp.com/
