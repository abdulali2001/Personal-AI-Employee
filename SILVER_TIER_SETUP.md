# Silver Tier Setup Guide

> **Complete setup instructions for AI Employee Silver Tier**

This guide walks you through setting up all Silver Tier components: Gmail Watcher, LinkedIn Poster, MCP Email Server, and the enhanced Orchestrator.

## Prerequisites

Ensure you have completed Bronze Tier setup:
- [x] Python 3.13+ installed
- [x] Qwen Code installed and working
- [x] Obsidian vault created
- [x] Basic folder structure in place

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd "D:\Hackathon 0\Personal-AI-Employee"

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Step 2: Gmail API Setup

### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select existing project
3. Name it "AI Employee" (or your choice)
4. Click "Create"

### 2.2 Enable Gmail API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on it and press "Enable"

### 2.3 Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: "External"
   - App name: "AI Employee"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Skip for now
   - Test users: Add your Gmail address
   - Click "Save and Continue"

4. Create OAuth Client ID:
   - Application type: "Desktop app"
   - Name: "AI Employee Gmail"
   - Click "Create"

5. Download the credentials:
   - Click "Download JSON"
   - Save as `credentials.json` in project root
   - **Keep this file secure - never commit to git!**

### 2.4 Test Gmail Connection

```bash
# Run Gmail Watcher (will open browser for auth)
python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json
```

First run will:
1. Open browser window
2. Show Google sign-in
3. Request Gmail permissions
4. Save authentication token

**Success:** You should see "Monitoring Gmail for new emails..."

## Step 3: LinkedIn Setup

### 3.1 Install Playwright (if not done)

```bash
playwright install chromium
```

### 3.2 Test LinkedIn Connection

```bash
# Check connection status
python watchers/linkedin_poster.py "AI_Employee_Vault" status
```

### 3.3 Login to LinkedIn

```bash
# First-time login (saves session)
python watchers/linkedin_poster.py "AI_Employee_Vault" login
```

This will:
1. Open browser window
2. Navigate to LinkedIn login
3. **You log in manually** (with 2FA if enabled)
4. Session saved for future runs

**Success:** You should see "✓ LinkedIn connected and ready"

## Step 4: MCP Email Server Setup

### 4.1 Test Email Server

```bash
# Run authentication (uses same credentials as Gmail Watcher)
python mcp_email_server.py auth
```

### 4.2 Test Sending Email

```bash
# Send test email
python mcp_email_server.py send \
  --to "your-email@gmail.com" \
  --subject "Test from AI Employee" \
  --body "This is a test email from the MCP Email Server."
```

**Success:** You should receive the test email.

## Step 5: Configure Orchestrator

The orchestrator has been updated for Silver Tier with:
- Plan generation for complex tasks
- HITL approval workflow
- MCP email integration
- LinkedIn posting support

### 5.1 Update Company Handbook

Add these rules to `AI_Employee_Vault/Company_Handbook.md`:

```markdown
## Email Rules

- Auto-reply to known contacts: YES
- Send invoices: Requires approval
- Bulk emails (>5): Requires approval
- New contacts: Requires approval

## LinkedIn Rules

- All posts: Requires approval before posting
- Post frequency: 3-5 times per week
- Content types: Business updates, thought leadership, client wins
- Brand tone: Professional, friendly, helpful

## Approval Thresholds

- Email payments: Always requires approval
- LinkedIn posts: Always requires approval
- Client communications: Auto-approve for known contacts
```

### 5.2 Test Orchestrator

```bash
# Run orchestrator (single cycle)
python orchestrator.py "AI_Employee_Vault"
```

## Step 6: Create Test Tasks

### 6.1 Test Gmail Watcher

1. Send yourself an email with subject "Test - AI Employee"
2. Run Gmail Watcher:
   ```bash
   python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json
   ```
3. Check `AI_Employee_Vault/Needs_Action/` for new email file

### 6.2 Test LinkedIn Poster

```bash
# Create draft post
python watchers/linkedin_poster.py "AI_Employee_Vault" draft business_update "New AI Feature Launch"
```

Check `AI_Employee_Vault/LinkedIn_Posts/` for draft file.

### 6.3 Test Approval Workflow

1. Move draft from `LinkedIn_Posts/` to `Pending_Approval/`
2. Run orchestrator:
   ```bash
   python orchestrator.py "AI_Employee_Vault"
   ```
3. Check if plan was created in `Plans/`

