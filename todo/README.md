# Todo Directory - Project Documentation

This directory contains all project documentation files (HTML and Markdown) that are auto-loaded by CLAUDE.md.

## Files in this directory:
- `workflow*.html` - Workflow specifications (any version)
- `agent-roles*.html` - Agent responsibilities (any version)
- `*.md` - Any markdown documentation
- Any other `.html` or `.md` documentation files

## Naming Convention:
When updating files, use versioning in the filename:
- `workflow.html` → `workflow-v2.html` → `workflow-v3.html`
- `agent-roles.html` → `agent-roles-v2.html`

## Auto-Loading:
All `.html` and `.md` files in this directory are automatically loaded via:
```
@todo/*.html @todo/*.md
```
in CLAUDE.md

This means:
- ✅ No need to update CLAUDE.md when adding new docs
- ✅ No need to update CLAUDE.md when versioning files
- ✅ All documentation is automatically available
- ✅ Both HTML and Markdown formats supported

## Current Files:
- `workflow-v2.html` - Complete workflow with I/O specifications and stage definitions
- `agent-roles.html` - Detailed agent responsibilities and interactions
- `README.md` - This file (directory documentation)

## To Add New Documentation:
1. Create your `.html` or `.md` file in this directory
2. It will automatically be loaded on next Claude Code session
3. No configuration needed!