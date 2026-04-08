---
name: plan-generator
description: |
  Generate structured plans for multi-step tasks. This skill analyzes complex
  tasks and creates detailed Plan.md files with objectives, steps, dependencies,
  and estimated timelines. Essential for the Claude reasoning loop in Silver Tier.

  When invoked, this skill will:
  1. Analyze task complexity and requirements
  2. Break down into actionable steps
  3. Identify dependencies and approvals needed
  4. Estimate time and resources
  5. Create structured Plan.md in /Plans folder

  Use for: Multi-step tasks, projects requiring coordination,
  tasks with dependencies, complex business operations
---

# Plan Generator - Agent Skill

## Overview

This skill implements the Claude reasoning loop by creating structured plans
for multi-step tasks. It transforms vague requests into actionable, tracked
work items with clear success criteria.

## When to Create a Plan

### Create Plan For:

- Tasks with 3+ distinct steps
- Tasks requiring multiple approvals
- Projects spanning multiple sessions
- Tasks with external dependencies
- Complex business operations
- Anything taking >30 minutes

### Don't Create Plan For:

- Simple single-step tasks
- Routine operations (reply to known contact)
- Auto-approved actions
- Tasks completed in one session

## Plan Schema

```markdown
---
type: plan
task_file: FILE_document_2026-03-29.md
task_name: Process client invoice request
created: 2026-03-29T10:30:00Z
status: planning | in_progress | on_hold | completed | cancelled
priority: high | normal | low
estimated_duration: 2 hours
actual_duration: (filled on completion)
requires_approval: true
approvals_needed:
  - send_email
  - generate_invoice
---

# Plan: [Task Name]

## Objective

Clear, concise statement of what this plan will accomplish.

**Example**: Process client invoice request, generate invoice document,
and send to client via email.

## Context

Background information about why this task exists and its importance.

**Example**: Client A requested their January invoice via WhatsApp on
2026-03-28. This is a standard monthly invoice for retainer services.

## Success Criteria

Measurable outcomes that indicate plan completion:

- [ ] Invoice generated with correct amount ($1,500)
- [ ] Invoice sent to client email
- [ ] Transaction logged in accounting
- [ ] Task file moved to /Done

## Steps

### Phase 1: Analysis

- [ ] Step 1.1: Review original request in WHATSAPP_client_a_2026-03-28.md
- [ ] Step 1.2: Verify client rate in /Vault/Clients/Client_A.md
- [ ] Step 1.3: Check previous invoice history
- [ ] Step 1.4: Confirm service period (January 2026)

**Exit Criteria**: All client and amount information verified

### Phase 2: Document Generation

- [ ] Step 2.1: Generate invoice PDF using template
- [ ] Step 2.2: Save to /Vault/Invoices/2026-01_Client_A.pdf
- [ ] Step 2.3: Verify PDF is readable and complete

**Exit Criteria**: Invoice PDF ready for sending

### Phase 3: Approval

- [ ] Step 3.1: Create approval request in /Pending_Approval
- [ ] Step 3.2: Wait for human approval (move to /Approved)
- [ ] Step 3.3: Verify approval before proceeding

**Exit Criteria**: Approval received

### Phase 4: Execution

- [ ] Step 4.1: Send email with invoice attachment via MCP
- [ ] Step 4.2: Verify email sent successfully
- [ ] Step 4.3: Log transaction in /Vault/Logs/

**Exit Criteria**: Email sent and logged

### Phase 5: Completion

- [ ] Step 5.1: Move all related files to /Done
- [ ] Step 5.2: Update Dashboard.md
- [ ] Step 5.3: Add completion timestamp
- [ ] Step 5.4: Generate brief summary

**Exit Criteria**: Task fully completed and documented

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| Client rate info | Information | ✅ Available | In Clients/Client_A.md |
| Invoice template | Resource | ✅ Available | In /Templates/invoice.md |
| Email MCP server | System | ✅ Available | Configured and tested |
| Human approval | External | ⏳ Pending | Required before sending |

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Client rate changed | Low | Medium | Verify with client if unsure |
| Email fails to send | Low | Medium | Retry up to 3 times, then alert |
| Approval delayed | Medium | Low | Send reminder after 24 hours |
| PDF generation fails | Low | High | Manual fallback process ready |

## Timeline

| Phase | Estimated | Start | End | Status |
|-------|-----------|-------|-----|--------|
| Analysis | 15 min | 10:30 AM | 10:45 AM | ✅ Complete |
| Document Generation | 30 min | 10:45 AM | 11:15 AM | ⏳ In Progress |
| Approval | 2-24 hours | 11:15 AM | TBD | ⏳ Pending |
| Execution | 15 min | TBD | TBD | ⏳ Not Started |
| Completion | 10 min | TBD | TBD | ⏳ Not Started |

## Resources

- /Vault/Clients/Client_A.md - Client information
- /Templates/invoice.md - Invoice template
- /Vault/Logs/ - Transaction logs
- Email MCP server - For sending

## Notes

### 2026-03-29 10:30 AM
Plan created. Client rate confirmed at $1,500/month. Standard retainer invoice.

### 2026-03-29 10:45 AM
[To be updated during execution]

---
*Generated by Plan Generator Skill*
*Last Updated: 2026-03-29T10:30:00Z*
```