## Step 7: Running All Components

### Option A: Manual Processing (Recommended for Testing)

```bash
# Terminal 1: Gmail Watcher
python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json

# Terminal 2: Process tasks with Qwen Code
qwen --cwd "AI_Employee_Vault" --prompt "Process all files in /Needs_Action and /Pending_Approval"
```

### Option B: Automated Orchestrator

```bash
# Terminal 1: Gmail Watcher
python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json

# Terminal 2: Orchestrator (continuous)
python orchestrator.py "AI_Employee_Vault"
```

### Option C: Scheduled Processing (Windows Task Scheduler)

Create scheduled tasks:

**Gmail Check (every 5 minutes):**
```
Program: python.exe
Args: watchers/gmail_watcher.py "D:\Hackathon 0\Personal-AI-Employee\AI_Employee_Vault" credentials.json
Start in: D:\Hackathon 0\Personal-AI-Employee
```

**Orchestrator (every 10 minutes):**
```
Program: python.exe
Args: orchestrator.py "D:\Hackathon 0\Personal-AI-Employee\AI_Employee_Vault"
Start in: D:\Hackathon 0\Personal-AI-Employee
```

## Step 8: Verify Silver Tier Checklist

| Requirement | Component | Status |
|-------------|-----------|--------|
| 2+ Watcher scripts | Gmail + LinkedIn | ✅ |
| LinkedIn auto-posting | linkedin_poster.py | ✅ |
| Plan.md generation | orchestrator.create_plan() | ✅ |
| MCP server integration | mcp_email_server.py | ✅ |
| HITL approval workflow | /Pending_Approval folder | ✅ |
| All as Agent Skills | /skills/*.md files | ✅ |

## Troubleshooting

### Gmail Watcher Issues

**Problem:** "Credentials not found"
- **Solution:** Ensure `credentials.json` is in project root

**Problem:** "Token expired"
- **Solution:** Delete `.gmail_token.pickle` and re-run authentication

**Problem:** "No unread emails detected"
- **Solution:** Send yourself a test email, check spam folder

### LinkedIn Poster Issues

**Problem:** "Not logged in"
- **Solution:** Run `python linkedin_poster.py <vault> login`

**Problem:** "Post failed"
- **Solution:** Check LinkedIn session, ensure browser is not blocked

**Problem:** "Playwright timeout"
- **Solution:** Increase timeout in script, check network connection

### MCP Email Server Issues

**Problem:** "Authentication failed"
- **Solution:** Re-run `python mcp_email_server.py auth`

**Problem:** "Email not sent"
- **Solution:** Check Gmail API quota, verify recipient email

### Orchestrator Issues

**Problem:** "No tasks found"
- **Solution:** Create test file in `/Needs_Action` folder

**Problem:** "Plan not created"
- **Solution:** Check task type in frontmatter, verify script has write access

## Next Steps (Gold Tier)

After Silver Tier is working:

1. **Weekly Briefing:** Implement CEO Briefing generation
2. **WhatsApp Watcher:** Add WhatsApp Web monitoring
3. **Odoo Integration:** Connect accounting system
4. **Ralph Wiggum Loop:** Implement persistence pattern
5. **Cloud Deployment:** Run on cloud VM 24/7

## Quick Reference

### Start All Watchers

```bash
# Gmail (background)
start /B python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json

# Orchestrator (foreground)
python orchestrator.py "AI_Employee_Vault"
```

### Process Pending Tasks

```bash
# With Qwen Code
qwen --cwd "AI_Employee_Vault" --prompt "Process all pending tasks and approvals"
```

### Check Status

```bash
# Gmail connection
python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json

# LinkedIn connection
python watchers/linkedin_poster.py "AI_Employee_Vault" status

# Email server
python mcp_email_server.py test
```

## Security Notes

- **Never commit** `credentials.json` or `.gmail_token.pickle`
- Add to `.gitignore`:
  ```
  credentials.json
  .gmail_token.pickle
  .linkedin_session/
  .env
  ```
- Rotate credentials monthly
- Review logs weekly for unusual activity

## Support

- **Documentation:** See `/skills/*.md` files for detailed skill documentation
- **Logs:** Check `AI_Employee_Vault/Logs/` for watcher and orchestrator logs
- **Hackathon Spec:** See main specification document for full requirements

---

*Silver Tier Setup Guide v1.0*
*Last Updated: 2026-03-29*
