#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client - Example of how an AI agent calls MCP tools.

This script demonstrates how Qwen or any AI agent would communicate
with the MCP server to send emails.

Usage:
    python mcp_client.py
"""

# Fix Windows console encoding
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
from pathlib import Path

# Import the MCP server tools directly
sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import TOOLS, handle_tools_list, handle_tools_call


def main():
    """Example: AI agent calls MCP tools"""

    print("=" * 60)
    print("MCP Client - AI Agent Example")
    print("=" * 60)

    # Step 1: List available tools
    print("\n1. Listing available tools...")
    tools_result = handle_tools_list({})
    tools = tools_result["tools"]
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")

    # Step 2: Call send_email tool
    print("\n2. Calling send_email tool...")
    call_result = handle_tools_call({
        "name": "send_email",
        "arguments": {
            "to": "client@example.com",
            "subject": "Invoice #1234 - January 2026",
            "body": "Dear Client,\n\nPlease find attached your invoice for January 2026.\n\nAmount Due: $1,500.00\nDue Date: February 15, 2026\n\nBest regards,\nAI Employee",
            "cc": "accounting@company.com"
        }
    })

    # Parse and display result
    result = json.loads(call_result["content"][0]["text"])
    print(f"\n   Status:  {result['status']}")
    print(f"   Message: {result['message']}")
    print(f"   Sent at: {result['details']['sent_at']}")

    print("\n" + "=" * 60)
    print("MCP tool call successful!")
    print("=" * 60)

    # Step 3: Show how AI would use this
    print("\n3. How an AI agent uses this:")
    print("""
   AI Agent Workflow:
   +-----------------------------------------+
   | 1. AI decides to send email             |
   | 2. AI calls: tools/call                 |
   |    - name: send_email                   |
   |    - arguments: {to, subject, body}     |
   | 3. MCP server executes send_email()     |
   | 4. AI receives result                   |
   | 5. AI logs action and continues         |
   +-----------------------------------------+
""")


if __name__ == "__main__":
    main()
