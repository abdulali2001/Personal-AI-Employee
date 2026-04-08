#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email MCP Server - Send emails via Gmail API.

This MCP server provides email sending capabilities for the AI Employee.
It integrates with Gmail API to send emails with attachments.

Setup:
1. Create Gmail OAuth credentials (same as Gmail Watcher)
2. Place credentials.json in project directory
3. Run initial auth: python mcp_email_server.py --auth
4. Start server: python mcp_email_server.py

Usage with Qwen Code:
    Configure in Claude Code MCP settings or call directly:
    python mcp_email_server.py send --to "user@example.com" --subject "Test" --body "Hello"
"""

import sys
import os
import json
import pickle
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Gmail API libraries
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    GMAIL_AVAILABLE = True
except ImportError as e:
    GMAIL_AVAILABLE = False
    print(f"Warning: Gmail libraries not installed: {e}")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# MCP library
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Note: MCP library not installed - running in standalone mode")
    print("Install with: pip install mcp")


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly']


class EmailMCPServer:
    """
    MCP Server for sending emails via Gmail.
    """

    def __init__(self, vault_path: str, credentials_path: str = 'credentials.json'):
        """
        Initialize the Email MCP Server.

        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail OAuth credentials.json
        """
        self.vault_path = Path(vault_path)
        self.credentials_path = Path(credentials_path)
        self.token_path = self.vault_path / '.gmail_token.pickle'
        self.service = None

        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token
        if self.token_path.exists():
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f'Error loading token: {e}')
                creds = None

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f'Token refresh failed: {e}')
                    creds = None

            if not creds:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f'Credentials file not found: {self.credentials_path}\n'
                        'Please create Gmail OAuth credentials first.'
                    )

                print('Starting OAuth flow...')
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=8081, open_browser=True)

                # Save token
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
                print('OAuth completed, token saved')

        # Build service
        self.service = build('gmail', 'v1', credentials=creds)
        print('Gmail service initialized')

    def _create_message(self, sender: str, to: str, subject: str,
                       message_text: str, attachments: Optional[List[str]] = None) -> Dict:
        """
        Create a Gmail message.

        Args:
            sender: Sender email address
            to: Recipient email address
            subject: Email subject
            message_text: Email body
            attachments: Optional list of attachment file paths

        Returns:
            Encoded message dictionary
        """
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        # Add body
        msg = MIMEText(message_text, 'plain', 'utf-8')
        message.attach(msg)

        # Add attachments
        if attachments:
            for filepath in attachments:
                try:
                    part = MIMEBase('application', 'octet-stream')
                    with open(filepath, 'rb') as f:
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{Path(filepath).name}"'
                    )
                    message.attach(part)
                except Exception as e:
                    print(f'Warning: Could not attach {filepath}: {e}')

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send_email(self, to: str, subject: str, body: str,
                   attachments: Optional[List[str]] = None,
                   sender: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an email via Gmail.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            attachments: Optional list of attachment file paths
            sender: Optional sender email (defaults to authenticated account)

        Returns:
            Result dictionary with status and message_id
        """
        try:
            # Get sender email
            if not sender:
                profile = self.service.users().getProfile(userId='me').execute()
                sender = profile['emailAddress']

            # Create message
            message = self._create_message(sender, to, subject, body, attachments)

            # Send message
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            result = {
                'status': 'success',
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId'],
                'to': to,
                'subject': subject,
                'sent_at': datetime.now().isoformat()
            }

            print(f"Email sent successfully to {to}")
            return result

        except HttpError as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'error_code': e.resp.status if hasattr(e, 'resp') else 'unknown'
            }
            print(f"Error sending email: {e}")
            return error_result
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e)
            }
            print(f"Error sending email: {e}")
            return error_result

    def get_tools(self) -> List[Tool]:
        """Get MCP tools"""
        return [
            Tool(
                name='email_send',
                description='Send an email via Gmail',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'to': {
                            'type': 'string',
                            'description': 'Recipient email address'
                        },
                        'subject': {
                            'type': 'string',
                            'description': 'Email subject'
                        },
                        'body': {
                            'type': 'string',
                            'description': 'Email body text'
                        },
                        'attachments': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Optional list of attachment file paths'
                        },
                        'sender': {
                            'type': 'string',
                            'description': 'Optional sender email (defaults to authenticated account)'
                        }
                    },
                    'required': ['to', 'subject', 'body']
                }
            ),
            Tool(
                name='email_send_approval',
                description='Send an email that was approved via approval file',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'approval_file': {
                            'type': 'string',
                            'description': 'Path to the approval file in /Approved folder'
                        }
                    },
                    'required': ['approval_file']
                }
            )
        ]

    async def handle_tool(self, name: str, arguments: Dict) -> List[TextContent]:
        """Handle MCP tool calls"""
        if name == 'email_send':
            result = self.send_email(
                to=arguments.get('to'),
                subject=arguments.get('subject'),
                body=arguments.get('body'),
                attachments=arguments.get('attachments'),
                sender=arguments.get('sender')
            )
            return [TextContent(type='text', text=json.dumps(result, indent=2))]

        elif name == 'email_send_approval':
            # Read approval file
            approval_file = Path(arguments.get('approval_file'))
            if not approval_file.exists():
                return [TextContent(type='text', text=f'Error: File not found: {approval_file}')]

            content = approval_file.read_text()

            # Parse approval file (simple parsing)
            import re

            # Extract email details from frontmatter
            to_match = re.search(r'to:\s*(\S+)', content)
            subject_match = re.search(r'subject:\s*(.+)', content)

            # Extract email body from content section
            body_match = re.search(r'## Email Content\s*\n\s*```\s*\n([\s\S]*?)```', content)

            if not all([to_match, subject_match, body_match]):
                return [TextContent(type='text', text='Error: Could not parse approval file')]

            to = to_match.group(1)
            subject = subject_match.group(1).strip()
            body = body_match.group(1).strip()

            # Find attachments
            attachments = []
            attachment_match = re.search(r'attachment:\s*(\S+)', content)
            if attachment_match:
                attachment_path = Path(attachment_match.group(1))
                if attachment_path.exists():
                    attachments.append(str(attachment_path))

            result = self.send_email(to, subject, body, attachments)
            return [TextContent(type='text', text=json.dumps(result, indent=2))]

        else:
            return [TextContent(type='text', text=f'Unknown tool: {name}')]


