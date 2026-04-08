#!/usr/bin/env python3
"""
Manual LinkedIn Cookie Extractor - Copy cookies from browser DevTools.

This script helps you manually paste cookies from browser DevTools.
No extension required!

Usage:
    1. Open LinkedIn in Chrome/Edge
    2. Press F12 to open DevTools
    3. Go to Application/Storage tab
    4. Copy cookies as shown in instructions
    5. Paste when this script prompts
"""

import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def manual_cookie_import(session_path: str):
    """Import cookies manually pasted by user"""
    
    print("\n" + "="*60)
    print("MANUAL COOKIE IMPORT")
    print("="*60)
    print("\nStep 1: Open LinkedIn in your browser")
    print("  → https://www.linkedin.com/feed/")
    print("\nStep 2: Make sure you're logged in")
    print("\nStep 3: Open Developer Tools")
    print("  → Press F12 OR Right-click → Inspect")
    print("\nStep 4: Go to Application tab (Chrome) or Storage tab (Edge)")
    print("\nStep 5: Expand 'Cookies' on the left")
    print("  → Click on 'https://www.linkedin.com'")
    print("\nStep 6: Copy the cookies")
    print("  → Right-click anywhere in the cookies table")
    print("  → Select 'Copy all' or 'Copy as JSON'")
    print("\nStep 7: Paste below")
    print("="*60)
    
    # Try to parse pasted cookies
    print("\nPaste cookies here (JSON format or press Enter for guided input):")
    
    try:
        cookie_input = input("> ").strip()
        
        if not cookie_input:
            # Guided input mode
            print("\nNo cookies pasted. Let's extract key cookies manually.")
            print("\nFrom the cookies table, find and copy these values:")
            print("  1. li_at")
            print("  2. JSESSIONID")
            print("  3. bcookie")
            print("  4. bscookie")
            print("\nEnter li_at value:")
            li_at = input("> ").strip()
            
            if not li_at:
                print("Error: li_at cookie is required!")
                return False
            
            cookies = [
                {
                    'name': 'li_at',
                    'value': li_at,
                    'domain': '.linkedin.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                }
            ]
        else:
            # Try to parse JSON
            try:
                cookies = json.loads(cookie_input)
                print(f"Parsed {len(cookies)} cookies")
            except json.JSONDecodeError:
                # Try tab-separated format
                cookies = []
                lines = cookie_input.strip().split('\n')
                for line in lines:
                    if '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            cookies.append({
                                'name': parts[0],
                                'value': parts[1],
                                'domain': '.linkedin.com',
                                'path': '/',
                                'httpOnly': False,
                                'secure': True
                            })
                
                if not cookies:
                    print("Could not parse cookies. Try JSON format.")
                    return False
    except Exception as e:
        print(f"Error parsing cookies: {e}")
        return False
    
    # Import to Playwright
    print("\nImporting cookies to Playwright session...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False,
            args=['--disable-gpu', '--no-sandbox']
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Add cookies
        for cookie in cookies:
            try:
                pw_cookie = {
                    'name': cookie.get('name', ''),
                    'value': cookie.get('value', ''),
                    'domain': cookie.get('domain', '.linkedin.com'),
                    'path': cookie.get('path', '/'),
                    'httpOnly': cookie.get('httpOnly', False),
                    'secure': cookie.get('secure', True),
                }
                page.context.add_cookies([pw_cookie])
            except Exception as e:
                print(f"Warning: Could not import {cookie.get('name', 'unknown')}: {e}")
        
        # Verify
        print("Verifying LinkedIn session...")
        page.goto('https://www.linkedin.com/feed/', timeout=60000)
        page.wait_for_timeout(5000)
        
        is_logged_in = page.query_selector('[data-testid="update-components-start-a-post"]') is not None
        
        if is_logged_in:
            print("\n✓ Success! LinkedIn session verified.")
            print("You can now use: python linkedin_poster.py <vault> draft")
        else:
            print("\n⚠ Could not verify login. The session may need more cookies.")
            print("Try copying all cookies from DevTools instead of just li_at.")
        
        input("\nPress Enter to close browser...")
        browser.close()
        
        return is_logged_in


def main():
    session_path = Path(__file__).parent / '.linkedin_session'
    
    print("LinkedIn Manual Cookie Importer")
    print("================================")
    print("No extension required - uses browser DevTools")
    
    success = manual_cookie_import(str(session_path))
    
    if success:
        print("\n✓ Cookie import successful!")
    else:
        print("\n✗ Cookie import failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
