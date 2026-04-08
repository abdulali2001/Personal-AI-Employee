# AI Employee - Silver Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

This is the **Silver Tier** implementation of the Personal AI Employee Hackathon 0. It builds on Bronze Tier with Gmail monitoring, LinkedIn auto-posting, MCP email integration, and Human-in-the-Loop approval workflows.

## 📋 Silver Tier Deliverables

- [x] All Bronze Tier requirements
- [x] Gmail Watcher - Monitor Gmail for new emails
- [x] LinkedIn Poster - Auto-generate and post business content
- [x] MCP Email Server - Send emails via Gmail API
- [x] Human-in-the-Loop (HITL) approval workflow
- [x] Plan generation for multi-step tasks
- [x] Enhanced orchestrator with Silver Tier features
- [x] All AI functionality as Agent Skills

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│     Gmail       │────▶│  Gmail Watcher   │────▶│  Needs_Action   │
│   (Incoming)    │     │  (Python)        │     │  (Obsidian)     │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐             │
│    LinkedIn     │◀────│  LinkedIn Poster │◀────────────┤
│   (Outgoing)    │     │  (Playwright)    │             │
└─────────────────┘     └──────────────────┘             │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Dashboard.md   │◀────│  Qwen Code       │◀────│  Orchestrator   │
│  (Status)       │     │  (Reasoning)     │     │  (Coordinator)  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
┌─────────────────┐     ┌──────────────────┐             │
│   Gmail Send    │◀────│  MCP Email       │◀────────────┤
│  (Outgoing)     │     │  Server          │             │
└─────────────────┘     └──────────────────┘
```

## 📁 Project Structure

```
Personal -AI-Employee/
├── AI_Employee_Vault/       # Obsidian vault (dashboard & data)
│   ├── Dashboard.md         # Real-time status dashboard
│   ├── Company_Handbook.md  # Rules of engagement
│   ├── Business_Goals.md    # Objectives and metrics
│   ├── Needs_Action/        # Items requiring processing
│   ├── In_Progress/         # Currently active tasks
│   ├── Pending_Approval/    # Awaiting human decision
│   ├── Approved/            # Ready for execution
│   ├── Rejected/            # Declined actions
│   ├── Done/                # Completed items (archive)
│   ├── Plans/               # Multi-step task plans
│   ├── Logs/                # System activity logs
│   ├── Briefings/           # CEO briefings
│   ├── LinkedIn_Posts/      # LinkedIn draft posts
│   └── Files/               # Processed file attachments
│
├── watchers/                # Watcher scripts
│   ├── base_watcher.py      # Base class for all watchers
│   ├── filesystem_watcher.py # File system monitor
│   ├── gmail_watcher.py     # Gmail monitor (NEW - Silver)
│   └── linkedin_poster.py   # LinkedIn auto-poster (NEW - Silver)
│
├── skills/                  # Agent Skills for Qwen Code
│   ├── process-needs-action.md      # Core task processing
│   ├── email-mcp-sender.md          # Email sending (NEW - Silver)
│   ├── gmail-watcher.md             # Gmail monitoring (NEW - Silver)
│   ├── whatsapp-watcher.md          # WhatsApp monitoring (NEW - Silver)
│   ├── linkedin-poster.md           # LinkedIn posting (NEW - Silver)
│   ├── approval-workflow.md         # HITL workflow (NEW - Silver)
│   ├── plan-generator.md            # Plan creation (NEW - Silver)
│   └── weekly-briefing.md           # CEO briefing (NEW - Silver)
│
├── mcp_email_server.py      # MCP server for email (NEW - Silver)
├── orchestrator.py          # Master coordinator (Enhanced)
├── requirements.txt         # Python dependencies
├── credentials.json.template # Gmail OAuth template
├── SILVER_TIER_SETUP.md    # Setup guide (NEW)
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | Reasoning engine |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Dashboard |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers (future) |

### Installation

**Step 1: Install Dependencies**

```bash
cd "D:\Hackathon 0\Personal-AI-Employee"
pip install -r requirements.txt
playwright install chromium
```

**Step 2: Setup Gmail API**

1. Follow [SILVER_TIER_SETUP.md](SILVER_TIER_SETUP.md) for Gmail OAuth setup
2. Download `credentials.json` from Google Cloud Console
3. Place in project root directory

**Step 3: First-Time Authentication**