async def run_mcp_server(vault_path: str, credentials_path: str):
    """Run the MCP server"""
    if not MCP_AVAILABLE:
        print("MCP library not installed. Run in standalone mode instead.")
        return

    server = Server('email-mcp')
    email_server = EmailMCPServer(vault_path, credentials_path)

    @server.list_tools()
    async def list_tools():
        return email_server.get_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict):
        return await email_server.handle_tool(name, arguments)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Email MCP Server - Send emails via Gmail API")
        print("\nUsage:")
        print("  python mcp_email_server.py [command] [args]")
        print("\nCommands:")
        print("  run <vault_path>     - Run as MCP server")
        print("  send [options]       - Send email (standalone)")
        print("  auth                 - Run OAuth authentication")
        print("  test                 - Test email sending")
        print("\nSend Options:")
        print("  --to <email>         - Recipient email (required)")
        print("  --subject <subject>  - Email subject (required)")
        print("  --body <body>        - Email body (required)")
        print("  --attachment <file>  - Attachment (can repeat)")
        sys.exit(0)

    command = sys.argv[1]
    vault_path = os.environ.get('VAULT_PATH', '.')

    if command == 'run':
        if len(sys.argv) < 3:
            print("Usage: python mcp_email_server.py run <vault_path>")
            sys.exit(1)
        vault_path = sys.argv[2]
        print(f"Starting Email MCP Server...")
        print(f"Vault: {vault_path}")
        import asyncio
        asyncio.run(run_mcp_server(vault_path, 'credentials.json'))

    elif command == 'send':
        # Parse arguments
        args = {}
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--to' and i + 1 < len(sys.argv):
                args['to'] = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--subject' and i + 1 < len(sys.argv):
                args['subject'] = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--body' and i + 1 < len(sys.argv):
                args['body'] = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--attachment' and i + 1 < len(sys.argv):
                if 'attachments' not in args:
                    args['attachments'] = []
                args['attachments'].append(sys.argv[i + 1])
                i += 2
            else:
                i += 1

        if not all(k in args for k in ['to', 'subject', 'body']):
            print("Error: --to, --subject, and --body are required")
            sys.exit(1)

        email_server = EmailMCPServer(vault_path, 'credentials.json')
        result = email_server.send_email(**args)
        print(json.dumps(result, indent=2))

    elif command == 'auth':
        print("Running OAuth authentication...")
        email_server = EmailMCPServer(vault_path, 'credentials.json')
        print("Authentication complete!")

    elif command == 'test':
        print("Testing email server...")
        test_email = input("Enter test email address: ")
        email_server = EmailMCPServer(vault_path, 'credentials.json')
        result = email_server.send_email(
            to=test_email,
            subject='Test Email from AI Employee',
            body='This is a test email from the AI Employee Email MCP Server.'
        )
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
