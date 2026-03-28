#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

This watcher monitors a designated "drop folder" for incoming files.
When a new file is detected, it creates an action file in the Needs_Action
folder for Claude Code to process.

This is the simplest watcher to set up and is perfect for Bronze Tier.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder

Example:
    python filesystem_watcher.py "D:/Hackathon 0/Personal -AI-Employee/AI_Employee_Vault" "D:/DropFolder"
"""

import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import base class
from base_watcher import BaseWatcher

# Watchdog library for file system events
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. Using polling fallback.")
    print("Install with: pip install watchdog")


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events in the drop folder."""
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        super().__init__()
        self.watcher = watcher
    
    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        
        try:
            self.watcher.process_new_file(Path(event.src_path))
        except Exception as e:
            self.watcher.logger.error(f'Error processing new file: {e}')


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files.
    
    When a file is added, it:
    1. Copies the file to the vault
    2. Creates a metadata markdown file in Needs_Action
    3. Logs the action
    """
    
    def __init__(self, vault_path: str, drop_folder_path: str, check_interval: int = 5):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            drop_folder_path: Path to the folder to monitor for new files
            check_interval: How often to check for new files (seconds)
        """
        super().__init__(vault_path, check_interval)
        
        self.drop_folder = Path(drop_folder_path).resolve()
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Files directory inside vault
        self.files_dir = self.vault_path / 'Files'
        self.files_dir.mkdir(parents=True, exist_ok=True)
        
        # Track file hashes to detect new files
        self.known_files: dict = {}
        self._load_known_files()
        
        self.logger.info(f'Drop folder: {self.drop_folder}')
    
    def _load_known_files(self):
        """Load hashes of already-known files to avoid re-processing."""
        cache_file = self.logs_dir / '.known_files.cache'
        
        if cache_file.exists():
            try:
                for line in cache_file.read_text().strip().split('\n'):
                    if '|' in line:
                        filepath, filehash = line.split('|', 1)
                        self.known_files[filepath] = filehash
                self.logger.debug(f'Loaded {len(self.known_files)} known files')
            except Exception as e:
                self.logger.error(f'Error loading known files: {e}')
    
    def _save_known_files(self):
        """Save known files cache."""
        cache_file = self.logs_dir / '.known_files.cache'
        content = '\n'.join(f'{k}|{v}' for k, v in self.known_files.items())
        cache_file.write_text(content)
    
    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f'Error hashing file: {e}')
            return ''
    
    def _is_new_file(self, filepath: Path) -> bool:
        """Check if a file is new (not previously processed)."""
        filepath_str = str(filepath)
        
        # Check if we know this file
        if filepath_str in self.known_files:
            return False
        
        # Check if file exists in vault already
        vault_copy = self.files_dir / filepath.name
        if vault_copy.exists():
            return False
        
        return True
    
    def _mark_as_known(self, filepath: Path, file_hash: str):
        """Mark a file as processed."""
        self.known_files[str(filepath)] = file_hash
        self._save_known_files()
    
    def process_new_file(self, filepath: Path):
        """
        Process a newly detected file.
        
        Args:
            filepath: Path to the new file
        """
        if not filepath.exists():
            self.logger.warning(f'File no longer exists: {filepath}')
            return
        
        # Check if it's really new
        if not self._is_new_file(filepath):
            self.logger.debug(f'Skipping known file: {filepath.name}')
            return
        
        # Calculate hash
        file_hash = self._get_file_hash(filepath)
        
        # Copy to vault
        dest = self.files_dir / filepath.name
        try:
            shutil.copy2(filepath, dest)
            self.logger.info(f'Copied {filepath.name} to vault')
        except Exception as e:
            self.logger.error(f'Error copying file: {e}')
            return
        
        # Create action file
        self.create_action_file({
            'source_path': filepath,
            'vault_path': dest,
            'name': filepath.name,
            'size': filepath.stat().st_size,
            'hash': file_hash
        })
        
        # Mark as known
        self._mark_as_known(filepath, file_hash)
    
    def check_for_updates(self) -> list:
        """
        Check drop folder for new files.
        
        Returns:
            List of new file info dictionaries
        """
        new_files = []
        
        if not self.drop_folder.exists():
            self.logger.warning(f'Drop folder does not exist: {self.drop_folder}')
            return []
        
        # Scan all files in drop folder
        for filepath in self.drop_folder.iterdir():
            if filepath.is_file() and self._is_new_file(filepath):
                new_files.append({
                    'source_path': filepath,
                    'vault_path': self.files_dir / filepath.name,
                    'name': filepath.name,
                    'size': filepath.stat().st_size,
                    'hash': self._get_file_hash(filepath)
                })
        
        return new_files
    
    def create_action_file(self, item: dict) -> Path:
        """
        Create a markdown action file for a new file drop.
        
        Args:
            item: File info dictionary
            
        Returns:
            Path to the created action file
        """
        timestamp = datetime.now().isoformat()
        filename = self.generate_filename('FILE', item['name'].replace(' ', '_')[:20])
        
        content = f'''---
type: file_drop
original_name: {item['name']}
size: {item['size']}
size_human: {self._human_readable_size(item['size'])}
received: {timestamp}
status: pending
source_hash: {item['hash']}
---

# File Drop for Processing

A new file has been dropped for processing.

## File Details

| Property | Value |
|----------|-------|
| **Name** | {item['name']} |
| **Size** | {self._human_readable_size(item['size'])} |
| **Received** | {timestamp} |
| **Location** | `/Files/{item['name']}` |

## Original Location

```
{item['source_path']}
```

## Suggested Actions

- [ ] Review file content
- [ ] Determine required action
- [ ] Process and move to /Done
- [ ] Update Dashboard

## Notes

<!-- AI Employee: Add your analysis and actions here -->

---
*Created by FileSystemWatcher*
'''
        
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f'Created action file: {filepath.name}')
        return filepath
    
    def _human_readable_size(self, size: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.1f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'
    
    def run_with_watchdog(self):
        """Run using watchdog library for real-time monitoring."""
        if not WATCHDOG_AVAILABLE:
            self.logger.warning('watchdog not available, falling back to polling')
            self.run()
            return
        
        self.logger.info('Starting FileSystemWatcher with watchdog (real-time)')
        
        event_handler = DropFolderHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        observer.start()
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info('Watcher stopped by user')
        
        observer.join()


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python filesystem_watcher.py <vault_path> <drop_folder>")
        print("\nExample:")
        print('  python filesystem_watcher.py "D:/Vault" "D:/DropFolder"')
        sys.exit(1)
    
    vault_path = sys.argv[1]
    drop_folder = sys.argv[2]
    
    print(f"📁 AI Employee File System Watcher")
    print(f"==================================")
    print(f"Vault: {vault_path}")
    print(f"Drop Folder: {drop_folder}")
    print(f"\nWatching for new files...")
    print(f"Press Ctrl+C to stop\n")
    
    watcher = FileSystemWatcher(vault_path, drop_folder)
    
    # Use watchdog if available for real-time monitoring
    if WATCHDOG_AVAILABLE:
        watcher.run_with_watchdog()
    else:
        watcher.run()


if __name__ == '__main__':
    main()
