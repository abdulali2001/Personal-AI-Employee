---
name: email-mcp-sender
description: |
  Send emails via MCP server integration. This skill handles all email-related
  operations including drafting, sending, and managing email approvals.
  Supports Gmail API integration through MCP server.

  When invoked, this skill will:
  1. Validate email content and recipient
  2. Check Company_Handbook.md for email rules
  3. Determine if approval is required
  4. Send directly (if auto-approved) or create approval request
  5. Log the action and update Dashboard

  Use for: Sending invoices, replies, notifications, bulk emails (with approval)
---

# Email MCP Sender - Agent Skill

## Overview

This skill enables Qwen Code to send emails through an MCP server integration.
It implements the Human-in-the-Loop (HITL) pattern for sensitive email actions.

## Prerequisites

- MCP Email Server configured in Claude Code settings
- Gmail API credentials (or other SMTP provider)
- Company_Handbook.md with email rules

## Usage

### Direct Send (Auto-Approved Cases)

```bash
qwen --cwd "/path/to/vault" --prompt "Send email to known contact with invoice"
```

### Approval Required Send

```bash
qwen --cwd "/path/to/vault" --prompt "Draft email to new client for approval"
```

## Email Rules (from Company_Handbook.md)

### Auto-Approve (Can Send Directly)

- Replies to existing threads with known contacts
- Invoice emails to clients in approved list
- Internal notifications (to self/team)
- Scheduled recurring emails (already approved)

### Requires Approval

- First-time contact (new recipient)
- Bulk emails (>5 recipients)
- Emails with attachments over 5MB
- Emails containing financial commitments
- Marketing/sales outreach emails

## Email Action Schema

### Input Format

```markdown
---
type: email_send
to: client@example.com
cc: manager@example.com (optional)
bcc: records@company.com (optional)
subject: Invoice #123 - January 2026
priority: normal | high | urgent
attachment: /Invoices/2026-01_Client_A.pdf (optional)
requires_approval: true | false
---

# Email Content

Dear Client,

Body of the email goes here.

Best regards,
AI Employee
```

### MCP Call Format

```json
{
  "to": "client@example.com",
  "cc": "manager@example.com",
  "subject": "Invoice #123 - January 2026",
  "body": "Dear Client,\n\nBody of the email...\n\nBest regards,\nAI Employee",
  "attachments": ["/path/to/file.pdf"]
}
```

## Workflow

### Step 1: Analyze Email Request

```markdown
1. Read email draft from /Needs_Action or /In_Progress
2. Extract recipient, subject, body, attachments
3. Check if recipient is in known contacts list
4. Determine approval requirement based on rules
5. Check Company_Handbook.md for tone guidelines
```

### Step 2: Create Approval Request (if needed)

For emails requiring approval, create:

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #123 - January 2026
created: 2026-03-29T10:30:00Z
expires: 2026-03-30T10:30:00Z
status: pending
priority: normal
---

# Approval Required: Send Email

## Email Details

| Field | Value |
|-------|-------|
| **To** | client@example.com |
| **Subject** | Invoice #123 - January 2026 |
| **Attachments** | 1 file (245 KB) |
| **Priority** | Normal |

## Why Approval is Required

This email requires approval because:
- [ ] New recipient (first contact)
- [x] Contains financial document (invoice)
- [ ] Bulk send (>5 recipients)
- [ ] Other: _______________

## Email Preview

**Subject**: Invoice #123 - January 2026

**Body**:
```
Dear Client,

Please find attached your invoice for January 2026.

Amount Due: $1,500.00
Due Date: February 15, 2026

Best regards,
AI Employee
```

## To Approve

1. Review the email content above
2. Move this file to `/Approved` folder

## To Request Changes

1. Add comments to this file
2. Move back to `/Needs_Action`

## To Reject

1. Add reason for rejection below
2. Move to `/Rejected` folder

---
*Created by AI Employee - requires human decision before sending*
```

### Step 3: Send via MCP (When Approved)

When approval file is moved to `/Approved`:

```bash
# MCP server call
python mcp-client.py call -u http://localhost:8809 -t email_send \
  -p '{
    "to": "client@example.com",
    "subject": "Invoice #123 - January 2026",
    "body": "Dear Client,\n\nPlease find attached...",
    "attachments": ["/Vault/Invoices/2026-01_Client_A.pdf"]
  }'