## Workflow

### Step 1: Analyze Task

```python
def analyze_task(task_file, vault_path):
    """Analyze task to determine complexity and requirements"""
    content = task_file.read_text()
    
    # Extract metadata
    metadata = extract_frontmatter(content)
    
    # Count potential steps
    complexity_score = 0
    
    # Check for multiple action items
    if 'suggested_actions' in metadata:
        complexity_score += len(metadata['suggested_actions'])
    
    # Check for approval requirements
    if requires_approval(metadata.get('type', '')):
        complexity_score += 2
    
    # Check for external dependencies
    if has_external_dependencies(content):
        complexity_score += 2
    
    # Determine if plan needed
    needs_plan = complexity_score >= 3
    
    return {
        'needs_plan': needs_plan,
        'complexity': complexity_score,
        'estimated_steps': complexity_score + 1,
        'requires_approval': requires_approval(metadata.get('type', ''))
    }
```

### Step 2: Generate Plan Structure

```python
def generate_plan_structure(task_analysis, task_file, vault_path):
    """Generate structured plan based on task analysis"""
    
    # Read task content
    task_content = task_file.read_text()
    task_metadata = extract_frontmatter(task_content)
    
    # Generate objective
    objective = generate_objective(task_metadata, task_content)
    
    # Generate steps based on task type
    steps = generate_steps_for_type(task_metadata.get('type', 'general'))
    
    # Identify dependencies
    dependencies = identify_dependencies(steps, vault_path)
    
    # Estimate timeline
    timeline = estimate_timeline(steps)
    
    return {
        'objective': objective,
        'steps': steps,
        'dependencies': dependencies,
        'timeline': timeline,
        'requires_approval': task_analysis['requires_approval']
    }
```

### Step 3: Create Plan File

```python
def create_plan_file(plan_data, task_file, vault_path):
    """Create Plan.md file in /Plans folder"""
    timestamp = datetime.now().isoformat()
    safe_name = task_file.stem.replace(' ', '_')[:30]
    filename = f"PLAN_{safe_name}_{datetime.now().strftime('%Y%m%d')}.md"
    
    content = f"""---
type: plan
task_file: {task_file.name}
task_name: {plan_data['task_name']}
created: {timestamp}
status: planning
priority: {plan_data.get('priority', 'normal')}
estimated_duration: {plan_data['estimated_duration']}
requires_approval: {plan_data['requires_approval']}
---

# Plan: {plan_data['task_name']}

## Objective

{plan_data['objective']}

## Success Criteria

{format_checklist(plan_data['success_criteria'])}

## Steps

{format_steps(plan_data['steps'])}

## Dependencies

{format_dependencies_table(plan_data['dependencies'])}

## Timeline

{format_timeline_table(plan_data['timeline'])}

## Notes

### {timestamp[:10]}
Plan created.

---
*Generated by Plan Generator Skill*
"""
    
    filepath = Path(vault_path) / 'Plans' / filename
    filepath.write_text(content, encoding='utf-8')
    return filepath
```

### Step 4: Link Plan to Task

```python
def link_plan_to_task(plan_file, task_file, vault_path):
    """Add plan reference to original task file"""
    content = task_file.read_text()
    
    # Add plan link
    if '## Plan' not in content:
        content += f"""

## Plan

See: [{plan_file.name}]({plan_file})
Created: {datetime.now().isoformat()}
"""
        task_file.write_text(content)
```

