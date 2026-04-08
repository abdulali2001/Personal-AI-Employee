#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple MCP Server for AI Employee

This server exposes external actions (tools) that the AI Employee can call.
It uses JSON-RPC over stdio (standard input/output) for communication.

How it works:
1. AI agent sends a JSON-RPC request to stdin
2. Server processes the request and calls the appropriate tool
3. Server writes the JSON-RPC response to stdout
4. AI agent reads the response and continues

Tools available:
- send_email: Send an email (simulated for now)

Usage:
    python mcp_server.py

Example JSON-RPC request (from AI agent):
    {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "send_email", "arguments": {"to": "user@example.com", "subject": "Hello", "body": "Test email"}}}

Example response:
    {"jsonrpc": "2.0", "id": 1, "result": {"content": [{"type": "text", "text": "Email sent successfully to user@example.com"}]}}
"""

import sys
import json
from datetime import datetime
from typing import Dict, Any


# ============================================================
# TOOLS - External actions the AI can call
# ============================================================

def send_email(to: str, subject: str, body: str, **kwargs) -> Dict[str, Any]:
    """
    Send an email to a recipient.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body text
        **kwargs: Optional extra fields (cc, bcc, attachments, etc.)

    Returns:
        Result dictionary with status and details
    """
    # TODO: Replace this with real email sending logic
    # For now, we simulate by printing to stderr (so it doesn't break stdout JSON)
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"[EMAIL SENT - simulated]", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"To:      {to}", file=sys.stderr)
    print(f"Subject: {subject}", file=sys.stderr)
    print(f"Body:    {body[:100]}{'...' if len(body) > 100 else ''}", file=sys.stderr)
    if kwargs.get('cc'):
        print(f"CC:      {kwargs['cc']}", file=sys.stderr)
    print(f"Time:    {datetime.now().isoformat()}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)

    return {
        "status": "success",
        "message": f"Email sent successfully to {to}",
        "details": {
            "to": to,
            "subject": subject,
            "sent_at": datetime.now().isoformat()
        }
    }


# ============================================================
# TOOL REGISTRY - Map tool names to functions
# ============================================================

TOOLS = {
    "send_email": {
        "name": "send_email",
        "description": "Send an email to a recipient. Use this to send messages on behalf of the AI Employee.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address (e.g., user@example.com)"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line"
                },
                "body": {
                    "type": "string",
                    "description": "Email body text"
                },
                "cc": {
                    "type": "string",
                    "description": "Optional CC email address"
                }
            },
            "required": ["to", "subject", "body"]
        },
        "function": send_email
    }
}


# ============================================================
# JSON-RPC SERVER - Handles communication protocol
# ============================================================

def handle_initialize(params: Dict) -> Dict:
    """Handle initialization request from client"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "ai-employee-mcp-server",
            "version": "1.0.0"
        }
    }


def handle_tools_list(params: Dict) -> Dict:
    """Return list of available tools"""
    tools = []
    for name, tool in TOOLS.items():
        tools.append({
            "name": tool["name"],
            "description": tool["description"],
            "inputSchema": tool["inputSchema"]
        })
    return {"tools": tools}


def handle_tools_call(params: Dict) -> Dict:
    """Call a specific tool with arguments"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    tool = TOOLS[tool_name]
    result = tool["function"](**arguments)

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, indent=2)
            }
        ]
    }


def process_request(request: Dict) -> Dict:
    """Process a JSON-RPC request and return response"""
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})

    # Route to appropriate handler
    if method == "initialize":
        result = handle_initialize(params)
    elif method == "tools/list":
        result = handle_tools_list(params)
    elif method == "tools/call":
        result = handle_tools_call(params)
    else:
        raise ValueError(f"Unknown method: {method}")

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }


def send_response(response: Dict):
    """Send JSON-RPC response to stdout"""
    # MCP uses Content-Length header for message framing
    body = json.dumps(response)
    header = f"Content-Length: {len(body)}\r\n\r\n"
    sys.stdout.write(header + body)
    sys.stdout.flush()


def read_request() -> Dict:
    """Read JSON-RPC request from stdin"""
    # Read headers until empty line
    while True:
        line = sys.stdin.readline()
        if not line:
            raise EOFError("No more input")
        if line.startswith("Content-Length:"):
            length = int(line.split(":")[1].strip())
        elif line == "\r\n" or line == "\n":
            break

    # Read body
    body = sys.stdin.read(length)
    return json.loads(body)


# ============================================================
# MAIN LOOP - Run the server
# ============================================================

def main():
    """Main entry point - runs the MCP server loop"""
    print("[AI Employee MCP Server started]", file=sys.stderr)
    print("Waiting for requests on stdin...", file=sys.stderr)
    print("Press Ctrl+C to stop\n", file=sys.stderr)

    try:
        while True:
            try:
                request = read_request()
                response = process_request(request)
                send_response(response)
            except EOFError:
                break
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                send_response(error_response)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                send_response(error_response)
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)


# ============================================================
# STANDALONE TEST MODE - Run directly to test tools
# ============================================================

if __name__ == "__main__":
    # If called with --test flag, run in test mode instead of server mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("=" * 60)
        print("MCP Server - Test Mode")
        print("=" * 60)

        # Test send_email tool directly
        print("\n[Testing send_email tool...]\n")
        result = send_email(
            to="test@example.com",
            subject="Test Email from MCP Server",
            body="This is a test email to verify the MCP server is working correctly.",
            cc="backup@example.com"
        )
        print(f"\nResult: {json.dumps(result, indent=2)}")

        # Show available tools
        print(f"\n{'='*60}")
        print("Available Tools:")
        print(f"{'='*60}")
        for name, tool in TOOLS.items():
            print(f"\n  Tool: {tool['name']}")
            print(f"  Description: {tool['description']}")
            print(f"  Required fields: {tool['inputSchema'].get('required', [])}")

        print(f"\n{'='*60}")
        print("To run as MCP server: python mcp_server.py")
        print(f"{'='*60}")
    else:
        main()