```bash
# Gmail authentication
python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json

# LinkedIn authentication
python watchers/linkedin_poster.py "AI_Employee_Vault" login
```

**Step 4: Open the vault in Obsidian**:
- Launch Obsidian
- Click "Open folder as vault"
- Select `AI_Employee_Vault` folder

**Step 5: Verify Qwen Code installation**:
```bash
qwen --version
```

### Running the AI Employee

#### Option 1: Start All Components

```bash
# Terminal 1: Start Gmail Watcher
cd "D:\Hackathon 0\Personal-AI-Employee"
python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json

# Terminal 2: Start the Orchestrator
cd "D:\Hackathon 0\Personal-AI-Employee"
python orchestrator.py "AI_Employee_Vault"

# Terminal 3: Process tasks with Qwen Code
cd "D:\Hackathon 0\Personal-AI-Employee"
qwen --cwd "AI_Employee_Vault" --prompt "Process all files in /Needs_Action and /Pending_Approval"
```

#### Option 2: Manual Processing

```bash
# Check Gmail manually
python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json

# Create LinkedIn post draft
python watchers/linkedin_poster.py "AI_Employee_Vault" draft business_update "Your Topic"

# Process tasks with Qwen Code
qwen --cwd "AI_Employee_Vault" --prompt "Process all pending tasks"
```

#### Option 3: Scheduled (Windows Task Scheduler)

Set up scheduled tasks for:
- Gmail Watcher: Every 5 minutes
- Orchestrator: Every 10 minutes
- Weekly Briefing: Monday 7:00 AM

See [SILVER_TIER_SETUP.md](SILVER_TIER_SETUP.md) for detailed scheduling instructions.

## 📖 Usage Guide

### How It Works

1. **Gmail Watcher detects** new email and creates action file in `/Needs_Action`

2. **Orchestrator picks up** the task, creates Plan.md in `/Plans`

3. **Qwen Code processes** the task according to `Company_Handbook.md` rules

4. **Approval workflow** - If action requires approval (email send, LinkedIn post), file moves to `/Pending_Approval`

5. **Human approves** by moving file from `/Pending_Approval` to `/Approved`

6. **MCP server executes** the approved action (send email, post to LinkedIn)

7. **Task completes** and moves to `/Done`, Dashboard updates

### Silver Tier Features

#### Gmail Integration

```bash
# Monitor Gmail continuously
python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json

# Emails appear in /Needs_Action as:
# EMAIL_{subject}_{sender}_{timestamp}.md
```

#### LinkedIn Auto-Posting

```bash
# Create draft post
python watchers/linkedin_poster.py "AI_Employee_Vault" draft business_update "New Product Launch"

# Draft saved to /LinkedIn_Posts/
# Move to /Pending_Approval for posting
# Qwen Code will post after approval
```

#### Email Sending via MCP

```bash
# Send email directly
python mcp_email_server.py send \
  --to "client@example.com" \
  --subject "Invoice #123" \
  --body "Please find attached..."

# Or via approval workflow
# 1. Create approval request in /Pending_Approval
# 2. Human moves to /Approved
# 3. Orchestrator sends via MCP
```

#### Plan Generation

Complex tasks automatically get Plan.md files:
- Multi-step workflows
- Tasks requiring approval
- Cross-domain operations

Plans include:
- Clear objectives
- Step-by-step checklist
- Success criteria
- Progress tracking

## ⚙️ Configuration

### Watcher Settings

Edit `watchers/filesystem_watcher.py` to customize:

```python
# Check interval (default: 5 seconds)
check_interval = 5

# Drop folder path
drop_folder = Path("D:/DropFolder")
```

### Orchestrator Settings

Edit `orchestrator.py` to customize:

```python
# Check interval (default: 30 seconds)
check_interval = 30

# Vault path
vault_path = Path("AI_Employee_Vault")
```

### Company Handbook Rules

Customize `Company_Handbook.md` to set your rules:

- Approval thresholds
- Communication guidelines
- Priority classifications
- Security rules

## 🧪 Testing

### Test Gmail Watcher

```bash
# 1. Send yourself an email with subject "Test - AI Employee"

# 2. Run Gmail Watcher
python watchers/gmail_watcher.py "AI_Employee_Vault" credentials.json

# 3. Check /Needs_Action for new email file
# 4. Verify email marked as read in Gmail
```

### Test LinkedIn Poster

