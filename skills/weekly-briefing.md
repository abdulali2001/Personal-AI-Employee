---
name: weekly-briefing
description: |
  Generate the "Monday Morning CEO Briefing" - an autonomous weekly business
  audit that summarizes revenue, completed tasks, bottlenecks, and proactive
  suggestions. This is a key Gold Tier feature that transforms the AI from
  reactive to proactive business partner.

  When invoked, this skill will:
  1. Analyze completed tasks from the week
  2. Review financial transactions
  3. Identify bottlenecks and delays
  4. Generate proactive suggestions
  5. Create CEO Briefing in /Briefings folder
  6. Schedule recurring generation

  Use for: Weekly business reviews, Monday morning briefings,
  monthly reports, quarterly audits, investor updates
---

# Weekly Briefing - Agent Skill

## Overview

This skill generates the "Monday Morning CEO Briefing" - a comprehensive
weekly business audit that provides executives with actionable insights
about business performance, completed work, and areas needing attention.

## Briefing Schedule

| Briefing | Frequency | When | Audience |
|----------|-----------|------|----------|
| Daily Standup | Daily | 7:00 AM | Quick check |
| Weekly CEO Briefing | Weekly | Monday 7:00 AM | Business owner/CEO |
| Monthly Report | Monthly | 1st of month | Stakeholders |
| Quarterly Audit | Quarterly | Start of quarter | Investors/Advisors |

## CEO Briefing Schema

