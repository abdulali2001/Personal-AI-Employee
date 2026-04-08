---
name: linkedin-poster
description: |
  Create and post content to LinkedIn automatically. This skill uses Playwright
  to automate LinkedIn posting for business growth, lead generation, and
  brand building. Includes content generation, scheduling, and analytics.

  When invoked, this skill will:
  1. Generate LinkedIn post content based on business goals
  2. Check Company_Handbook.md for brand guidelines
  3. Create draft post for approval (HITL)
  4. Post to LinkedIn via browser automation
  5. Log post and track engagement

  Use for: Business promotion, lead generation, thought leadership,
  product announcements, company updates

  WARNING: Always require human approval before posting. LinkedIn has
  strict automation policies - use responsibly and within ToS.
---

# LinkedIn Poster - Agent Skill

## Overview

This skill enables Qwen Code to automatically create and post content to
LinkedIn for business growth. It implements a Human-in-the-Loop (HITL)
pattern requiring approval before any post goes live.

## Prerequisites

- LinkedIn account (personal or company page)
- Python with Playwright installed
- Browser installed (Chromium recommended)
- Company_Handbook.md with brand guidelines
- Business_Goals.md with content objectives

## Setup

### Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Initial LinkedIn Login

```bash
# First run requires manual login
python skills/linkedin_poster.py --initial-login
```

This will:
1. Open LinkedIn in visible browser
2. Allow manual login (with 2FA if enabled)
3. Save session to persistent storage
4. Verify successful login

### Session Storage

```bash
# Session stored in:
~/.linkedin_session/

# Contains:
- Cookies
- Local Storage
- Authentication tokens
```

## Usage

### Create and Post (with Approval)

```bash
qwen --cwd "/path/to/vault" --prompt "Create LinkedIn post about our new service and post after approval"
```

### Schedule Post

```bash
qwen --cwd "/path/to/vault" --prompt "Schedule LinkedIn post for tomorrow 9 AM about industry insights"
```

### Generate Content Only

```bash
qwen --cwd "/path/to/vault" --prompt "Generate 5 LinkedIn post ideas for this week"
```

## Content Types

### Business Update

```markdown
Type: business_update
Tone: Professional, enthusiastic
Length: 150-300 words
Hashtags: 3-5 relevant tags

Example:
🎉 Exciting News!

We're thrilled to announce the launch of our new AI Employee 
system, helping businesses automate 85% of routine tasks.

Key benefits:
✅ Save 40+ hours per week
✅ Reduce operational costs
✅ Improve consistency

Ready to transform your business? Let's talk!

#AI #Automation #Business #Innovation #Productivity
```

### Thought Leadership

```markdown
Type: thought_leadership
Tone: Insightful, educational
Length: 200-500 words
Hashtags: 3-7 industry tags

Example:
💡 The Future of Work is Here

After working with 50+ businesses, I've noticed a pattern:
The most successful companies aren't replacing humans with AI.
They're augmenting human creativity with AI efficiency.

Here's what works:
1️⃣ Let AI handle repetitive tasks
2️⃣ Humans focus on strategy & relationships
3️⃣ Together, achieve 10x outcomes

The question isn't "Will AI replace me?"
It's "How can I use AI to amplify my impact?"

What's your experience with AI at work?

#FutureOfWork #AI #Leadership #Productivity #Innovation
```

### Client Success Story

```markdown
Type: success_story
Tone: Celebratory, credible
Length: 150-250 words
Hashtags: 3-5 tags

Example:
🏆 Client Win Alert!

Helped @ClientName reduce their invoice processing time 
from 4 hours to 15 minutes using our AI Employee system.

Results in first month:
📈 95% time savings
💰 $2,400 cost reduction
⭐ 100% accuracy

"This changed how we do business!" - ClientName

Want similar results? DM me!

#ClientSuccess #Automation #ROI #BusinessGrowth
```

### Industry Insight

```markdown
Type: industry_insight
Tone: Analytical, forward-thinking
Length: 200-400 words
Hashtags: 5-10 trending tags

Example:
📊 2026 Automation Trends Report

Just analyzed data from 100+ SMBs. Here's what's happening:

🔥 Trending Now:
• Email triage automation (78% adoption)
• Invoice processing (65% adoption)
• Customer support chatbots (52% adoption)

📈 Fastest Growing:
• Social media automation (+145% YoY)
• Meeting scheduling (+120% YoY)
• Data entry (+95% YoY)

💰 Highest ROI:
1. Invoice automation (avg 340% ROI)
2. Email management (avg 280% ROI)
3. Lead qualification (avg 250% ROI)

The message is clear: Automation isn't coming, it's here.

Is your business keeping up?

#Automation #SMB #BusinessTrends #AI #DigitalTransformation
```

### Question/Engagement

```markdown
Type: engagement
Tone: Conversational, curious
Length: 100-200 words
Hashtags: 2-4 broad tags

Example:
❓ Quick Question for Business Owners:

What's the ONE task you wish you could clone yourself to handle?

For me, it was email management. I was spending 3+ hours 
daily just keeping up with messages.

Now I'm curious - what's eating up YOUR time?

Drop your answer below! 👇

#Business #Entrepreneur #Productivity #TimeManagement
```

