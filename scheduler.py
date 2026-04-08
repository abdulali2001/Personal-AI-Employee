#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Employee Scheduler

Automatically runs AI Employee tasks on a schedule so the system works
without manual input.

How it works:
1. Scheduler waits for the configured interval
2. When time comes, it runs mcp_client.py
3. Logs the result (success or error)
4. Waits for the next interval
5. Repeats forever

Usage:
    python scheduler.py

To stop:
    Press Ctrl + C

To change interval:
    Edit the SCHEDULE_INTERVAL_MINUTES variable below
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION - Change these values to customize the schedule
# ============================================================

# How often to run the task (in minutes)
# For testing: 1 minute
# For production: 60 minutes (1 hour)
SCHEDULE_INTERVAL_MINUTES = 1

# Path to the script to run
SCRIPT_TO_RUN = "mcp_client.py"


# ============================================================
# SCHEDULER - Main automation loop
# ============================================================

def run_task() -> bool:
    """
    Run the scheduled task (mcp_client.py).

    Returns:
        True if task succeeded, False if it failed
    """
    # Find the script path (same directory as this scheduler)
    script_path = Path(__file__).parent / SCRIPT_TO_RUN

    if not script_path.exists():
        print(f"   Error: Script not found: {script_path}")
        return False

    print(f"   Running: {SCRIPT_TO_RUN}")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   " + "-" * 40)

    try:
        # Run the script and capture output
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        # Check if it succeeded
        if result.returncode == 0:
            print("   Task completed successfully")
            return True
        else:
            print(f"   Task failed with exit code: {result.returncode}")
            if result.stderr:
                print(f"   Error output: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print("   Task timed out (5 minutes)")
        return False
    except FileNotFoundError:
        print(f"   Python not found. Make sure Python is installed.")
        return False
    except Exception as e:
        print(f"   Unexpected error: {e}")
        return False


def run_scheduler():
    """
    Main scheduler loop - runs tasks on schedule forever.
    """
    interval_seconds = SCHEDULE_INTERVAL_MINUTES * 60

    print("=" * 60)
    print("AI Employee Scheduler")
    print("=" * 60)
    print(f"Task:     {SCRIPT_TO_RUN}")
    print(f"Interval: Every {SCHEDULE_INTERVAL_MINUTES} minute(s)")
    print(f"Status:   Running (Press Ctrl+C to stop)")
    print("=" * 60)
    print()

    # Track run count
    run_count = 0
    success_count = 0
    fail_count = 0

    try:
        while True:
            # Wait for the next scheduled time
            print(f"Waiting for next run... ({SCHEDULE_INTERVAL_MINUTES} min)")
            print(f"Next run at: {(datetime.now().timestamp() + interval_seconds):.0f}")
            time.sleep(interval_seconds)

            # Time to run the task!
            run_count += 1
            print(f"\n{'='*60}")
            print(f"Run #{run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")

            # Execute the task
            success = run_task()

            # Update counters
            if success:
                success_count += 1
            else:
                fail_count += 1

            # Show summary
            print(f"\nSummary: {success_count} succeeded, {fail_count} failed out of {run_count} runs")
            print()

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Scheduler stopped by user (Ctrl+C)")
        print(f"Final summary: {success_count} succeeded, {fail_count} failed out of {run_count} runs")
        print("=" * 60)
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("Scheduler stopped.")
        sys.exit(1)


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_scheduler()
