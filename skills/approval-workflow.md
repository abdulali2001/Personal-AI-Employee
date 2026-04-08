---
name: approval-workflow
description: |
  Human-in-the-Loop (HITL) approval workflow for sensitive actions.
  This skill manages the approval process for actions that require human
  decision before execution, such as sending emails, making payments,
  or posting to social media.

  When invoked, this skill will:
  1. Identify actions requiring approval
  2. Create structured approval request files
  3. Move files between folders based on status
  4. Track approval deadlines and escalations
  5. Execute approved actions via MCP servers

  Use for: Payment approvals, email sends, social media posts,
  contract reviews, any sensitive business action
---

# Approval Workflow - Agent Skill

## Overview

This skill implements the Human-in-the-Loop (HITL) pattern for the AI Employee.
It ensures that sensitive actions always require human review and approval
before execution, providing a safety layer for autonomous operations.

## Core Principles

1. **Never auto-execute sensitive actions** - Always require approval
2. **Clear context** - Provide all information needed for decision
3. **Easy approval** - Simple file movement to approve
4. **Audit trail** - Log all approvals and rejections
5. **Timeout handling** - Escalate or expire stale requests

## Approval Categories

### Category 1: Financial Actions

| Action | Auto-Approve Threshold | Always Requires Approval |
|--------|----------------------|-------------------------|
| Payments | < $50 (recurring) | All new payees, > $100 |
| Invoices | Generated only | Sending to clients |
| Refunds | Any amount | All refunds |
| Subscriptions | < $20/month | > $50/month or annual |

### Category 2: Communication Actions

| Action | Auto-Approve | Requires Approval |
|--------|-------------|-------------------|
| Email replies | Known contacts | New contacts, bulk |
| WhatsApp messages | Individual replies | Group messages, broadcasts |
| LinkedIn posts | Never | All posts |
| Social media replies | Generic responses | Custom responses |

### Category 3: Data Actions

| Action | Auto-Approve | Requires Approval |
|--------|-------------|-------------------|
| File create/edit | Within vault | Outside vault |
| File delete | Draft files only | Original files |
| Data export | Personal data | Business data |
| API calls | Read-only | Write operations |

## Approval Request Schema

```markdown
---
type: approval_request
action: send_email
action_category: communication
priority: normal
created: 2026-03-29T10:30:00Z
expires: 2026-03-30T10:30:00Z
status: pending
requires_approval: true
---

# Approval Required: [Action Name]

## Action Details

| Field | Value |
|-------|-------|
| **Action Type** | Send Email |
| **Category** | Communication |
| **Priority** | Normal |
| **Created** | 2026-03-29 10:30 AM |
| **Expires** | 2026-03-30 10:30 AM |
| **Time Remaining** | 23 hours 45 minutes |

## Why Approval is Required

This action requires approval because:
- [x] Sending email to external recipient
- [ ] Payment to new vendor
- [ ] Social media post
- [ ] Other: _______________

## Action Details

### Email Information

| Field | Value |
|-------|-------|
| **To** | client@example.com |
| **Subject** | Invoice #123 - January 2026 |
| **Attachments** | 1 file (245 KB) |
| **Priority** | Normal |

## Full Content/Details

```
Dear Client,

Please find attached your invoice for January 2026.

Amount Due: $1,500.00
Due Date: February 15, 2026

Best regards,
AI Employee
```

## Context

- Client requested invoice via WhatsApp on 2026-03-28
- Invoice generated based on agreed rate ($1,500)
- Payment terms: Net 15 days
- This is a follow-up to previous conversation

## Impact Assessment

| Aspect | Assessment |
|--------|------------|
| **Financial** | None (invoice, not payment) |
| **Reputation** | Positive (professional communication) |
| **Legal** | None (standard business document) |
| **Relationship** | Positive (responsive service) |

## To Approve

**Option 1: Move File**
1. Move this file to `/Approved` folder
2. AI will execute the action automatically

**Option 2: Quick Approve** (if implemented)
1. Run: `qwen --prompt "Approve pending action: [filename]"`

## To Request Changes

1. Add your comments below this line
2. Move file back to `/Needs_Action`
3. AI will revise and resubmit

## To Reject

1. Add reason for rejection below
2. Move file to `/Rejected` folder
3. AI will log and notify if needed

---
*Created by AI Employee - requires human decision*
*This request will expire in 24 hours if not actioned*
```