```markdown
---
type: ceo_briefing
period_start: 2026-03-23
period_end: 2026-03-29
generated: 2026-03-30T07:00:00Z
status: draft | final
confidence: high | medium | low
---

# Monday Morning CEO Briefing

**Period**: March 23-29, 2026
**Generated**: Monday, March 30 at 7:00 AM
**Confidence**: High (all data sources available)

---

## Executive Summary

Strong week with revenue ahead of target. Completed 15 client deliverables
with 100% on-time rate. One bottleneck identified in invoice processing.

**Key Highlights**:
- ✅ Revenue: $4,850 (97% of $5,000 weekly target)
- ✅ Client satisfaction: 5/5 average rating
- ⚠️ Invoice processing delayed by 2 days
- 📈 New lead pipeline: 8 qualified prospects

---

## Revenue & Financials

### This Week's Revenue

| Metric | Amount | Target | Variance |
|--------|--------|--------|----------|
| **Total Revenue** | $4,850 | $5,000 | -3% |
| **Invoices Sent** | $5,200 | $5,000 | +4% |
| **Payments Received** | $4,100 | $4,500 | -9% |
| **Outstanding** | $2,350 | $2,000 | +17.5% |

### Revenue Breakdown by Client

| Client | Amount | Status |
|--------|--------|--------|
| Client A | $1,500 | ✅ Paid |
| Client B | $1,200 | ✅ Paid |
| Client C | $850 | ⏳ Pending |
| Client D | $1,300 | ⏳ Pending |

### Expenses This Week

| Category | Amount | Notes |
|----------|--------|-------|
| Software Subscriptions | $127 | 3 new tools |
| Contractor Payments | $800 | Design work |
| Marketing | $250 | LinkedIn ads |
| **Total** | **$1,177** | Within budget |

### Profit Summary

```
Revenue:    $4,850
Expenses:   $1,177
-------------------
Net Profit: $3,673 (75.7% margin)
```

---

## Completed Tasks

### Task Summary

| Category | Completed | Pending | Overdue |
|----------|-----------|---------|---------|
| Client Work | 12 | 3 | 0 |
| Administrative | 8 | 2 | 1 |
| Business Development | 5 | 4 | 0 |
| **Total** | **25** | **9** | **1** |

### Key Accomplishments

#### Client Deliverables
- [x] Client A - Website redesign (Phase 2)
- [x] Client B - Marketing automation setup
- [x] Client C - Monthly report & analysis
- [x] Client D - Strategy consultation (4 hours)

#### Business Operations
- [x] Weekly LinkedIn content (5 posts)
- [x] Email newsletter (247 subscribers)
- [x] Invoice generation & sending
- [x] Client check-in calls (8 calls)

#### Professional Development
- [x] Completed AI automation course (3 hours)
- [x] Industry webinar attendance

---

## Bottlenecks & Delays

### Identified Bottlenecks

| Issue | Impact | Root Cause | Status |
|-------|--------|------------|--------|
| Invoice processing delay | 2 days | Manual approval backlog | 🔄 Improving |
| Client C response time | 24hr delay | Awaiting client feedback | ⏳ Pending |
| Software integration | 1 week | API documentation gaps | 🔍 Investigating |

### Deep Dive: Invoice Processing Delay

**Problem**: Invoices took average 2 days to process vs. target of same-day.

**Root Cause Analysis**:
1. Approval requests sitting in Pending_Approval for 18+ hours
2. Some invoices required manual research for missing information
3. Email MCP server had 4-hour downtime on Wednesday

**Recommended Actions**:
1. Set up approval notifications (SMS for urgent)
2. Create invoice template with required fields checklist
3. Implement MCP server health monitoring

**Expected Impact**: Reduce processing time from 2 days to 4 hours

---

## Proactive Suggestions

### Cost Optimization

#### 1. Cancel Unused Software Subscription

**Finding**: Notion team plan ($15/month) - no team activity in 45 days.

**Recommendation**: 
- [ ] Downgrade to free plan
- [ ] Export important data first
- [ ] Monthly savings: $15

**Action**: Move to /Pending_Approval for decision

#### 2. Negotiate Better Rate

**Finding**: Adobe Creative Cloud at $54.99/month (standard rate).

**Recommendation**:
- [ ] Contact Adobe for business discount
- [ ] Consider annual prepay (15% savings)
- [ ] Potential savings: $100/year

**Action**: Research and present options next week

### Revenue Optimization

#### 3. Follow Up on Outstanding Invoices

**Finding**: $2,350 in outstanding invoices, 2 overdue by 15+ days.

**Recommendation**:
- [ ] Send polite reminder to Client C ($850)
- [ ] Schedule call with Client D ($1,300)
- [ ] Implement auto-reminder system

**Expected Impact**: Improve cash flow by $2,350

#### 4. Upsell Opportunity

**Finding**: Client A expressed interest in additional services.

**Recommendation**:
- [ ] Prepare proposal for Phase 3
- [ ] Estimated value: $2,000-3,000
- [ ] Timeline: Q2 2026

**Action**: Draft proposal by Friday

### Process Improvement

#### 5. Automate Weekly Reporting

**Finding**: Manual briefing generation takes 45 minutes weekly.

**Recommendation**:
- [ ] Create automated data collection
- [ ] Template standard sections
- [ ] Time savings: 30 minutes/week

**Action**: Implement in next sprint

---

## Key Metrics Dashboard

### Weekly Trends (4-Week View)

| Week | Revenue | Expenses | Profit | Tasks Done |
|------|---------|----------|--------|------------|
| W1 (Mar 2-8) | $4,200 | $1,050 | $3,150 | 22 |
| W2 (Mar 9-15) | $4,650 | $1,200 | $3,450 | 24 |
| W3 (Mar 16-22) | $5,100 | $1,100 | $4,000 | 27 |
| W4 (Mar 23-29) | $4,850 | $1,177 | $3,673 | 25 |

### Monthly Comparison

| Metric | March MTD | February Total | Change |
|--------|-----------|----------------|--------|
| Revenue | $18,800 | $17,500 | +7.4% |
| Expenses | $4,527 | $4,200 | +7.8% |
| Profit | $14,273 | $13,300 | +7.3% |
| Clients | 8 | 7 | +14% |

### KPI Scorecard

| KPI | Target | Actual | Status |
|-----|--------|--------|--------|
| Revenue/week | $5,000 | $4,850 | 🟡 97% |
| Profit margin | >70% | 75.7% | 🟢 Exceeds |
| Client satisfaction | >4.5 | 5.0 | 🟢 Exceeds |
| Task completion rate | >90% | 73.5% | 🔴 Below |
| Response time | <24hr | 18hr | 🟢 Meets |

---

## Upcoming Deadlines & Events

### This Week's Deadlines

| Date | Event | Priority | Status |
|------|-------|----------|--------|
| Apr 1 | Client E proposal due | High | 📝 In Progress |
| Apr 2 | Quarterly tax estimate | High | ⏳ Not Started |
| Apr 3 | Monthly reports (3 clients) | Medium | ⏳ Not Started |
| Apr 5 | Team strategy session | Medium | ✅ Scheduled |

### Important Dates

- **April 15**: Q1 Taxes Due
- **April 20**: Client A Project Deadline
- **April 25**: Monthly Retainer Invoices
- **May 1**: Q2 Planning Session

---

## Risk Assessment

### Current Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Client concentration (40% from 1 client) | Medium | High | Diversify client base |
| Cash flow gap (30-day payment terms) | Medium | Medium | Offer early payment discount |
| Single point of failure (no backup) | Low | High | Document processes, train VA |

### Opportunities

| Opportunity | Probability | Impact | Action Needed |
|-------------|-------------|--------|---------------|
| Client A expansion | High | $3,000 | Prepare proposal |
| Referral from Client B | Medium | $2,500 | Send referral info |
| Product launch | Low | $10,000 | Feasibility study |

---

## Action Items for CEO

### Requires Decision

1. **Cancel Notion subscription?** 
   - Save $15/month
   - Move to /Pending_Approval for decision

2. **Approve Client A Phase 3 proposal?**
   - Estimated value: $2,500
   - Timeline: 3 weeks
   - Will prepare and submit for approval

### Requires Attention

3. **Follow up on overdue invoices** ($2,350)
   - Client C: $850 (15 days overdue)
   - Client D: $1,300 (20 days overdue)

4. **Review Q1 tax estimate**
   - Due: April 15
   - Estimated: $3,200
   - Documents in /Accounting/Taxes/

### FYI Only

5. **New lead pipeline strong** - 8 qualified prospects
6. **Client satisfaction at all-time high** - 5.0/5.0
7. **LinkedIn engagement up 45%** - content strategy working

---

## Appendix: Data Sources

This briefing was generated from:

- `/Vault/Done/` - Completed task files (25 tasks)
- `/Vault/Accounting/` - Transaction records
- `/Vault/Logs/` - System activity logs
- `/Vault/Clients/` - Client information
- `/Vault/Plans/` - Active and completed plans

### Data Quality Notes

- All revenue data: ✅ Complete
- Expense tracking: ⚠️ One receipt missing (categorized as "Misc")
- Time tracking: ✅ 95% of tasks logged
- Client communications: ✅ All archived

---

*Generated by AI Employee Weekly Briefing Skill*
*Next Briefing: Monday, April 6, 2026 at 7:00 AM*
*Questions? Reply to this file or ask "Explain [section]"*
```

