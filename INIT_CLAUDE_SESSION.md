# 🚀 Initialize Claude Session - Copy & Paste This

Copy and paste this entire block at the start of each new Claude session:

```
I'm working on the GPT-OSS Local AI Knowledge Assistant project at D:\gpt-oss.

Please read these files to understand the project:
1. D:\gpt-oss\CLAUDE_CONTEXT.md - Project overview and rules
2. D:\gpt-oss\todo\workflow-v2.html - Complete workflow with I/O specs
3. D:\gpt-oss\todo\agent-roles.html - Agent responsibilities
4. D:\gpt-oss\.claude-bus\agents\current-agent.txt - Which agent you should be

Then check for any pending tasks in:
- D:\gpt-oss\.claude-bus\tasks\*.json
- D:\gpt-oss\.claude-bus\planning\*.json

Please confirm which agent role I should act as and show me current tasks.
```

## Alternative Quick Starts

### For PM-Architect Agent:
```
I am PM-Architect-Agent for GPT-OSS project at D:\gpt-oss.
Read D:\gpt-oss\CLAUDE_CONTEXT.md and check .claude-bus/planning/ for new requirements.
Create tasks in .claude-bus/tasks/ following the workflow.
```

### For Backend Agent:
```
I am Backend-Agent for GPT-OSS project at D:\gpt-oss.
Read D:\gpt-oss\CLAUDE_CONTEXT.md and check .claude-bus/tasks/ for Backend assignments.
Write code to .claude-bus/code/backend/ following standards: max 400 lines, nesting < 3.
```

### For QA Agent:
```
I am QA-Agent for GPT-OSS project at D:\gpt-oss.
Read D:\gpt-oss\CLAUDE_CONTEXT.md and check .claude-bus/code/ for code to review.
Verify quality standards and create reviews in .claude-bus/reviews/.
```

### For Super-AI-UltraThink Agent:
```
I am Super-AI-UltraThink-Agent for GPT-OSS project at D:\gpt-oss.
Read D:\gpt-oss\CLAUDE_CONTEXT.md and check .claude-bus/help/ for blocking issues.
Provide solutions for complex problems others can't solve.
```

## File References for Manual Loading

If Claude needs specific context, ask to read:

### Core Documentation
- `D:\gpt-oss\bak\goal.md` - Original project vision
- `D:\gpt-oss\bak\CHATROOM_SUMMARY.md` - Technical decisions
- `D:\gpt-oss\bak\docker-compose.yml` - Service configuration

### Workflow Files
- `D:\gpt-oss\todo\workflow-v2.html` - I/O specifications
- `D:\gpt-oss\todo\agent-roles.html` - Agent R&R

### Message Bus
- `D:\gpt-oss\.claude-bus\TASK_FORMAT.md` - Task structure
- `D:\gpt-oss\.claude-bus\agents\AGENT_PROMPTS.md` - Agent prompts

### Monitoring
- `D:\gpt-oss\monitor.ps1` - PowerShell monitoring script

## Remember:
1. **Always specify which agent you are**
2. **Check the message bus for context**
3. **Follow the workflow phases**
4. **Maintain quality standards**
5. **Log all actions to events.jsonl**

---
*This is your session initialization guide for the GPT-OSS project*