## Workflow

### Step 1: Determine if Approval is Needed

```python
def requires_approval(action_type, action_details, company_handbook):
    """Determine if an action requires human approval"""
    
    # Load approval rules from Company_Handbook.md
    rules = company_handbook.get('approval_rules', {})
    
    # Check action type
    if action_type in rules.get('always_require_approval', []):
        return True
    
    # Check thresholds
    if action_type == 'payment':
        amount = action_details.get('amount', 0)
        threshold = rules.get('payment_threshold', 100)
        if amount > threshold:
            return True
    
    # Check if new recipient
    if action_type == 'email':
        recipient = action_details.get('to', '')
        known_contacts = rules.get('known_contacts', [])
        if recipient not in known_contacts:
            return True
    
    # Check if bulk action
    if action_details.get('is_bulk', False):
        return True
    
    return False
```

### Step 2: Create Approval Request

```python
def create_approval_request(action_data, vault_path):
    """Create approval request file in Pending_Approval folder"""
    timestamp = datetime.now().isoformat()
    expiry = datetime.now().replace(hour=10, minute=30)
    expiry = expiry + timedelta(days=1)  # 24 hour expiry
    
    # Generate filename
    safe_action = action_data['action'].replace(' ', '_')[:20]
    filename = f"APPROVAL_{safe_action}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    
    content = f"""---
type: approval_request
action: {action_data['action']}
action_category: {action_data['category']}
priority: {action_data.get('priority', 'normal')}
created: {timestamp}
expires: {expiry.isoformat()}
status: pending
requires_approval: true
---

# Approval Required: {action_data['title']}

## Action Details

[... rest of template ...]
"""
    
    filepath = Path(vault_path) / 'Pending_Approval' / filename
    filepath.write_text(content, encoding='utf-8')
    return filepath
```

### Step 3: Monitor Pending Approvals

```python
def check_pending_approvals(vault_path):
    """Check for expired or stale approvals"""
    pending_folder = Path(vault_path) / 'Pending_Approval'
    now = datetime.now()
    
    expired = []
    stale = []
    
    for approval_file in pending_folder.glob('*.md'):
        content = approval_file.read_text()
        
        # Extract expiry time from frontmatter
        expiry_match = re.search(r'expires:\s*(\S+)', content)
        if expiry_match:
            expiry = datetime.fromisoformat(expiry_match.group(1))
            
            if expiry < now:
                expired.append(approval_file)
            elif expiry < now + timedelta(hours=2):
                stale.append(approval_file)
    
    return {
        'expired': expired,
        'stale': stale
    }
```

### Step 4: Process Approved Actions

```python
def process_approved_actions(vault_path, mcp_servers):
    """Process actions that have been approved"""
    approved_folder = Path(vault_path) / 'Approved'
    results = []
    
    for approval_file in approved_folder.glob('*.md'):
        content = approval_file.read_text()
        
        # Parse action details
        action_data = parse_approval_request(content)
        
        try:
            # Execute based on action type
            if action_data['action'] == 'send_email':
                result = mcp_servers['email'].send_email(action_data['details'])
            elif action_data['action'] == 'make_payment':
                result = mcp_servers['payment'].process_payment(action_data['details'])
            elif action_data['action'] == 'post_linkedin':
                result = mcp_servers['linkedin'].post_content(action_data['details'])
            else:
                result = {'status': 'unknown_action', 'action': action_data['action']}
            
            # Log result
            log_action(approval_file, result)
            
            # Move to Done
            if result.get('status') == 'success':
                approval_file.rename(Path(vault_path) / 'Done' / approval_file.name)
                results.append({'file': approval_file.name, 'status': 'completed'})
            else:
                # Move back for review on failure
                approval_file.rename(Path(vault_path) / 'Needs_Action' / approval_file.name)
                results.append({'file': approval_file.name, 'status': 'failed'})
                
        except Exception as e:
            results.append({'file': approval_file.name, 'status': 'error', 'error': str(e)})
    
    return results
```

### Step 5: Handle Expired Approvals

