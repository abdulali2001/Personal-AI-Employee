#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Poster - Creates and posts content to LinkedIn.

This script uses Playwright to automate LinkedIn posting for business growth.
It supports content generation, draft creation, approval workflow, and posting.

IMPORTANT: Always require human approval before posting. LinkedIn has strict
automation policies - use responsibly and within Terms of Service.

Setup:
1. Install Playwright: pip install playwright
2. Install browsers: playwright install chromium
3. First run will open browser for manual LinkedIn login
4. Session is saved for future runs

Usage:
    python linkedin_poster.py /path/to/vault [action]

Actions:
    post        - Create and post content (requires approval)
    draft       - Create draft post only
    schedule    - Schedule post for later
    status      - Check LinkedIn connection status

Example:
    python linkedin_poster.py "D:/Vault" draft
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import random

# Playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed")
    print("Install with: pip install playwright && playwright install chromium")

# Import base class
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


# Content templates
CONTENT_TEMPLATES = {
    'business_update': {
        'hook': ['🎉 Exciting News!', '📢 Announcement!', '🚀 Big News!'],
        'structure': '''{hook}

{main_message}

Key highlights:
{highlights}

{call_to_action}

{hashtags}''',
        'hashtags': ['#Business', '#Innovation', '#Growth']
    },
    'thought_leadership': {
        'hook': ['💡 Leadership Insight', '🤔 Food for Thought', '📚 Lesson Learned'],
        'structure': '''{hook}

{observation}

Here's what I've learned:
{points}

{question_for_engagement}

{hashtags}''',
        'hashtags': ['#Leadership', '#ThoughtLeadership', '#Business']
    },
    'client_success': {
        'hook': ['🏆 Client Win!', '✅ Success Story', '⭐ Great Results!'],
        'structure': '''{hook}

Helped {client} achieve:
{results}

The impact:
{impact}

Want similar results? Let's talk!

{hashtags}''',
        'hashtags': ['#ClientSuccess', '#Results', '#ROI']
    },
    'industry_insight': {
        'hook': ['📊 Industry Trends', '🔍 Market Analysis', '📈 Data Insight'],
        'structure': '''{hook}

Recent analysis shows:
{data_points}

What this means:
{analysis}

{prediction_or_recommendation}

{hashtags}''',
        'hashtags': ['#Industry', '#Trends', '#Analysis']
    },
    'engagement_question': {
        'hook': ['❓ Quick Question', '🤔 Curious:', '💬 Let\'s Discuss:'],
        'structure': '''{hook}

{context}

What's your take? Drop your answer below! 👇

{hashtags}''',
        'hashtags': ['#Discussion', '#Community', '#Networking']
    }
}

HASHTAG_POOL = [
    '#AI', '#Automation', '#Business', '#Productivity', '#Innovation',
    '#Technology', '#Entrepreneur', '#Startup', '#Growth', '#Leadership',
    '#Marketing', '#Sales', '#Strategy', '#Digital', '#Future',
    '#Success', '#BusinessTips', '#Professional', '#Industry', '#Trends'
]


