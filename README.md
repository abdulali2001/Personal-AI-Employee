# AI Employee - Bronze Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

This is the **Bronze Tier** implementation of the Personal AI Employee Hackathon 0. It provides the foundational layer for an autonomous AI employee that uses Obsidian as the dashboard and Qwen Code as the reasoning engine.

## 📋 Bronze Tier Deliverables

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (File System Watcher)
- [x] Qwen Code integration for reading/writing to the vault
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] Agent Skill for processing tasks

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Drop Folder    │────▶│  File Watcher    │────▶│  Needs_Action   │
│  (Input)        │     │  (Python)        │     │  (Obsidian)     │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Dashboard.md   │◀────│  Qwen Code       │◀────│  Orchestrator   │
│  (Status)       │     │  (Reasoning)     │     │  (Coordinator)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 📁 Project Structure

```
Personal -AI-Employee/
├── AI_Employee_Vault/       # Obsidian vault (dashboard & data)
│   ├── Dashboard.md         # Real-time status dashboard
│   ├── Company_Handbook.md  # Rules of engagement
│   ├── Business_Goals.md    # Objectives and metrics
│   ├── Inbox/               # Raw incoming items
│   ├── Needs_Action/        # Items requiring processing
│   ├── In_Progress/         # Currently active tasks
│   ├── Pending_Approval/    # Awaiting human decision
│   ├── Approved/            # Ready for execution
│   ├── Rejected/            # Declined actions
│   ├── Done/                # Completed items (archive)
│   ├── Plans/               # Multi-step task plans
│   ├── Logs/                # System activity logs
│   ├── Briefings/           # CEO briefings
│   ├── Accounting/          # Financial records
│   └── Files/               # Processed file attachments
│
├── watchers/                # Watcher scripts
│   ├── base_watcher.py      # Base class for all watchers
│   └── filesystem_watcher.py # File system monitor
│
├── skills/                  # Agent Skills for Qwen Code
│   └── process-needs-action.md
│
├── orchestrator.py          # Master coordinator
├── requirements.txt         # Python dependencies
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

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Open the vault in Obsidian**:
   - Launch Obsidian
   - Click "Open folder as vault"
   - Select `AI_Employee_Vault` folder

4. **Verify Qwen Code installation**:
   ```bash
   qwen --version
   ```

### Running the AI Employee

#### Option 1: Start All Components

```bash
# Terminal 1: Start the File Watcher
cd "D:\Hackathon 0\Personal -AI-Employee"
python watchers/filesystem_watcher.py "AI_Employee_Vault" "D:\DropFolder"

# Terminal 2: Start the Orchestrator
cd "D:\Hackathon 0\Personal -AI-Employee"
python orchestrator.py "AI_Employee_Vault"
```

#### Option 2: Manual Processing

```bash
# Process tasks manually with Qwen Code
qwen --cwd "AI_Employee_Vault" --prompt "Process all files in /Needs_Action"
```

## 📖 Usage Guide

### How It Works

1. **Drop a file** into your designated drop folder (e.g., `D:\DropFolder`)

2. **File Watcher detects** the new file and creates an action file in `/Needs_Action`

3. **Orchestrator picks up** the task and moves it to `/In_Progress`

4. **Qwen Code processes** the task according to `Company_Handbook.md` rules

5. **Task completes** and moves to `/Done`, Dashboard updates

### Creating Your First Task

1. **Create a test file**:
   ```bash
   echo "Process this document" > "D:\DropFolder\test.txt"
   ```

2. **Wait 5 seconds** for the watcher to detect it

3. **Check `/Needs_Action`** folder - you should see a new `.md` file

4. **Run Qwen Code**:
   ```bash
   qwen --cwd "AI_Employee_Vault"
   ```

5. **Ask Qwen to**: "Process all files in /Needs_Action following the Company Handbook"

### Understanding the Flow

```
1. User drops file → D:\DropFolder\document.pdf
2. Watcher detects → Creates FILE_document_2026-03-27.md in /Needs_Action
3. Orchestrator → Moves to /In_Progress
4. Qwen Code → Analyzes, creates plan, executes
5. Complete → Moves to /Done, updates Dashboard
```

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

### Test the File Watcher

```bash
# Run watcher once (non-continuous)
python watchers/filesystem_watcher.py "AI_Employee_Vault" "D:\DropFolder"

# Check output for:
# - "Initialized FileSystemWatcher"
# - "Created action file: FILE_*.md"
```

### Test the Orchestrator

```bash
# Run one cycle
python orchestrator.py "AI_Employee_Vault"

# Check output for:
# - "Found X pending task(s)"
# - "Claimed task: *.md"
# - "Dashboard updated"
```

### Test Qwen Code Integration

```bash
# Create a test task manually
echo "---
type: test
status: pending
---

# Test Task
Process this test." > "AI_Employee_Vault/Needs_Action/TEST_2026-03-27.md"

# Run Qwen Code
qwen --cwd "AI_Employee_Vault" --prompt "Process TEST_2026-03-27.md"
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

## 🎯 Next Steps (Silver Tier)

After mastering Bronze Tier, upgrade to Silver:

- [ ] Add Gmail Watcher for email monitoring
- [ ] Add WhatsApp Watcher (Playwright-based)
- [ ] Implement MCP server for sending emails
- [ ] Create human-in-the-loop approval workflow
- [ ] Set up scheduled tasks (cron/Task Scheduler)
- [ ] Auto-post to LinkedIn for business

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

### Silver Tier (Future)

- [ ] Gmail Watcher
- [ ] WhatsApp Watcher
- [ ] MCP email server
- [ ] Approval workflow
- [ ] Scheduled tasks

### Gold Tier (Future)

- [ ] Odoo accounting integration
- [ ] Social media posting
- [ ] Multiple MCP servers
- [ ] CEO Briefing generation
- [ ] Ralph Wiggum loop

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