```python
def handle_expired_approvals(expired_files, vault_path):
    """Handle approval requests that have expired"""
    for approval_file in expired_files:
        content = approval_file.read_text()
        
        # Add expiry marker
        content += f"""

---
## EXPIRED
This approval request expired on {datetime.now().isoformat()}.
Action was not taken due to timeout.
"""
        approval_file.write_text(content)
        
        # Move to Rejected
        approval_file.rename(Path(vault_path) / 'Rejected' / approval_file.name)
        
        # Create notification
        create_notification(
            vault_path,
            f"Approval expired: {approval_file.name}",
            "The above approval request expired without action. "
            "If this action is still needed, please recreate the request."
        )
```

## Approval Folder Structure

```
Vault/
├── Pending_Approval/
│   ├── APPROVAL_send_email_20260329_1030.md
│   ├── APPROVAL_payment_20260329_1145.md
│   └── APPROVAL_linkedin_post_20260329_1500.md
├── Approved/
│   └── (files moved here when human approves)
├── Rejected/
│   └── (files moved here when rejected)
└── Done/
    └── (files moved here after successful execution)
```

## Quick Approval Commands

### Approve Single Action

```bash
qwen --cwd "/path/to/vault" --prompt "Process approval request: APPROVAL_send_email_20260329_1030.md"
```

### Approve All Pending

```bash
qwen --cwd "/path/to/vault" --prompt "List all pending approvals and their details"
```

### Check Approval Status

```bash
qwen --cwd "/path/to/vault" --prompt "Show status of all pending approvals"
```

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `email-mcp-sender` | Creates approval for new contacts |
| `linkedin-poster` | All posts require approval |
| `whatsapp-watcher` | Approval for bulk messages |
| `weekly-briefing` | Reports approval statistics |

## Logging & Audit

### Approval Log Schema

```json
{
  "timestamp": "2026-03-29T10:45:00Z",
  "action_type": "send_email",
  "approval_id": "APPROVAL_send_email_20260329_1030",
  "created": "2026-03-29T10:30:00Z",
  "approved_at": "2026-03-29T10:44:00Z",
  "approved_by": "human",
  "execution_time": "2026-03-29T10:45:00Z",
  "execution_result": "success",
  "details": {
    "to": "client@example.com",
    "subject": "Invoice #123"
  }
}
```

### Weekly Approval Report

Generated by `weekly-briefing` skill:

```markdown
## Approval Statistics (Week of March 23-29, 2026)

| Metric | Value |
|--------|-------|
| Total Requests | 15 |
| Approved | 12 (80%) |
| Rejected | 2 (13%) |
| Expired | 1 (7%) |

### By Category

| Category | Count | Approved | Rejected |
|----------|-------|----------|----------|
| Email | 8 | 7 | 1 |
| Payment | 4 | 3 | 1 |
| Social Media | 3 | 2 | 0 |

### Average Response Time

- Time to approval: 2.5 hours (avg)
- Fastest: 5 minutes
- Slowest: 18 hours
```

## Error Handling

### Approval File Corrupted

```markdown
1. Log error with file details
2. Move to /Needs_Action with error marker
3. Create notification for human review
4. Don't execute the action
```

### MCP Execution Failed

```markdown
1. Log error with full details
2. Move approval back to /Needs_Action
3. Add error details to file
4. Notify human of failure
5. Don't retry without fresh approval
```

### Approval Loop Detected

```markdown
1. Detect if same action submitted multiple times
2. Log potential loop condition
3. Pause similar approvals
4. Create alert for human review
```

## Testing

### Test Approval Creation

```bash
qwen --cwd "/path/to/vault" --prompt "Create a test approval request for sending an email"
```

### Test Approval Flow

1. Create test approval request
2. Manually move to `/Approved`
3. Run processor to execute
4. Verify action completed
5. Check file moved to `/Done`

### Test Expiry Handling

1. Create approval with past expiry time
2. Run expiry checker
3. Verify file moved to `/Rejected`
4. Check notification created

## Security Considerations

- Never bypass approval for sensitive actions
- Log all approval decisions
- Require human movement (not automated)
- Don't store credentials in approval files
- Redact sensitive info in logs

## Best Practices

1. **Clear Titles**: Make action obvious at a glance
2. **Complete Context**: Include all relevant information
3. **Reasonable Deadlines**: 24-48 hours for most actions
4. **Priority Marking**: High priority for time-sensitive
5. **Impact Assessment**: Help human understand consequences

---

*Agent Skill v1.0 - Silver Tier*
*Last Updated: 2026-03-29*
