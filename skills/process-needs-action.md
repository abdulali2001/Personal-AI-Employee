---
name: process-needs-action
description: |
  Process files in the Needs_Action folder. This is the core Agent Skill for the
  AI Employee Bronze Tier. Use this skill to analyze incoming tasks, create plans,
  execute actions, and manage task lifecycle.
  
  When invoked, this skill will:
  1. Read all files in /Needs_Action or /In_Progress
  2. Analyze what action is needed based on content and type
  3. Create a plan in /Plans if the task has multiple steps
  4. Execute simple actions directly (file operations, analysis)
  5. Create approval requests in /Pending_Approval for sensitive actions
  6. Move completed tasks to /Done
---

# Process Needs Action - Agent Skill

## Overview

This skill enables Qwen Code to autonomously process tasks in the AI Employee vault.
It follows the rules defined in `Company_Handbook.md` and updates `Dashboard.md`.

## Usage

### Manual Invocation

```bash
qwen --cwd "/path/to/vault" --prompt "Process all files in /Needs_Action"
```

### From Orchestrator

The orchestrator.py automatically triggers this skill when tasks are detected.

## Task Processing Workflow

### Step 1: Read and Analyze

```markdown
1. Read the task file content
2. Extract metadata from frontmatter (type, priority, status)
3. Identify the required action type
4. Check Company_Handbook.md for relevant rules
```

### Step 2: Plan (if needed)

For multi-step tasks, create a plan file:

```markdown
---
created: 2026-03-27T10:00:00Z
task_file: FILE_example_2026-03-27.md
status: planning
---

# Plan: [Task Description]

## Objective
Clear statement of what needs to be accomplished.

## Steps
- [ ] Step 1: Analysis
- [ ] Step 2: Action
- [ ] Step 3: Verification
- [ ] Step 4: Completion

## Approval Required
Yes/No - If yes, specify what needs approval.

## Estimated Time
X minutes/hours
```

### Step 3: Execute

Execute based on task type:

| Type | Action |
|------|--------|
| `file_drop` | Analyze content, determine next steps |
| `email` | Draft reply or create approval request |
| `whatsapp` | Analyze message, suggest response |
| `approval_request` | Wait for human decision |

### Step 4: Complete

When task is done:
1. Add completion timestamp to task file
2. Move file to `/Done` folder
3. Update `Dashboard.md`
4. Log the action

## Action Types

### File Operations (Auto-Approve)

These actions can be performed without approval:

- Reading files
- Creating drafts
- Organizing content
- Creating summaries
- Moving files between vault folders

### Actions Requiring Approval

These actions require human approval before execution:

- Sending emails to external recipients
- Making any payment
- Posting to social media
- Deleting files outside vault
- Accessing external APIs with credentials

## Creating Approval Requests

When an action requires approval, create a file in `/Pending_Approval`:

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #123
created: 2026-03-27T10:00:00Z
expires: 2026-03-28T10:00:00Z
status: pending
---

# Approval Required: Send Email

## Action Details
- **Type**: Send Email
- **To**: client@example.com
- **Subject**: Invoice #123
- **Attachment**: /Invoices/2026-01_Client_A.pdf

## Context
Client A requested their January invoice. The invoice has been generated
and is ready to send.

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with a note explaining why.

---
*Created by AI Employee - requires human decision*
```

## Error Handling

### If Task is Unclear

1. Add analysis notes to the task file
2. Create a clarification request in `/Pending_Approval`
3. Do not proceed until clarified

### If Required Information is Missing

1. Document what's missing
2. Suggest how to obtain it
3. Move to `/Needs_Action` with notes

### If Action Fails

1. Log the error with full context
2. Retry up to 3 times (for transient errors)
3. After 3 failures, create error report in `/Pending_Approval`

## Examples

### Example 1: Processing a File Drop

```
Input: FILE_document.pdf in /Needs_Action
Analysis: PDF document dropped for processing
Action: 
  1. Read PDF content (if possible)
  2. Create summary in task file
  3. Ask user what action to take
  4. Move to /Done with notes
```

### Example 2: Processing an Email Request

```
Input: EMAIL_reply_request.md in /Needs_Action
Analysis: Request to reply to client email
Action:
  1. Draft reply content
  2. Create approval request in /Pending_Approval
  3. Wait for human to move to /Approved
  4. When approved, send via MCP or mark as ready
```

## Integration with Company Handbook

Always reference `Company_Handbook.md` for:

- Priority classification rules
- Approval thresholds
- Communication guidelines
- Security requirements
- Quality standards

## Dashboard Update Template

After processing tasks, update Dashboard.md:

```markdown
## Quick Status Updates

- Increment "Tasks Completed Today" counter
- Update "Pending Actions" count
- Add entry to "Recent Activity"
- Update timestamp
```

## Testing This Skill

1. Create a test file in `/Needs_Action`:
   ```markdown
   ---
   type: test
   status: pending
   ---
   
   # Test Task
   
   This is a test to verify the Process Needs Action skill works.
   
   ## Expected Actions
   - [ ] Acknowledge receipt
   - [ ] Create a plan
   - [ ] Move to /Done
   ```

2. Run Qwen Code:
   ```bash
   qwen --cwd "/path/to/vault" --prompt "Process all files in /Needs_Action"
   ```

3. Verify:
   - Task was analyzed
   - Plan was created (if needed)
   - File moved to /Done
   - Dashboard updated

---

*Agent Skill v1.0 - Bronze Tier*