## Workflow

### Step 1: Collect Weekly Data

```python
def collect_weekly_data(vault_path, start_date, end_date):
    """Collect all data for the briefing period"""
    
    data = {
        'completed_tasks': [],
        'revenue': [],
        'expenses': [],
        'bottlenecks': [],
        'approvals': [],
        'communications': []
    }
    
    # Scan Done folder for completed tasks
    done_folder = Path(vault_path) / 'Done'
    for task_file in done_folder.glob('*.md'):
        task_date = get_completion_date(task_file)
        if start_date <= task_date <= end_date:
            data['completed_tasks'].append(parse_task_file(task_file))
    
    # Scan accounting records
    accounting_folder = Path(vault_path) / 'Accounting'
    for transaction_file in accounting_folder.glob('*.md'):
        transactions = parse_transactions(transaction_file, start_date, end_date)
        data['revenue'].extend([t for t in transactions if t['type'] == 'income'])
        data['expenses'].extend([t for t in transactions if t['type'] == 'expense'])
    
    # Scan logs for bottlenecks
    logs_folder = Path(vault_path) / 'Logs'
    data['bottlenecks'] = analyze_logs_for_issues(logs_folder, start_date, end_date)
    
    return data
```

### Step 2: Analyze Performance

```python
def analyze_performance(data, business_goals):
    """Analyze performance against goals"""
    
    analysis = {
        'revenue_vs_target': 0,
        'task_completion_rate': 0,
        'average_response_time': 0,
        'client_satisfaction': 0,
        'profit_margin': 0
    }
    
    # Revenue analysis
    total_revenue = sum(t['amount'] for t in data['revenue'])
    weekly_target = business_goals.get('revenue_weekly', 5000)
    analysis['revenue_vs_target'] = (total_revenue / weekly_target) * 100
    
    # Task completion
    completed = len(data['completed_tasks'])
    # Would need pending count from elsewhere
    analysis['task_completion_rate'] = calculate_completion_rate(data)
    
    # Profit margin
    total_expenses = sum(t['amount'] for t in data['expenses'])
    analysis['profit_margin'] = ((total_revenue - total_expenses) / total_revenue) * 100
    
    return analysis
```

### Step 3: Identify Bottlenecks

