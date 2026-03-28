#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for AI Employee.

The orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process items
3. Updates the Dashboard
4. Manages task lifecycle (pending → in_progress → done)

Usage:
    python orchestrator.py /path/to/vault

Example:
    python orchestrator.py "D:/Hackathon 0/Personal -AI-Employee/AI_Employee_Vault"
"""

import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import time


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Coordinates between watchers, Claude Code, and the vault.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: How often to check for work (seconds)
        """
        self.vault_path = Path(vault_path).resolve()
        self.check_interval = check_interval
        
        # Core folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs_dir = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all folders exist
        for folder in [self.needs_action, self.in_progress, self.done, 
                       self.plans, self.pending_approval, self.approved,
                       self.rejected, self.logs_dir]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track current task
        self.current_task_file: Optional[Path] = None
        
        self.logger.info(f'Orchestrator initialized')
        self.logger.info(f'Vault: {self.vault_path}')
    
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
            
            # For Bronze tier, approved tasks are just moved to Done
            # In higher tiers, actual actions (emails, payments) would be executed here
            
            self.complete_task(task_file)
            self.logger.info(f'Approved task completed: {task_file.name}')
    
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
