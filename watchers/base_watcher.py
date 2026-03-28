#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher Module - Abstract base class for all AI Employee watchers.

This module provides the foundation for creating watcher scripts that monitor
various inputs (Gmail, WhatsApp, filesystems, etc.) and create actionable
files for Claude Code to process.

Usage:
    Create a new watcher by extending BaseWatcher:
    
    class MyWatcher(BaseWatcher):
        def check_for_updates(self) -> list:
            # Return list of new items to process
            pass
        
        def create_action_file(self, item) -> Path:
            # Create .md file in Needs_Action folder
            pass
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Any


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher scripts.
    
    Watchers run continuously in the background, monitoring various inputs
    and creating markdown files in the Needs_Action folder when action is needed.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: How often to check for updates (in seconds)
        """
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs_dir = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
        self.logger.info(f'Initialized {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {check_interval}s')
    
    def _setup_logging(self):
        """Configure logging to file and console."""
        log_file = self.logs_dir / f'watcher_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Setup logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items that need processing.
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Path:
        """
        Create a markdown action file for an item.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file
        """
        pass
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a standardized filename.
        
        Args:
            prefix: File type prefix (e.g., 'EMAIL', 'WHATSAPP', 'FILE')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return f'{prefix}_{unique_id}_{timestamp}.md'
    
    def create_inbox_file(self, item: Any, item_type: str, content: str) -> Path:
        """
        Create a file in the Inbox folder (raw incoming items).
        
        Args:
            item: The item to save
            item_type: Type of item (email, whatsapp, file, etc.)
            content: Markdown content for the file
            
        Returns:
            Path to the created file
        """
        filename = self.generate_filename(item_type.upper(), str(hash(str(item)))[:8])
        filepath = self.inbox / filename
        filepath.write_text(content, encoding='utf-8')
        self.logger.debug(f'Created inbox file: {filepath}')
        return filepath
    
    def promote_to_needs_action(self, inbox_file: Path) -> Path:
        """
        Move a file from Inbox to Needs_Action.
        
        Args:
            inbox_file: Path to the file in Inbox
            
        Returns:
            Path to the file in Needs_Action
        """
        new_path = self.needs_action / inbox_file.name
        inbox_file.rename(new_path)
        self.logger.debug(f'Promoted {inbox_file} to Needs_Action')
        return new_path
    
    def run(self):
        """
        Main watcher loop.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__} main loop')
        self.logger.info('Press Ctrl+C to stop')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s) to process')
                        
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                self.logger.info(f'Created action file: {filepath.name}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new items')
                        
                except Exception as e:
                    self.logger.error(f'Error in check cycle: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
        finally:
            self.logger.info(f'{self.__class__.__name__} shutting down')
    
    def run_once(self) -> int:
        """
        Run a single check cycle (useful for testing).
        
        Returns:
            Number of items processed
        """
        items = self.check_for_updates()
        count = 0
        
        for item in items:
            self.create_action_file(item)
            count += 1
        
        return count


def load_processed_ids(vault_path: str, watcher_name: str) -> set:
    """
    Load previously processed IDs from a cache file.
    
    Args:
        vault_path: Path to the vault
        watcher_name: Name of the watcher (for cache file naming)
        
    Returns:
        Set of processed IDs
    """
    cache_file = Path(vault_path) / 'Logs' / f'.processed_{watcher_name}.cache'
    
    if cache_file.exists():
        try:
            ids = set(cache_file.read_text().strip().split('\n'))
            return ids - {''}  # Remove empty strings
        except Exception:
            pass
    
    return set()


def save_processed_ids(vault_path: str, watcher_name: str, ids: set):
    """
    Save processed IDs to a cache file.
    
    Args:
        vault_path: Path to the vault
        watcher_name: Name of the watcher
        ids: Set of processed IDs to save
    """
    cache_file = Path(vault_path) / 'Logs' / f'.processed_{watcher_name}.cache'
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text('\n'.join(ids))


if __name__ == '__main__':
    # Example usage / testing
    print("BaseWatcher module - extend this class to create your own watcher")
    print("\nExample:")
    print("""
class MyWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        # Your logic here
        return []
    
    def create_action_file(self, item) -> Path:
        # Your logic here
        return Path('/path/to/file.md')
    
    if __name__ == '__main__':
        watcher = MyWatcher(vault_path='/path/to/vault')
        watcher.run()
""")