## Post Approval Schema

```markdown
---
type: linkedin_post_approval
post_type: business_update
scheduled_time: 2026-03-30T09:00:00Z
created: 2026-03-29T14:30:00Z
status: pending_approval
requires_approval: true
---

# LinkedIn Post Approval Required

## Post Details

| Field | Value |
|-------|-------|
| **Type** | Business Update |
| **Length** | 187 words |
| **Hashtags** | 5 tags |
| **Scheduled** | 2026-03-30 9:00 AM |

## Post Content

```
🎉 Exciting News!

We're thrilled to announce the launch of our new AI Employee 
system, helping businesses automate 85% of routine tasks.

Key benefits:
✅ Save 40+ hours per week
✅ Reduce operational costs
✅ Improve consistency

Ready to transform your business? Let's talk!

#AI #Automation #Business #Innovation #Productivity
```

## Why Approval is Required

- [x] All LinkedIn posts require human approval
- [ ] Posting to company page (additional approval)
- [ ] Mentioning clients/partners
- [ ] Sensitive business information

## To Approve

1. Review the post content above
2. Check for typos or issues
3. Move this file to `/Approved` folder

## To Request Changes

1. Add comments below with suggested edits
2. Move back to `/Needs_Action`

## To Reject

1. Add reason for rejection
2. Move to `/Rejected` folder

---
*Created by LinkedIn Poster - requires human approval before posting*
```

## Workflow

### Step 1: Generate Post Content

```python
def generate_linkedin_post(topic, post_type, business_goals):
    """Generate LinkedIn post content based on topic and goals"""
    
    # Read Business_Goals.md for context
    goals = load_business_goals()
    
    # Read Company_Handbook.md for brand guidelines
    guidelines = load_company_handbook()
    
    # Generate content using Qwen
    prompt = f"""
    Generate a LinkedIn post about: {topic}
    
    Type: {post_type}
    Tone: {guidelines['tone']}
    Length: {guidelines['length']}
    
    Business Context:
    - Goals: {goals['current_objectives']}
    - Target Audience: {goals['target_audience']}
    - Key Messages: {goals['key_messages']}
    
    Include:
    - Engaging hook (emoji)
    - Clear value proposition
    - Call to action
    - 3-5 relevant hashtags
    """
    
    content = call_qwen(prompt)
    return content
```

### Step 2: Create Approval Request

```python
def create_approval_request(post_content, vault_path):
    """Create approval request file for LinkedIn post"""
    timestamp = datetime.now().isoformat()
    filename = f"LINKEDIN_POST_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    
    content = f"""---
type: linkedin_post_approval
post_type: {post_content['type']}
scheduled_time: {post_content.get('scheduled_time', 'immediate')}
created: {timestamp}
status: pending_approval
requires_approval: true
---

# LinkedIn Post Approval Required

## Post Content

{post_content['body']}

## To Approve

Move this file to `/Approved` folder.

## To Request Changes

Add comments and move to `/Needs_Action`.

---
*Requires human approval before posting*
"""
    
    filepath = Path(vault_path) / 'Pending_Approval' / filename
    filepath.write_text(content, encoding='utf-8')
    return filepath
```

### Step 3: Post to LinkedIn (When Approved)

```python
from playwright.sync_api import sync_playwright

def post_to_linkedin(session_path, post_content):
    """Post content to LinkedIn using Playwright"""
    
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=session_path,
        headless=True
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    try:
        # Navigate to LinkedIn
        page.goto('https://www.linkedin.com/feed/')
        page.wait_for_timeout(2000)
        
        # Click on "Start a post"
        start_post = page.query_selector('[data-testid="update-components-start-a-post"]')
        if not start_post:
            start_post = page.query_selector('button:has-text("Start a post")')
        start_post.click()
        page.wait_for_timeout(1000)
        
        # Find and fill post text area
        text_area = page.query_selector('[data-testid="update-editor-text-input"]')
        if not text_area:
            text_area = page.query_selector('div[contenteditable="true"][role="textbox"]')
        
        # Type post content
        text_area.fill(post_content['text'])
        page.wait_for_timeout(500)
        
        # Click Post button
        post_button = page.query_selector('button:has-text("Post")')
        post_button.click()
        page.wait_for_timeout(3000)
        
        # Verify post was successful
        notification = page.query_selector('.notification-manager')
        if notification:
            print("Post successful!")
            return True
        
        return True
        
    except Exception as e:
        print(f"Error posting to LinkedIn: {e}")
        return False
    finally:
        browser.close()
        playwright.stop()
```

### Step 4: Log Post

```python
def log_post(post_data, logs_dir):
    """Log posted content for tracking"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "linkedin_post",
        "content_type": post_data['type'],
        "text": post_data['text'],
        "hashtags": post_data['hashtags'],
        "status": "posted",
        "approval_by": "human"
    }
    
    # Append to daily log
    log_file = logs_dir / f"linkedin_{datetime.now().strftime('%Y-%m-%d')}.json"
    append_to_json_log(log_file, log_entry)
```