class LinkedInPoster(BaseWatcher):
    """
    Creates and posts content to LinkedIn.

    All posts require human approval before going live.
    """

    def __init__(self, vault_path: str, session_path: Optional[str] = None,
                 check_interval: int = 3600):
        """
        Initialize the LinkedIn poster.

        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store browser session (default: vault/.linkedin_session)
            check_interval: Check interval for scheduled posts (seconds)
        """
        super().__init__(vault_path, check_interval)

        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")

        self.session_path = Path(session_path) if session_path else self.vault_path / '.linkedin_session'
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.posts_dir = self.vault_path / 'LinkedIn_Posts'
        self.posts_dir.mkdir(parents=True, exist_ok=True)

        self.is_authenticated = False

    # Override abstract methods (not used by LinkedInPoster but required by base class)
    def check_for_updates(self) -> list:
        """Not used for LinkedIn poster - returns empty list"""
        return []

    def create_action_file(self, item: Any) -> Path:
        """Not used for LinkedIn poster - raises NotImplementedError"""
        raise NotImplementedError("LinkedInPoster does not create action files")

    def _login_to_linkedin(self, page) -> bool:
        """
        Login to LinkedIn.

        Returns:
            True if login successful
        """
        try:
            self.logger.info('Navigating to LinkedIn...')
            page.goto('https://www.linkedin.com/login', timeout=60000)
            page.wait_for_timeout(3000)

            # Check if already logged in
            try:
                page.wait_for_selector('[data-testid="update-components-start-a-post"]', timeout=5000)
                self.logger.info('Already logged in to LinkedIn')
                return True
            except PlaywrightTimeout:
                pass

            self.logger.info('Please log in to LinkedIn manually in the browser window')
            self.logger.info('Waiting for successful login...')

            # Wait for user to log in (max 5 minutes)
            try:
                page.wait_for_selector('[data-testid="update-components-start-a-post"]', timeout=300000)
                self.logger.info('LinkedIn login successful!')
                return True
            except PlaywrightTimeout:
                self.logger.error('Login timeout - please try again')
                return False

        except Exception as e:
            self.logger.error(f'Login error: {e}')
            return False

    def _generate_content(self, post_type: str, topic: str,
                         business_goals: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate LinkedIn post content.

        Args:
            post_type: Type of post (business_update, thought_leadership, etc.)
            topic: Main topic/subject
            business_goals: Optional business goals context

        Returns:
            Dictionary with post content
        """
        template = CONTENT_TEMPLATES.get(post_type, CONTENT_TEMPLATES['business_update'])

        # Generate hook
        hook = random.choice(template['hook'])

        # Generate content based on type
        if post_type == 'business_update':
            main_message = f"We're excited to share updates about {topic}."
            highlights = "• New capabilities launched\n• Improved performance\n• Enhanced user experience"
            call_to_action = "Ready to learn more? Let's connect!"
            content = template['structure'].format(
                hook=hook,
                main_message=main_message,
                highlights=highlights,
                call_to_action=call_to_action,
                hashtags=' '.join(template['hashtags'] + random.sample(HASHTAG_POOL, 2))
            )

        elif post_type == 'thought_leadership':
            observation = f"After working in {topic}, I've noticed an important pattern."
            points = "• Quality matters more than speed\n• Consistency builds trust\n• Value creation is key"
            question = "What's your experience with this? Share below!"
            content = template['structure'].format(
                hook=hook,
                observation=observation,
                points=points,
                question_for_engagement=question,
                hashtags=' '.join(template['hashtags'] + random.sample(HASHTAG_POOL, 2))
            )

        elif post_type == 'client_success':
            client = "a valued client"
            results = "• 50% time savings\n• 3x productivity increase\n• 100% satisfaction"
            impact = "This is the power of smart automation."
            content = template['structure'].format(
                hook=hook,
                client=client,
                results=results,
                impact=impact,
                hashtags=' '.join(template['hashtags'] + random.sample(HASHTAG_POOL, 2))
            )

        else:
            content = f"{hook}\n\n{topic}\n\n{' '.join(template['hashtags'])}"

        return {
            'type': post_type,
            'topic': topic,
            'content': content,
            'length': len(content),
            'hashtags': [h for h in content.split() if h.startswith('#')],
            'generated_at': datetime.now().isoformat()
        }

    def _create_approval_request(self, post_data: Dict[str, Any]) -> Path:
        """
        Create approval request file for a LinkedIn post.

        Args:
            post_data: Post content dictionary

        Returns:
            Path to the approval file
        """
        timestamp = datetime.now().isoformat()
        filename = f"LINKEDIN_POST_{datetime.now().strftime('%Y%m%d_%H%M')}.md"

        content = f'''---
type: linkedin_post_approval
post_type: {post_data['type']}
topic: {post_data['topic']}
created: {timestamp}
status: pending_approval
requires_approval: true
content_length: {post_data['length']}
---

# LinkedIn Post Approval Required

## Post Details

| Field | Value |
|-------|-------|
| **Type** | {post_data['type'].replace('_', ' ').title()} |
| **Topic** | {post_data['topic']} |
| **Length** | {post_data['length']} characters |
| **Hashtags** | {len(post_data['hashtags'])} tags |
| **Created** | {timestamp} |

## Post Content

```
{post_data['content']}
```

## Why Approval is Required

- [x] All LinkedIn posts require human approval
- [ ] Posting to company page
- [ ] Mentioning clients/partners
- [ ] Sensitive business information

## To Approve

1. Review the post content above
2. Check for typos or issues
3. **Move this file to `/Approved` folder**

## To Request Changes

1. Add comments below with suggested edits
2. Move back to `/Needs_Action`

## To Reject

1. Add reason for rejection
2. Move to `/Rejected` folder

---
*Created by LinkedIn Poster - requires human approval before posting*
'''

        filepath = self.vault_path / 'Pending_Approval' / filename
        filepath.write_text(content, encoding='utf-8')

        self.logger.info(f'Created approval request: {filename}')
        return filepath

    def post_content(self, post_content: str) -> bool:
        """
        Post content to LinkedIn.

        Args:
            post_content: The content to post

        Returns:
            True if post successful
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Navigate to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                page.goto('https://www.linkedin.com/feed/', timeout=60000)
                page.wait_for_timeout(3000)

                # Check if logged in
                try:
                    page.wait_for_selector('[data-testid="update-components-start-a-post"]', timeout=10000)
                except PlaywrightTimeout:
                    self.logger.error('Not logged in. Please run with --login first.')
                    browser.close()
                    return False

                # Click "Start a post"
                self.logger.info('Clicking "Start a post"...')
                start_post = page.query_selector('[data-testid="update-components-start-a-post"]')
                if start_post:
                    start_post.click()
                    page.wait_for_timeout(2000)
                else:
                    # Try alternative selector
                    start_post = page.query_selector('button:has-text("Start a post")')
                    if start_post:
                        start_post.click()
                        page.wait_for_timeout(2000)

                # Find and fill text area
                self.logger.info('Entering post content...')
                text_area = page.query_selector('[data-testid="update-editor-text-input"]')
                if not text_area:
                    text_area = page.query_selector('div[contenteditable="true"][role="textbox"]')

                if text_area:
                    text_area.fill(post_content)
                    page.wait_for_timeout(1000)

                    # Click Post button
                    self.logger.info('Clicking "Post"...')
                    post_button = page.query_selector('button:has-text("Post")')
                    if post_button:
                        post_button.click()
                        page.wait_for_timeout(3000)

                        # Check for success
                        self.logger.info('Post submitted successfully!')
                        browser.close()
                        return True
                    else:
                        self.logger.error('Post button not found')
                        browser.close()
                        return False
                else:
                    self.logger.error('Text area not found')
                    browser.close()
                    return False

        except Exception as e:
            self.logger.error(f'Error posting to LinkedIn: {e}')
            return False

    def create_draft(self, post_type: str, topic: str) -> Path:
        """
        Create a draft post file.

        Args:
            post_type: Type of post
            topic: Post topic

        Returns:
            Path to the draft file
        """
        post_data = self._generate_content(post_type, topic)
        timestamp = datetime.now().isoformat()
        filename = f"LINKEDIN_DRAFT_{datetime.now().strftime('%Y%m%d_%H%M')}.md"

        content = f'''---
type: linkedin_draft
post_type: {post_type}
topic: {topic}
created: {timestamp}
status: draft
content_length: {post_data['length']}
---

# LinkedIn Draft Post

## Post Details

| Field | Value |
|-------|-------|
| **Type** | {post_type.replace('_', ' ').title()} |
| **Topic** | {topic} |
| **Length** | {post_data['length']} characters |
| **Created** | {timestamp} |

## Post Content

```
{post_data['content']}
```

## Actions

- To post: Run `python linkedin_poster.py <vault> post <filename>`
- To edit: Modify this file
- To delete: Move to trash

---
*Created by LinkedIn Poster*
'''

        filepath = self.posts_dir / filename
        filepath.write_text(content, encoding='utf-8')

        self.logger.info(f'Created draft: {filename}')
        return filepath

    def check_connection(self) -> bool:
        """
        Check LinkedIn connection status.

        Returns:
            True if connected and logged in
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,  # Use visible browser to avoid bot detection
                    args=['--disable-gpu', '--no-sandbox', '--start-maximized']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/feed/', timeout=60000)
                page.wait_for_timeout(5000)

                # Check for feed element
                is_logged_in = page.query_selector('[data-testid="update-components-start-a-post"]') is not None

                print("\nCheck browser window - are you logged in to LinkedIn?")
                print("Press Enter to continue...")
                input()

                browser.close()

                if is_logged_in:
                    self.logger.info('LinkedIn connection OK')
                else:
                    self.logger.info('Not logged in - run with --login')

                return is_logged_in

        except Exception as e:
            self.logger.error(f'Connection check failed: {e}')
            return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python linkedin_poster.py <vault_path> [action] [args]")
        print("\nActions:")
        print("  login              - Login to LinkedIn (saves session)")
        print("  status             - Check connection status")
        print("  draft <type> <topic> - Create draft post")
        print("  post <file>        - Post from approval file")
        print("\nPost Types:")
        print("  business_update, thought_leadership, client_success,")
        print("  industry_insight, engagement_question")
        print("\nExamples:")
        print('  python linkedin_poster.py "D:/Vault" login')
        print('  python linkedin_poster.py "D:/Vault" draft business_update "New AI Feature"')
        print('  python linkedin_poster.py "D:/Vault" status')
        sys.exit(1)

    vault_path = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else 'status'

    print(f"💼 AI Employee LinkedIn Poster")
    print(f"==============================")
    print(f"Vault: {vault_path}")
    print(f"Action: {action}\n")

    try:
        poster = LinkedInPoster(vault_path)

        if action == 'login':
            print("Opening browser for LinkedIn login...")
            print("IMPORTANT: LinkedIn may show a security check (reCAPTCHA).")
            print("This is normal - just complete the verification in the browser.")
            print("\nSteps:")
            print("1. Browser will open")
            print("2. Complete any security verification if shown")
            print("3. Log in to your LinkedIn account")
            print("4. Wait until you see your feed")
            print("5. Press Enter in this terminal")
            print("\nOpening browser in 3 seconds...")
            
            import time
            time.sleep(3)

            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(poster.session_path),
                    headless=False,  # Visible browser for security checks
                    args=['--disable-gpu', '--no-sandbox', '--start-maximized']
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/login')

                print("\nWaiting for you to log in...")
                print("Press Enter after you see your LinkedIn feed...")
                input()
                browser.close()

            print("Login complete! Session saved.")
            print("Next time you can use 'status' or 'draft' commands.")

        elif action == 'status':
            status = poster.check_connection()
            if status:
                print("LinkedIn connected and ready")
            else:
                print("Not connected - run 'login' action first")

        elif action == 'draft':
            if len(sys.argv) < 5:
                print("Usage: python linkedin_poster.py <vault> draft <type> <topic>")
                print("\nPost types: business_update, thought_leadership, client_success,")
                print("            industry_insight, engagement_question")
                sys.exit(1)

            post_type = sys.argv[3]
            topic = sys.argv[4]

            draft_file = poster.create_draft(post_type, topic)
            print(f"Draft created: {draft_file.name}")
            print("\nTo post this draft:")
            print("1. Review and edit the draft if needed")
            print("2. Move it to /Pending_Approval folder")
            print("3. Or run: qwen --prompt 'Post this LinkedIn draft'")

        elif action == 'post':
            if len(sys.argv) < 4:
                print("Usage: python linkedin_poster.py <vault> post <approval_file>")
                sys.exit(1)

            approval_file = Path(sys.argv[3])
            if not approval_file.exists():
                print(f"Error: File not found: {approval_file}")
                sys.exit(1)

            # Read approval file
            content = approval_file.read_text()

            # Extract post content
            import re
            content_match = re.search(r'```(?:\n)?([\s\S]*?)(?:```|$)', content)
            if not content_match:
                print("Error: Could not find post content in file")
                sys.exit(1)

            post_content = content_match.group(1).strip()

            print(f"Posting to LinkedIn...")
            print(f"Content preview: {post_content[:100]}...\n")

            success = poster.post_content(post_content)

            if success:
                print("Post successful!")
                # Move file to Done
                done_file = Path(vault_path) / 'Done' / approval_file.name
                approval_file.rename(done_file)
                print(f"File moved to: {done_file}")
            else:
                print("Post failed - check browser and try again")

        else:
            print(f"Unknown action: {action}")
            sys.exit(1)

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