### Step 5: Track Plan Progress

```python
def update_plan_status(plan_file, new_status, notes=''):
    """Update plan status and add progress notes"""
    content = plan_file.read_text()
    
    # Update status in frontmatter
    content = re.sub(
        r'status:\s*\w+',
        f'status: {new_status}',
        content
    )
    
    # Add progress note
    if notes:
        timestamp = datetime.now().isoformat()
        note_section = f"""
### {timestamp[:16]}
{notes}
"""
        if '## Notes' in content:
            content = content.replace('## Notes', f'## Notes\n{note_section}')
        else:
            content += f"\n\n## Notes\n{note_section}"
    
    plan_file.write_text(content)
```

## Plan Templates by Type

### Email Response Plan

```markdown
## Steps

### Phase 1: Analyze Request
- [ ] Read original email/message
- [ ] Identify sender and context
- [ ] Determine required response type
- [ ] Check Company_Handbook for guidelines

### Phase 2: Draft Response
- [ ] Compose response content
- [ ] Review for tone and accuracy
- [ ] Add attachments if needed

### Phase 3: Approval (if required)
- [ ] Create approval request
- [ ] Wait for approval
- [ ] Verify approval received

### Phase 4: Send
- [ ] Send via email/WhatsApp MCP
- [ ] Verify delivery
- [ ] Log communication

### Phase 5: Complete
- [ ] Move files to /Done
- [ ] Update Dashboard
```

### Payment Processing Plan

```markdown
## Steps

### Phase 1: Verify Payment Details
- [ ] Confirm payee information
- [ ] Verify amount and currency
- [ ] Check approval threshold
- [ ] Review payment purpose

### Phase 2: Create Approval Request
- [ ] Document payment details
- [ ] Add justification
- [ ] Submit for approval
- [ ] Track approval status

### Phase 3: Execute Payment
- [ ] Verify approval received
- [ ] Process via payment MCP
- [ ] Confirm transaction success
- [ ] Save transaction receipt

### Phase 4: Record & Report
- [ ] Log in accounting system
- [ ] Update payment records
- [ ] Notify relevant parties
- [ ] File documentation
```

### Content Creation Plan

```markdown
## Steps

### Phase 1: Research
- [ ] Gather topic information
- [ ] Review brand guidelines
- [ ] Identify key messages
- [ ] Research best practices

### Phase 2: Create Draft
- [ ] Generate initial content
- [ ] Review for accuracy
- [ ] Check tone alignment
- [ ] Add visuals if needed

### Phase 3: Review & Approve
- [ ] Internal review
- [ ] Create approval request
- [ ] Incorporate feedback
- [ ] Final approval

### Phase 4: Publish
- [ ] Schedule/post content
- [ ] Monitor initial engagement
- [ ] Respond to comments
- [ ] Track performance
```

## Integration with Ralph Wiggum Loop

The plan generator integrates with the Ralph Wiggum persistence pattern:

```python
def ralph_loop_check(plan_file):
    """Check if plan is complete for Ralph Wiggum loop"""
    content = plan_file.read_text()
    
    # Check all steps completed
    steps = re.findall(r'- \[([ x])\]', content)
    total_steps = len(steps)
    completed_steps = steps.count('x')
    
    if completed_steps == total_steps:
        return {'complete': True, 'ratio': 1.0}
    else:
        return {
            'complete': False,
            'ratio': completed_steps / total_steps,
            'remaining': total_steps - completed_steps
        }
```

## Error Handling

### Plan Too Complex

```markdown
1. Break into sub-plans
2. Create parent plan with child references
3. Track each sub-plan separately
4. Parent completes when all children complete
```

### Plan Blocked

```markdown
1. Update status to 'on_hold'
2. Add blocker note with details
3. Create notification for human
4. Resume when blocker resolved
```

### Plan Obsolete

```markdown
1. Update status to 'cancelled'
2. Add cancellation reason
3. Move to /Done with cancelled marker
4. Create new plan if needed
```

## Testing

### Test Plan Creation

```bash
qwen --cwd "/path/to/vault" --prompt "Create a plan for processing the invoice request in /Needs_Action"
```

### Test Plan Tracking

1. Create test plan
2. Update step statuses
3. Add progress notes
4. Verify plan completion detection

---

*Agent Skill v1.0 - Silver Tier*
*Last Updated: 2026-03-29*