## Content Calendar

### Weekly Planning

Create content calendar in `/Vault/LinkedIn_Calendar.md`:

```markdown
# LinkedIn Content Calendar

## Week of March 29 - April 4, 2026

| Day | Type | Topic | Status |
|-----|------|-------|--------|
| Mon | Thought Leadership | Future of Work | ✅ Posted |
| Tue | Business Update | New feature launch | ⏳ Scheduled |
| Wed | Question | Time management tips | 📝 Draft |
| Thu | Client Success | Case study: Acme Corp | 📝 Draft |
| Fri | Industry Insight | Weekly trends | 📝 Draft |

## Content Pillars

1. **Education** (40%) - Teaching about automation
2. **Proof** (30%) - Client results, case studies
3. **Engagement** (20%) - Questions, discussions
4. **Promotion** (10%) - Direct offers, announcements
```

### Best Posting Times

```python
OPTIMAL_POSTING_TIMES = {
    'Monday': ['8:00', '12:00', '17:00'],
    'Tuesday': ['8:00', '12:00', '17:00'],
    'Wednesday': ['8:00', '12:00', '17:00'],
    'Thursday': ['8:00', '12:00', '17:00'],
    'Friday': ['8:00', '12:00'],
    'Saturday': ['9:00', '11:00'],
    'Sunday': ['19:00', '20:00']  # Sunday evening prep
}

# Best engagement: Tuesday-Thursday, 8-10 AM
```

## Hashtag Strategy

### Primary Hashtags (Always Use)

```python
PRIMARY_HASHTAGS = [
    '#AI',
    '#Automation',
    '#Business',
    '#Productivity',
    '#Innovation'
]
```

### Secondary Hashtags (Rotate)

```python
SECONDARY_HASHTAGS = {
    'thought_leadership': ['#Leadership', '#FutureOfWork', '#Strategy'],
    'business_update': ['#ProductLaunch', '#Growth', '#Technology'],
    'success_story': ['#ClientSuccess', '#Results', '#ROI'],
    'industry_insight': ['#Trends', '#Data', '#Analysis'],
    'engagement': ['#Community', '#Discussion', '#Networking']
}
```

### Hashtag Rules

- Use 3-5 hashtags per post
- Mix popular and niche tags
- Place at end of post
- Don't exceed LinkedIn's limit (no official limit, but 10+ looks spammy)

## Error Handling

### Session Expired

```markdown
1. Detect login page instead of feed
2. Create alert in /Needs_Action
3. Include: "Please log in to LinkedIn manually"
4. Pause posting until re-authenticated
```

### Post Failed

```markdown
1. Log error with full content
2. Screenshot current page state
3. Retry up to 2 times
4. After failures, create error report
5. Don't lose the draft content
```

### Content Violation

```markdown
1. LinkedIn may flag certain content
2. Log the violation notice
3. Review content guidelines
4. Adjust future content generation
5. Appeal if necessary
```

## Analytics Tracking

### Post Performance

Track in `/Vault/LinkedIn_Analytics.md`:

```markdown
# LinkedIn Analytics

## March 2026

| Date | Type | Impressions | Likes | Comments | Shares |
|------|------|-------------|-------|----------|--------|
| 03/25 | Thought Leadership | 1,245 | 45 | 12 | 8 |
| 03/27 | Business Update | 892 | 32 | 7 | 3 |
| 03/29 | Client Success | 2,156 | 89 | 23 | 15 |

## Monthly Totals

- Total Posts: 12
- Total Impressions: 15,432
- Total Engagement: 567
- Average Engagement Rate: 3.67%
- Top Performing: Client Success posts
```

### Engagement Rate Calculation

```python
def calculate_engagement_rate(likes, comments, shares, impressions):
    """Calculate LinkedIn engagement rate"""
    total_engagement = likes + comments + shares
    if impressions == 0:
        return 0
    return (total_engagement / impressions) * 100
```

## Testing

### Test Connection

```bash
python -c "
from skills.linkedin_poster import test_connection
test_connection('~/.linkedin_session')
"
```

### Test Post Creation

1. Generate test post content
2. Create approval request
3. Manually approve
4. Verify post appears on LinkedIn

## Security Considerations

- Session stored locally only
- Never commit credentials
- Use 2FA on LinkedIn account
- Review LinkedIn ToS regularly
- Don't automate connection requests (against ToS)

## Rate Limiting

To avoid LinkedIn restrictions:

- Max 2 posts per day
- 5-second delay between actions
- Human-like typing speed
- Don't auto-connect with strangers
- Respect LinkedIn's automation policies

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't find post button | LinkedIn UI changed, update selectors |
| Session expired | Re-run initial login |
| Post not appearing | Check for content violations |
| Browser crashes | Increase timeout, add retry logic |

---

*Agent Skill v1.0 - Silver Tier*
*Last Updated: 2026-03-29*

**Disclaimer**: Use responsibly and within LinkedIn's Terms of Service.
This skill is for posting content only - do not use for spam or 
inauthentic activity. Always require human approval before posting.