```bash
# 1. Create draft post
python watchers/linkedin_poster.py "AI_Employee_Vault" draft business_update "Test Post"

# 2. Check /LinkedIn_Posts for draft file
# 3. Review content
# 4. Move to /Pending_Approval for posting
```

### Test MCP Email Server

```bash
# 1. Test send
python mcp_email_server.py send \
  --to "your-email@gmail.com" \
  --subject "Test Email" \
  --body "This is a test from AI Employee"

# 2. Check inbox for test email
```

### Test Approval Workflow

```bash
# 1. Create test approval file in /Pending_Approval
# 2. Run orchestrator
python orchestrator.py "AI_Employee_Vault"

# 3. Move file to /Approved
# 4. Run orchestrator again
# 5. Verify file moved to /Done
```

### Test Plan Generation

```bash
# 1. Create complex task in /Needs_Action
# 2. Run orchestrator
python orchestrator.py "AI_Employee_Vault"

# 3. Check /Plans for new plan file
# 4. Verify steps match task type
```

## 📊 Dashboard

The `Dashboard.md` provides real-time status:

| Section | Description |
|---------|-------------|
| Quick Status | Pending actions, approvals, completions |
| Inbox Summary | New incoming items |
| Needs Action | Items requiring attention |
| In Progress | Currently active tasks |
| Pending Approval | Awaiting your decision |
| Recent Activity | Last 5 completed tasks |
| System Status | Watcher and orchestrator status |

## 🔧 Troubleshooting

### Watcher Not Detecting Files

1. **Check drop folder path**: Ensure it exists and is accessible
2. **Verify permissions**: Make sure Python can read the folder
3. **Check logs**: Look in `/Logs/watcher_*.log` for errors

### Orchestrator Not Processing

1. **Check folder paths**: Ensure vault structure exists
2. **Verify Python version**: Must be 3.13+
3. **Check logs**: Look in `/Logs/orchestrator_*.log`

### Qwen Code Not Found

```bash
# Install Qwen Code
# Follow installation instructions at: https://github.com/QwenLM/Qwen

# Verify installation
qwen --version
```

### Tasks Stuck in In_Progress

1. **Manual processing**: Run Qwen Code manually
2. **Check task file**: Ensure valid markdown format
3. **Review Company Handbook**: Rules may require approval

## 🎯 Next Steps (Gold Tier)

After mastering Silver Tier, upgrade to Gold:

- [ ] WhatsApp Watcher for messaging monitoring
- [ ] Weekly CEO Briefing generation
- [ ] Odoo accounting integration
- [ ] Multiple MCP servers
- [ ] Ralph Wiggum loop for persistence
- [ ] Comprehensive error recovery
- [ ] Cloud deployment for 24/7 operation

## 📝 Hackathon Checklist

### Bronze Tier (Complete)

- [x] Obsidian vault with Dashboard.md
- [x] Company_Handbook.md with rules
- [x] Business_Goals.md template
- [x] File System Watcher working
- [x] Orchestrator coordinating tasks
- [x] Qwen Code integration
- [x] Basic folder structure
- [x] Agent Skill documentation

### Silver Tier (Complete)

- [x] Gmail Watcher - Monitor incoming emails
- [x] LinkedIn Poster - Auto-post business content
- [x] MCP Email Server - Send emails via Gmail
- [x] Plan generation for multi-step tasks
- [x] HITL approval workflow
- [x] Enhanced orchestrator
- [x] 7 Agent Skills documented

### Gold Tier (Future)

- [ ] WhatsApp Watcher
- [ ] Weekly CEO Briefing
- [ ] Odoo accounting integration
- [ ] Multiple MCP servers
- [ ] Ralph Wiggum loop
- [ ] Error recovery system
- [ ] Comprehensive audit logging

## 🔐 Security Notes

- **Never commit** `.env` files with credentials
- **Review logs** weekly for unusual activity
- **Rotate credentials** monthly
- **Keep vault local** - use Git with `.gitignore` for sync

## 📚 Resources

- [Hackathon Specification](Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026%20(2).md)
- [Qwen Code Documentation](https://github.com/QwenLM/Qwen)
- [Obsidian Help](https://help.obsidian.md)
- [Wednesday Research Meetings](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)

## 🤝 Support

- **Issues**: Create an issue in the repository
- **Discussions**: Join Wednesday research meetings
- **Documentation**: Check the hackathon spec

---

*Built for Personal AI Employee Hackathon 0 - Bronze Tier*

*Version: 1.0 | Date: 2026-03-27*
