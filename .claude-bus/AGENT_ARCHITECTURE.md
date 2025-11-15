# GPT-OSS Multi-Agent Architecture Guide

## Two Distinct Systems

### 1. Claude Code Agents (UI Personas)
**Location**: `C:\Users\User\.claude\agents\`
**Purpose**: Selectable agents in Claude Code's UI
**Format**: Markdown with YAML frontmatter
**Scope**: Global to all Claude Code sessions

### 2. Message Bus Roles (Project Workflow)
**Location**: `D:\gpt-oss\.claude-bus\agents\`
**Purpose**: Define roles and responsibilities within GPT-OSS project
**Format**: Detailed role specifications for multi-agent coordination
**Scope**: Project-specific workflow definitions

## How They Work Together

```
┌─────────────────────────────────────┐
│     Claude Code UI Agent Selector   │
├─────────────────────────────────────┤
│ • gpt-oss-pm-architect              │ ──┐
│ • gpt-oss-backend                   │   │
│ • gpt-oss-frontend                  │   │ Links to
│ • gpt-oss-document-rag              │   │
│ • gpt-oss-qa                        │   │
│ • super-ai-ultrathink               │ ──┘
└─────────────────────────────────────┘
                  ↓
         Selected agent loads
                  ↓
┌─────────────────────────────────────┐
│   Project Role Definition           │
│   (.claude-bus/agents/*.md)         │
├─────────────────────────────────────┤
│ • Detailed responsibilities         │
│ • Input/output specifications       │
│ • Task assignment rules             │
│ • Message bus protocols             │
│ • Quality standards                 │
└─────────────────────────────────────┘
                  ↓
          Agent operates using
                  ↓
┌─────────────────────────────────────┐
│       Message Bus System            │
│       (.claude-bus/*)               │
├─────────────────────────────────────┤
│ • planning/   - Requirements        │
│ • tasks/      - Work assignments    │
│ • contracts/  - API specs           │
│ • code/       - Development         │
│ • reviews/    - QA results          │
│ • events.jsonl - Activity log       │
└─────────────────────────────────────┘
```

## Agent Naming Convention

### Claude Code Agents (Global)
Format: `gpt-oss-[role].md`
Example: `gpt-oss-pm-architect.md`

### Message Bus Roles (Project)
Format: `[Role]-Agent.md`
Example: `PM-Architect-Agent.md`

## File Structure

```
C:\Users\User\.claude\agents\           # Claude Code UI Agents
├── gpt-oss-pm-architect.md
├── gpt-oss-backend.md
├── gpt-oss-frontend.md
├── gpt-oss-document-rag.md
├── gpt-oss-qa.md
└── super-ai-ultrathink.md            # Already exists

D:\gpt-oss\.claude-bus\agents\         # Project Role Definitions
├── AGENT_ARCHITECTURE.md              # This file
├── PM-Architect-Agent.md
├── Backend-Agent.md
├── Frontend-Agent.md
├── Document-RAG-Agent.md
├── QA-Agent.md
└── Super-AI-UltraThink-Agent.md
```

## Usage Instructions

### For Human Users
1. Open Claude Code
2. Click the agent selector dropdown
3. Choose a `gpt-oss-*` agent for the role you want Claude to assume
4. Claude will automatically load the corresponding role definition

### For Claude Sessions
1. Check `current-agent.txt` to see assigned role
2. Load role definition from `.claude-bus/agents/[Role]-Agent.md`
3. Follow role responsibilities and protocols
4. Communicate via message bus in `.claude-bus/`
5. Log all actions to `events.jsonl`

## Key Differences

| Aspect | Claude Code Agents | Message Bus Roles |
|--------|-------------------|-------------------|
| **Purpose** | UI selection | Workflow coordination |
| **Location** | ~/.claude/agents | Project/.claude-bus/agents |
| **Scope** | Global | Project-specific |
| **Format** | YAML + brief prompt | Detailed specifications |
| **Content** | When to use + core identity | Full responsibilities + protocols |
| **Persistence** | Across all projects | Within GPT-OSS only |

## Maintenance

### Adding New Agents
1. Create role definition in `.claude-bus/agents/`
2. Create corresponding Claude Code agent in `~/.claude/agents/`
3. Update this documentation
4. Test agent selection and loading

### Updating Agents
1. Update role definition in project
2. If needed, update Claude Code agent description
3. Log changes in events.jsonl
4. Notify team via message bus

## Important Notes

1. **Claude Code agents are thin wrappers** - They mainly point to the detailed role definitions
2. **Role definitions are the source of truth** - All behavior specs live in the project
3. **Agents work together via message bus** - Not direct communication
4. **Every action must be logged** - Maintain audit trail in events.jsonl
5. **Respect the separation** - Don't mix UI concerns with workflow logic