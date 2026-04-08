#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for AI Employee (Silver Tier).

The orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process items
3. Creates Plan.md files for multi-step tasks
4. Manages Human-in-the-Loop (HITL) approval workflow
5. Executes approved actions via MCP servers
6. Updates the Dashboard
7. Manages task lifecycle (pending → in_progress → done)

Silver Tier Features:
- Plan generation for complex tasks
- Approval workflow management
- MCP server integration for email sending
- Scheduled operations support

Usage:
    python orchestrator.py /path/to/vault

Example:
    python orchestrator.py "D:/Hackathon 0/Personal-AI-Employee/AI_Employee_Vault"
"""

import sys
import subprocess
import logging
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import time


class Orchestrator:
    """
    Main orchestrator for the AI Employee system (Silver Tier).

    Coordinates between watchers, Qwen Code, and the vault.
    Implements HITL approval workflow and MCP server integration.
    """

    def __init__(self, vault_path: str, check_interval: int = 30,
                 mcp_email_enabled: bool = False):
        """
        Initialize the orchestrator.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: How often to check for work (seconds)
            mcp_email_enabled: Enable MCP email server integration
        """
        self.vault_path = Path(vault_path).resolve()
        self.check_interval = check_interval
        self.mcp_email_enabled = mcp_email_enabled

        # Core folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs_dir = self.vault_path / 'Logs'
        self.briefings = self.vault_path / 'Briefings'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure all folders exist
        for folder in [self.needs_action, self.in_progress, self.done,
                       self.plans, self.pending_approval, self.approved,
                       self.rejected, self.logs_dir, self.briefings]:
            folder.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Track current task
        self.current_task_file: Optional[Path] = None

        # MCP email server path
        self.mcp_email_script = Path(__file__).parent / 'mcp_email_server.py'

        self.logger.info(f'Orchestrator initialized (Silver Tier)')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'MCP Email: {"Enabled" if mcp_email_enabled else "Disabled"}')
    
    def _setup_logging(self):
        """Configure logging."""
        log_file = self.logs_dir / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        self.logger = logging.getLogger('Orchestrator')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_pending_tasks(self) -> List[Path]:
        """
        Get list of pending tasks in Needs_Action folder.
        
        Returns:
            List of file paths sorted by creation time
        """
        if not self.needs_action.exists():
            return []
        
        files = [f for f in self.needs_action.iterdir() if f.is_file() and f.suffix == '.md']
        return sorted(files, key=lambda f: f.stat().st_ctime)
    
    def get_approved_tasks(self) -> List[Path]:
        """
        Get list of approved tasks ready for execution.
        
        Returns:
            List of file paths
        """
        if not self.approved.exists():
            return []
        
        return [f for f in self.approved.iterdir() if f.is_file() and f.suffix == '.md']
    
    def claim_task(self, task_file: Path) -> Path:
        """
        Move a task from Needs_Action to In_Progress.
        
        Args:
            task_file: Path to the task file
            
        Returns:
            New path in In_Progress
        """
        new_path = self.in_progress / task_file.name
        task_file.rename(new_path)
        self.logger.info(f'Claimed task: {task_file.name}')
        return new_path
    
    def complete_task(self, task_file: Path):
        """
        Move a completed task to Done folder.

        Args:
            task_file: Path to the completed task file
        """
        # Add completion timestamp
        content = task_file.read_text()
        if 'completed:' not in content:
            completion_marker = f'\n\n---\ncompleted: {datetime.now().isoformat()}\n'
            content += completion_marker
            task_file.write_text(content)

        # Move to Done
        new_path = self.done / task_file.name
        task_file.rename(new_path)
        self.logger.info(f'Completed task: {task_file.name}')

    def create_plan(self, task_file: Path, task_type: str) -> Path:
        """
        Create a Plan.md file for a multi-step task.

        Args:
            task_file: Path to the task file
            task_type: Type of task (email, file_drop, etc.)

        Returns:
            Path to the created plan file
        """
        timestamp = datetime.now().isoformat()
        plan_name = task_file.stem.replace(' ', '_')[:30]
        filename = f"PLAN_{plan_name}_{datetime.now().strftime('%Y%m%d')}.md"

        # Define steps based on task type
        steps = self._get_steps_for_type(task_type)

        content = f'''---
type: plan
task_file: {task_file.name}
task_name: {task_file.stem}
created: {timestamp}
status: planning
priority: normal
requires_approval: {self._requires_approval(task_type)}
---

# Plan: {task_file.stem}

## Objective

Process the task defined in {task_file.name} according to Company Handbook rules.

## Success Criteria

- [ ] Task analyzed and understood
- [ ] Required actions identified
- [ ] Approval obtained (if needed)
- [ ] Actions executed successfully
- [ ] Task moved to /Done

## Steps

{steps}

## Notes

### {timestamp[:10]}
Plan created by Orchestrator.

---
*Generated by AI Employee Orchestrator (Silver Tier)*
'''

        filepath = self.plans / filename
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created plan: {filename}')
        return filepath

    def _get_steps_for_type(self, task_type: str) -> str:
        """Get predefined steps based on task type"""
        steps_map = {
            'gmail_email': '''### Phase 1: Analysis
- [ ] Read email content and headers
- [ ] Identify sender and intent
- [ ] Check priority level
- [ ] Review Company Handbook for guidelines

### Phase 2: Response Planning
- [ ] Determine if response needed
- [ ] Draft response content
- [ ] Check if approval required

### Phase 3: Approval (if needed)
- [ ] Create approval request
- [ ] Wait for human approval
- [ ] Verify approval received

### Phase 4: Execution
- [ ] Send response or take action
- [ ] Verify success
- [ ] Log the action

### Phase 5: Completion
- [ ] Move files to /Done
- [ ] Update Dashboard''',

            'file_drop': '''### Phase 1: Analysis
- [ ] Identify file type and content
- [ ] Determine processing requirements
- [ ] Check for sensitive information

### Phase 2: Processing
- [ ] Process file content
- [ ] Extract relevant information
- [ ] Create summary or action items

### Phase 3: Action
- [ ] Execute required actions
- [ ] Create follow-up tasks if needed

### Phase 4: Completion
- [ ] Move files to /Done
- [ ] Update Dashboard''',

            'linkedin_post': '''### Phase 1: Content Review
- [ ] Review post content
- [ ] Check brand guidelines
- [ ] Verify hashtags and formatting

### Phase 2: Approval
- [ ] Create approval request in /Pending_Approval
- [ ] Wait for human approval
- [ ] Verify approval file moved to /Approved

### Phase 3: Posting
- [ ] Post to LinkedIn via Playwright
- [ ] Verify post successful
- [ ] Screenshot for records

### Phase 4: Completion
- [ ] Log the post
- [ ] Move files to /Done''',

            'default': '''### Phase 1: Analysis
- [ ] Read task file content
- [ ] Identify required actions
- [ ] Check Company Handbook rules

### Phase 2: Planning
- [ ] Create action plan
- [ ] Identify dependencies
- [ ] Determine approval needs

### Phase 3: Execution
- [ ] Execute planned actions
- [ ] Get approvals as needed
- [ ] Verify success

### Phase 4: Completion
- [ ] Move files to /Done
- [ ] Update Dashboard'''
        }

        return steps_map.get(task_type, steps_map['default'])

    def _requires_approval(self, task_type: str) -> bool:
        """Check if task type requires approval"""
        approval_types = ['email_send', 'linkedin_post', 'payment', 'whatsapp_bulk']
        return any(t in task_type for t in approval_types)
    
    def reject_task(self, task_file: Path, reason: str = ''):
        """
        Move a rejected task to Rejected folder.
        
        Args:
            task_file: Path to the task file
            reason: Reason for rejection
        """
        # Add rejection info
        content = task_file.read_text()
        rejection_marker = f'\n\n---\nrejected: {datetime.now().isoformat()}\nreason: {reason}\n'
        content += rejection_marker
        task_file.write_text(content)
        
        # Move to Rejected
        new_path = self.rejected / task_file.name
        task_file.rename(new_path)
        self.logger.warning(f'Rejected task: {task_file.name} - {reason}')
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        if not self.dashboard.exists():
            self.logger.warning('Dashboard.md not found')
            return
        
        # Count items in each folder
        pending_count = len(list(self.needs_action.glob('*.md')))
        in_progress_count = len(list(self.in_progress.glob('*.md')))
        approval_count = len(list(self.pending_approval.glob('*.md')))
        done_today = len([f for f in self.done.glob('*.md') 
                         if datetime.fromtimestamp(f.stat().st_mtime).date() == datetime.now().date()])
        
        # Get recent activity
        recent_files = sorted(self.done.glob('*.md'), key=lambda f: f.stat().st_mtime, reverse=True)[:5]
        recent_activity = []
        for f in recent_files:
            try:
                content = f.read_text()
                # Try to extract type from frontmatter
                if 'type:' in content:
                    type_line = [l for l in content.split('\n') if l.startswith('type:')][0]
                    file_type = type_line.split(':')[1].strip()
                else:
                    file_type = f.stem.split('_')[0]
                recent_activity.append(f'- [{file_type}] {f.name}')
            except:
                recent_activity.append(f'- {f.name}')
        
        # Read current dashboard
        content = self.dashboard.read_text(encoding='utf-8')
        
        # Update status section
        status_lines = [
            '| Metric | Value | Status |',
            '|--------|-------|--------|',
            f'| **Pending Actions** | {pending_count} | {"⚠️ Needs attention" if pending_count > 0 else "✅ Clear"} |',
            f'| **In Progress** | {in_progress_count} | {"🔄 Active" if in_progress_count > 0 else "⚪ Idle"} |',
            f'| **Pending Approvals** | {approval_count} | {"⚠️ Awaiting decision" if approval_count > 0 else "✅ Clear"} |',
            f'| **Completed Today** | {done_today} | {"✅ Active" if done_today > 0 else "⚪ No activity"} |',
        ]
        
        # Find and replace the status table
        lines = content.split('\n')
        in_status = False
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if '## 🎯 Quick Status' in line:
                new_lines.append(line)
                new_lines.extend(status_lines)
                in_status = True
                # Skip old status lines
                while i + 1 < len(lines) and not lines[i + 1].startswith('---'):
                    i += 1
            elif '## ✅ Recent Activity' in line:
                new_lines.append(line)
                new_lines.append('')
                new_lines.append('<!-- Last 5 completed actions -->')
                if recent_activity:
                    new_lines.extend(recent_activity)
                else:
                    new_lines.append('- No recent activity')
                in_status = False
            else:
                new_lines.append(line)
            i += 1
        
        # Update timestamp
        new_content = '\n'.join(new_lines)
        if 'last_updated:' in new_content:
            new_content = new_content.replace(
                f"last_updated: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}",
                f"last_updated: {datetime.now().isoformat()}"
            )
        
        self.dashboard.write_text(new_content, encoding='utf-8')
        self.logger.debug('Dashboard updated')
    
    def trigger_qwen(self, task_file: Path) -> bool:
        """
        Trigger Qwen Code to process a task.

        Args:
            task_file: Path to the task file in In_Progress

        Returns:
            True if Qwen was triggered successfully
        """
        self.logger.info(f'Triggering Qwen Code for: {task_file.name}')

        # Create a prompt file for Qwen
        prompt_file = self.plans / f'PROMPT_{task_file.stem}.md'
        prompt_content = f'''---
created: {datetime.now().isoformat()}
task_file: {task_file.name}
status: processing
---

# Task Processing Request

**Task File**: `{task_file.name}`

**Instructions for Qwen Code**:

1. Read the task file in /In_Progress
2. Analyze what action is needed
3. Create a plan in /Plans if multi-step
4. Execute the action or create approval request
5. Move task to /Done when complete

**Company Handbook**: Review /Company_Handbook.md for rules and guidelines.

**Current Dashboard**: See /Dashboard.md for context.
'''
        prompt_file.write_text(prompt_content, encoding='utf-8')

        # Build Qwen Code command
        # Note: This assumes Qwen Code is installed and in PATH
        cmd = [
            'qwen',
            '--prompt', f'Process the task in {task_file}. Follow the Company Handbook rules. Create a plan if needed. When complete, move the task file to /Done and update the Dashboard.',
            '--cwd', str(self.vault_path)
        ]

        try:
            # For Bronze tier, we'll use a simpler approach - just log that Qwen should be triggered
            # In a real implementation, you would call Qwen Code here
            self.logger.info(f'Would run: {" ".join(cmd)}')
            self.logger.info('NOTE: For Bronze tier, manually run Qwen Code with the vault:')
            self.logger.info(f'  qwen --cwd "{self.vault_path}"')
            self.logger.info('  Then ask Qwen to: "Process all files in /In_Progress"')

            # For now, just mark as ready for manual processing
            return True

        except FileNotFoundError:
            self.logger.error('Qwen Code not found. Please ensure Qwen Code is installed.')
            return False
        except Exception as e:
            self.logger.error(f'Error triggering Qwen: {e}')
            return False
    
    def process_approved_tasks(self):
        """Process tasks that have been approved by human."""
        approved_tasks = self.get_approved_tasks()

        for task_file in approved_tasks:
            self.logger.info(f'Processing approved task: {task_file.name}')
            
            # Parse approval file to determine action type
            content = task_file.read_text()
            action_type = self._extract_action_type(content)
            
            try:
                if action_type == 'send_email':
                    result = self._execute_email_send(task_file, content)
                elif action_type == 'linkedin_post':
                    result = self._execute_linkedin_post(task_file, content)
                else:
                    # Generic completion for other types
                    self.logger.info(f'No MCP handler for {action_type}, marking complete')
                    result = {'status': 'completed'}
                
                if result.get('status') == 'success':
                    self.complete_task(task_file)
                    self.logger.info(f'Approved task completed: {task_file.name}')
                else:
                    # Move back to needs_action on failure
                    self.logger.warning(f'Task failed: {result.get("error", "unknown")}')
                    task_file.rename(self.needs_action / task_file.name)
                    
            except Exception as e:
                self.logger.error(f'Error processing approved task: {e}')
                # Add error info to file
                error_content = f"\n\n## Error\n{str(e)}\nTimestamp: {datetime.now().isoformat()}\n"
                task_file.write_text(content + error_content)
                task_file.rename(self.needs_action / task_file.name)

    def _extract_action_type(self, content: str) -> str:
        """Extract action type from approval file"""
        # Check frontmatter for action type
        action_match = re.search(r'action:\s*(\w+)', content)
        if action_match:
            return action_match.group(1)
        
        # Check type field
        type_match = re.search(r'type:\s*(\w+)', content)
        if type_match:
            return type_match.group(1)
        
        return 'unknown'

    def _execute_email_send(self, task_file: Path, content: str) -> Dict[str, Any]:
        """
        Execute email send action via MCP.
        
        Args:
            task_file: Path to approval file
            content: File content
            
        Returns:
            Result dictionary
        """
        if not self.mcp_email_enabled:
            return {'status': 'error', 'error': 'MCP email not enabled'}
        
        # Parse email details from content
        to_match = re.search(r'to:\s*([^\n]+)', content)
        subject_match = re.search(r'subject:\s*([^\n]+)', content)
        
        # Extract email body from content section
        body_match = re.search(r'## Email Content\s*\n\s*```\s*\n([\s\S]*?)```', content)
        if not body_match:
            # Try alternative format
            body_match = re.search(r'Body[:\s]+([\s\S]*?)(?:\n\n|\Z)', content)
        
        if not all([to_match, subject_match, body_match]):
            return {'status': 'error', 'error': 'Could not parse email details'}
        
        to_email = to_match.group(1).strip()
        subject = subject_match.group(1).strip()
        body = body_match.group(1).strip()
        
        # Find attachments
        attachments = []
        attachment_match = re.search(r'attachment[:\s]+([^\n]+)', content)
        if attachment_match:
            attachment_path = Path(attachment_match.group(1).strip())
            if attachment_path.exists():
                attachments.append(str(attachment_path))
        
        # Send via MCP email server
        self.logger.info(f'Sending email to {to_email}')
        
        try:
            import subprocess
            cmd = [
                sys.executable,
                str(self.mcp_email_script),
                'send',
                '--to', to_email,
                '--subject', subject,
                '--body', body
            ]
            
            for attachment in attachments:
                cmd.extend(['--attachment', attachment])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Log success
                self._log_email_sent(to_email, subject)
                return {'status': 'success'}
            else:
                return {'status': 'error', 'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            return {'status': 'error', 'error': 'Email send timeout'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def _execute_linkedin_post(self, task_file: Path, content: str) -> Dict[str, Any]:
        """
        Execute LinkedIn post action.
        
        Args:
            task_file: Path to approval file
            content: File content
            
        Returns:
            Result dictionary
        """
        # Extract post content
        post_match = re.search(r'## Post Content\s*\n\s*```\s*\n([\s\S]*?)```', content)
        if not post_match:
            return {'status': 'error', 'error': 'Could not find post content'}
        
        post_content = post_match.group(1).strip()
        
        self.logger.info('Posting to LinkedIn...')
        
        # Call LinkedIn poster script
        linkedin_script = Path(__file__).parent / 'watchers' / 'linkedin_poster.py'
        
        try:
            # Save post to temp file for posting
            temp_file = self.vault_path / '.temp_post.txt'
            temp_file.write_text(post_content)
            
            cmd = [
                sys.executable,
                str(linkedin_script),
                str(self.vault_path),
                'post',
                str(task_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 or 'Post successful' in result.stdout:
                return {'status': 'success'}
            else:
                return {'status': 'error', 'error': result.stderr or result.stdout}
                
        except subprocess.TimeoutExpired:
            return {'status': 'error', 'error': 'LinkedIn post timeout'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def _log_email_sent(self, to: str, subject: str):
        """Log sent email to logs"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'email_sent',
            'to': to,
            'subject': subject,
            'status': 'success'
        }
        
        log_file = self.logs_dir / f'email_{datetime.now().strftime("%Y-%m-%d")}.json'
        
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                pass
        
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))
    
    def run_cycle(self):
        """Run one processing cycle."""
        self.logger.debug('Starting processing cycle')
        
        # Process approved tasks first
        self.process_approved_tasks()
        
        # Check for pending tasks
        pending_tasks = self.get_pending_tasks()
        
        if pending_tasks:
            self.logger.info(f'Found {len(pending_tasks)} pending task(s)')
            
            for task_file in pending_tasks:
                # Claim the task
                claimed = self.claim_task(task_file)

                # Trigger Qwen Code
                if self.trigger_qwen(claimed):
                    self.logger.info(f'Task {task_file.name} sent to Qwen')
                else:
                    self.logger.error(f'Failed to trigger Qwen for {task_file.name}')
                    # Move back to needs_action
                    task_file.rename(self.needs_action / task_file.name)
        else:
            self.logger.debug('No pending tasks')
        
        # Update dashboard
        self.update_dashboard()
    
    def run(self):
        """Main orchestrator loop."""
        self.logger.info('Starting Orchestrator main loop')
        self.logger.info('Press Ctrl+C to stop')
        
        try:
            while True:
                try:
                    self.run_cycle()
                except Exception as e:
                    self.logger.error(f'Error in cycle: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
    
    def run_once(self):
        """Run a single cycle (useful for testing)."""
        self.run_cycle()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <vault_path>")
        print("\nExample:")
        print('  python orchestrator.py "D:/Vault"')
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    print(f"🤖 AI Employee Orchestrator")
    print(f"==========================")
    print(f"Vault: {vault_path}")
    print(f"\nMonitoring for tasks...")
    print(f"Press Ctrl+C to stop\n")
    
    orchestrator = Orchestrator(vault_path)
    
    # Initial cycle
    print("Running initial cycle...")
    orchestrator.run_once()
    print("Initial cycle complete.")
    print("\nStarting continuous monitoring...")
    
    orchestrator.run()


if __name__ == '__main__':
    main()