```

### Step 4: Log and Complete

After successful send:

1. Log action to `/Logs/email_YYYY-MM-DD.json`
2. Add sent timestamp to approval file
3. Move all related files to `/Done`
4. Update `Dashboard.md`

```json
{
  "timestamp": "2026-03-29T10:45:00Z",
  "action_type": "email_send",
  "actor": "qwen_code",
  "target": "client@example.com",
  "subject": "Invoice #123 - January 2026",
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success",
  "message_id": "<msg123@gmail.com>"
}
```

## Email Templates

### Invoice Email

```markdown
Subject: Invoice #{invoice_number} - {month} {year}

Dear {client_name},

Please find attached invoice #{invoice_number} for {month} {year}.

**Invoice Details:**
- Amount: ${amount}
- Due Date: {due_date}
- Payment Terms: {terms}

You can pay via:
- Bank Transfer (details on invoice)
- Credit Card (link on invoice)
- PayPal (link on invoice)

If you have any questions, please don't hesitate to reach out.

Best regards,
AI Employee
On behalf of {your_name/company}
```

### Reply Email

```markdown
Subject: Re: {original_subject}

Dear {sender_name},

Thank you for your email regarding {topic}.

{response_body}

Please let me know if you need any clarification.

Best regards,
AI Employee
On behalf of {your_name/company}
```

### Follow-up Email

```markdown
Subject: Following up: {original_subject}

Dear {recipient_name},

I hope this email finds you well.

I'm following up on my previous email regarding {topic}.

{context_or_update}

Would you have time this week for a quick call?

Best regards,
AI Employee
On behalf of {your_name/company}
```

## Known Contacts Management

Maintain a contacts list in `/Vault/Contacts.md`:

```markdown
# Known Contacts

## Auto-Approve List (Can email without approval)

| Name | Email | Company | Last Contact |
|------|-------|---------|--------------|
| John Doe | john@example.com | Acme Corp | 2026-03-28 |
| Jane Smith | jane@client.com | Client Inc | 2026-03-27 |

## New Contacts (Require approval)

| Name | Email | Added | Reason |
|------|-------|-------|--------|
| New Lead | lead@prospect.com | 2026-03-29 | First contact |
```

## Error Handling

### Send Failed

```markdown
1. Log error with full details
2. Retry up to 3 times (exponential backoff)
3. After 3 failures, create error report in /Pending_Approval
4. Notify human of persistent failure
```

### Attachment Missing

```markdown
1. Check file path is correct
2. Verify file exists in vault
3. If missing, pause and request human input
4. Do not send email without required attachments
```

### MCP Server Unavailable

```markdown
1. Log intended action to /Pending_Action
2. Create notification in /Needs_Action
3. Retry when server is available
4. Do not lose the email draft
```

## Testing

### Test Email (Dry Run)

```markdown
---
type: test_email
to: your-email@gmail.com
subject: TEST - AI Employee Email System
requires_approval: false
dry_run: true
---

This is a test email to verify the email MCP integration is working.

If you receive this, the system is functional.
```

### Test Approval Workflow

1. Create email draft with `requires_approval: true`
2. Run skill to create approval request
3. Manually move file to `/Approved`
4. Verify email is sent
5. Check logs for success

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `process-needs-action` | Receives email requests from inbox |
| `approval-workflow` | Creates approval requests |
| `weekly-briefing` | Reports sent emails in weekly summary |
| `linkedin-poster` | Coordinates email + social campaigns |

## Security Considerations

- Never include credentials in email content
- BCC to records for audit trail
- Respect unsubscribe requests immediately
- Don't send sensitive data (passwords, account numbers)
- Verify recipient email before sending financial documents

## Rate Limiting

To avoid Gmail API limits:

- Max 100 emails/hour (auto-approved)
- Max 500 emails/day (total)
- 2-second delay between bulk sends
- Pause if rate limit warning received

---

*Agent Skill v1.0 - Silver Tier*
*Last Updated: 2026-03-29*
