#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Cookie Importer - Import cookies from browser to Playwright session.

This script imports LinkedIn cookies from a JSON file exported by a cookie editor
extension. This bypasses LinkedIn's bot detection since you're using your
regular browser's authenticated session.

Usage:
    1. Install cookie editor extension in Chrome/Edge
    2. Login to LinkedIn in your browser
    3. Export cookies as JSON (linkedin_cookies.json)
    4. Run: python linkedin_cookie_import.py linkedin_cookies.json
"""

import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def import_cookies(cookies_file: str, session_path: str):
    """Import cookies from JSON file to Playwright session"""
    
    # Load cookies
    cookies_path = Path(cookies_file)
    if not cookies_path.exists():
        print(f"Error: Cookie file not found: {cookies_file}")
        print("\nTo export cookies:")
        print("1. Install 'EditThisCookie' extension for Chrome/Edge")
        print("2. Login to LinkedIn in your browser")
        print("3. Click extension icon → Export → Export as JSON")
        print("4. Save as 'linkedin_cookies.json' in project folder")
        return False
    
    with open(cookies_path, 'r') as f:
        cookies = json.load(f)
    
    print(f"Loaded {len(cookies)} cookies from {cookies_file}")
    
    # Create browser context with cookies
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=session_path,
            headless=False,
            args=['--disable-gpu', '--no-sandbox']
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Add cookies
        print("Importing cookies...")
        for cookie in cookies:
            try:
                # Format cookie for Playwright
                pw_cookie = {
                    'name': cookie.get('name', ''),
                    'value': cookie.get('value', ''),
                    'domain': cookie.get('domain', '.linkedin.com'),
                    'path': cookie.get('path', '/'),
                    'expires': int(cookie.get('expirationDate', 0)),
                    'httpOnly': cookie.get('httpOnly', False),
                    'secure': cookie.get('secure', False),
                }
                
                # Fix domain format
                if pw_cookie['domain'] and not pw_cookie['domain'].startswith('.'):
                    pw_cookie['domain'] = '.' + pw_cookie['domain']
                
                page.context.add_cookies([pw_cookie])
            except Exception as e:
                print(f"Warning: Could not import cookie {cookie.get('name', 'unknown')}: {e}")
        
        # Verify login
        print("Verifying LinkedIn session...")
        page.goto('https://www.linkedin.com/feed/', timeout=60000)
        page.wait_for_timeout(5000)
        
        # Check if logged in
        is_logged_in = page.query_selector('[data-testid="update-components-start-a-post"]') is not None
        
        if is_logged_in:
            print("\nSuccess! LinkedIn session imported and verified.")
            print("You can now use: python linkedin_poster.py <vault> draft/post")
        else:
            print("\nWarning: Could not verify LinkedIn login.")
            print("The cookies may have expired or LinkedIn detected automation.")
            print("Try re-exporting fresh cookies from your browser.")
        
        input("\nPress Enter to close browser...")
        browser.close()
        
        return is_logged_in


def main():
    if len(sys.argv) < 2:
        print("LinkedIn Cookie Importer")
        print("========================\n")
        print("Import LinkedIn cookies from your browser to Playwright session.")
        print("\nUsage:")
        print("  python linkedin_cookie_import.py <cookies_file>")
        print("\nSteps:")
        print("1. Install 'EditThisCookie' extension for Chrome/Edge")
        print("2. Login to LinkedIn in your browser")
        print("3. Click extension icon → Export → Export as JSON")
        print("4. Save as 'linkedin_cookies.json'")
        print("5. Run: python linkedin_cookie_import.py linkedin_cookies.json")
        print("\nExample:")
        print("  python linkedin_cookie_import.py linkedin_cookies.json")
        sys.exit(1)
    
    cookies_file = sys.argv[1]
    session_path = Path(__file__).parent / '.linkedin_session'
    
    print(f"LinkedIn Cookie Importer")
    print(f"========================")
    print(f"Cookie file: {cookies_file}")
    print(f"Session path: {session_path}\n")
    
    success = import_cookies(cookies_file, str(session_path))
    
    if success:
        print("\n✓ Cookie import successful!")
    else:
        print("\n✗ Cookie import failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