```python
def identify_bottlenecks(data, analysis):
    """Identify bottlenecks and areas for improvement"""
    
    bottlenecks = []
    
    # Check for approval delays
    approval_delays = analyze_approval_times(data['approvals'])
    if approval_delays['avg_hours'] > 24:
        bottlenecks.append({
            'type': 'approval_delay',
            'impact': 'Task processing delayed',
            'avg_delay': approval_delays['avg_hours'],
            'recommendation': 'Implement faster approval notifications'
        })
    
    # Check for overdue invoices
    overdue_invoices = [t for t in data['revenue'] if t['status'] == 'overdue']
    if len(overdue_invoices) > 2:
        bottlenecks.append({
            'type': 'cash_flow',
            'impact': f'${sum(i["amount"] for i in overdue_invoices)} outstanding',
            'recommendation': 'Send payment reminders, offer early payment discount'
        })
    
    # Check task completion rate
    if analysis['task_completion_rate'] < 0.8:
        bottlenecks.append({
            'type': 'productivity',
            'impact': '20%+ tasks not completed on time',
            'recommendation': 'Review workload, prioritize tasks, consider delegation'
        })
    
    return bottlenecks
```

### Step 4: Generate Suggestions

```python
def generate_suggestions(data, bottlenecks, business_goals):
    """Generate proactive suggestions for improvement"""
    
    suggestions = []
    
    # Cost optimization suggestions
    subscriptions = analyze_subscriptions(data['expenses'])
    for sub in subscriptions:
        if sub['days_inactive'] > 30:
            suggestions.append({
                'category': 'cost_optimization',
                'type': 'cancel_subscription',
                'item': sub['name'],
                'savings': sub['monthly_cost'],
                'action': f"Cancel {sub['name']} - no activity in {sub['days_inactive']} days"
            })
    
    # Revenue optimization suggestions
    outstanding = [t for t in data['revenue'] if t['status'] == 'pending']
    if sum(t['amount'] for t in outstanding) > 1000:
        suggestions.append({
            'category': 'revenue_optimization',
            'type': 'follow_up_invoices',
            'amount': sum(t['amount'] for t in outstanding),
            'action': 'Send payment reminders for outstanding invoices'
        })
    
    # Process improvement suggestions
    if bottlenecks:
        suggestions.append({
            'category': 'process_improvement',
            'type': 'address_bottlenecks',
            'action': f'Address {len(bottlenecks)} identified bottlenecks',
            'priority': 'high'
        })
    
    return suggestions
```

### Step 5: Generate Briefing Document

```python
def generate_briefing_document(analysis, data, suggestions, vault_path):
    """Generate the complete CEO Briefing document"""
    
    timestamp = datetime.now().isoformat()
    filename = f"CEO_Briefing_{datetime.now().strftime('%Y-%m-%d')}.md"
    
    content = f"""---
type: ceo_briefing
period_start: {data['start_date'].isoformat()}
period_end: {data['end_date'].isoformat()}
generated: {timestamp}
status: draft
---

# Monday Morning CEO Briefing

**Period**: {data['start_date'].strftime('%B %d')} - {data['end_date'].strftime('%d, %Y')}
**Generated**: {timestamp[:10]} at {timestamp[11:16]}

[... rest of template ...]
"""
    
    filepath = Path(vault_path) / 'Briefings' / filename
    filepath.write_text(content, encoding='utf-8')
    return filepath
```

## Scheduling

### Cron Schedule (Linux/Mac)

```bash
# Every Monday at 7:00 AM
0 7 * * 1 cd /path/to/vault && qwen --prompt "Generate weekly CEO briefing"
```

### Task Scheduler (Windows)

```xml
<!-- Weekly briefing task -->
<Trigger>
  <CalendarTrigger>
    <StartBoundary>2026-03-30T07:00:00</StartBoundary>
    <ScheduleByWeek>
      <DaysOfWeek>
        <Monday />
      </DaysOfWeek>
      <WeeksInterval>1</WeeksInterval>
    </ScheduleByWeek>
  </CalendarTrigger>
</Trigger>
```

### Python Scheduler (Alternative)

```python
from apscheduler.schedulers.blocking import Blockingscheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', day_of_week='mon', hour=7)
def weekly_briefing():
    generate_ceo_briefing()

scheduler.start()
```

## Testing

### Test Briefing Generation

```bash
qwen --cwd "/path/to/vault" --prompt "Generate test CEO briefing for last week"
```

### Verify Data Sources

1. Check `/Vault/Done/` has completed tasks
2. Check `/Vault/Accounting/` has transactions
3. Check `/Vault/Logs/` has activity logs
4. Run briefing generation
5. Verify all sections populated

---

*Agent Skill v1.0 - Silver Tier*
*Last Updated: 2026-03-29*
