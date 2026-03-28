# Personal AI Employee - Project Context

## Project Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) - an autonomous AI employee that manages personal and business affairs 24/7. The architecture is **local-first** and **agent-driven**, using:

- **The Brain**: Claude Code as the reasoning engine
- **The Memory/GUI**: Obsidian (local Markdown) as the dashboard
- **The Senses**: Python "Watcher" scripts monitoring Gmail, WhatsApp, filesystems
- **The Hands**: MCP (Model Context Protocol) servers for external actions

### Key Architecture Concepts

1. **Perception → Reasoning → Action** loop
2. **Watcher Scripts**: Lightweight Python scripts that monitor inputs and create `.md` files in `/Needs_Action` folders
3. **Ralph Wiggum Loop**: A persistence pattern that keeps Claude working autonomously until tasks are complete
4. **Human-in-the-Loop**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)

## Current Project State

### Installed Skills

| Skill | Purpose |
|-------|---------|
| `browsing-with-playwright` | Browser automation via Playwright MCP server |

### Directory Structure

```
Personal -AI-Employee/
├── .qwen/skills/
│   └── browsing-with-playwright/
│       ├── SKILL.md              # Skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool schemas
│       └── scripts/
│           ├── mcp-client.py     # Universal MCP client (HTTP + stdio)
│           ├── start-server.sh   # Start Playwright MCP server
│           ├── stop-server.sh    # Stop Playwright MCP server
│           └── verify.py         # Verify server is running
├── skills-lock.json              # Skill installation registry
└── QWEN.md                       # This file
```

## Building and Running

### Prerequisites

- **Claude Code**: Active subscription
- **Obsidian**: v1.10.6+ (for vault/dashboard)
- **Python**: 3.13+ (for Watcher scripts)
- **Node.js**: v24+ LTS (for MCP servers)

### Playwright MCP Server

```bash
# Start the server (background)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify it's running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py list -u http://localhost:8808

# Call a tool
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 \
  -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Emit tool schemas as markdown
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py emit \
  -u http://localhost:8808
```

### Common Browser Automation Workflow

```bash
# 1. Navigate
mcp-client.py call -u http://localhost:8808 -t browser_navigate -p '{"url": "https://..."}'

# 2. Get accessibility snapshot (find element refs)
mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'

# 3. Interact (click, type, fill forms)
mcp-client.py call -u http://localhost:8808 -t browser_click -p '{"element": "Button", "ref": "e42"}'

# 4. Wait for condition
mcp-client.py call -u http://localhost:8808 -t browser_wait_for -p '{"text": "Success"}'

# 5. Screenshot result
mcp-client.py call -u http://localhost:8808 -t browser_take_screenshot -p '{"fullPage": true}'
```

## Development Conventions

### File-Based Communication

Agents communicate by writing files to specific folders:

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw incoming items |
| `/Needs_Action` | Items requiring processing |
| `/In_Progress/<agent>` | Items claimed by specific agent |
| `/Pending_Approval` | Actions awaiting human approval |
| `/Approved` | Approved actions ready for execution |
| `/Done` | Completed items |
| `/Plans` | Multi-step task plans |
| `/Briefings` | CEO briefing reports |

### Watcher Script Pattern

All Watcher scripts follow the `BaseWatcher` abstract class:

```python
class BaseWatcher(ABC):
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        '''Main loop: check → create files → sleep'''
```

### Markdown File Schema

Action files use frontmatter metadata:

```markdown
---
type: email
from: user@example.com
subject: Urgent Request
priority: high
status: pending
---

## Email Content
...

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
```

## Hackathon Tiers

| Tier | Requirements |
|------|--------------|
| **Bronze** | Obsidian vault, 1 Watcher, Claude reading/writing |
| **Silver** | 2+ Watchers, Plan.md generation, 1 MCP server, HITL workflow |
| **Gold** | Full integration, Odoo accounting, multiple MCPs, Ralph Wiggum loop |
| **Platinum** | Cloud deployment, work-zone specialization, vault sync |

## Key Reference Documents

- [Main Hackathon Spec](Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026%20(2).md) - Full architectural blueprint
- [Playwright Tools](.qwen/skills/browsing-with-playwright/references/playwright-tools.md) - Complete MCP tool reference
- [Skill Documentation](.qwen/skills/browsing-with-playwright/SKILL.md) - Browser automation guide

## Wednesday Research Meetings

- **When**: Wednesdays at 10:00 PM
- **Zoom**: [Link in main spec](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube**: https://www.youtube.com/@panaversity
