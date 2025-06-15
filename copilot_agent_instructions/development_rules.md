# Development Rules & Standards

## 🚨 STRICT RULES - NEVER VIOLATE THESE 🚨

### Context Awareness Rules
1. **ALWAYS CHECK CHANGES FIRST**: Before responding to any prompt, check what has changed since last interaction
2. **GIT DIFF ANALYSIS**: Use git status and diff to understand current workspace state
3. **FILE MODIFICATION AWARENESS**: Know which files have been edited, added, or deleted
4. **BRANCH STATE CHECK**: Verify current branch and any uncommitted changes
5. **VS CODE EDITOR CONTEXT**: Check what files are currently open in VS Code editor
6. **RECENT ACTIVITY**: Consider recent file changes that might affect your response

### Required Pre-Prompt Commands
Before any code response, run these commands to understand context:
```bash
git status                           # See current changes
git diff --name-only HEAD           # List modified files
git log --oneline -3                # See recent commits
```

### Pre-Prompt Context Commands
Before starting any work, ALWAYS run these commands to gather context:

```bash
# Check current git status
git status --porcelain

# Show unstaged changes
git diff

# Show staged changes  
git diff --cached

# Show recent commits for context
git log --oneline -5

# Check which files were modified recently
git diff --name-only HEAD~1
```

### Code Response Format
1. **MODULAR ONLY**: Provide individual methods or small file updates, never entire files
2. **ONE METHOD AT A TIME**: Present each method separately with clear headings
3. **INCREMENTAL**: Allow copy-paste integration one piece at a time
4. **FILE PATH COMMENTS**: Always include `// filepath:` for code blocks

### Task Completion Rules
1. **ALWAYS UPDATE STATUS**: When completing any task, update the status in the relevant task file
2. **STATUS VALUES**: Use only Y (complete), N (not started), O (ongoing)
3. **AUTOMATIC UPDATES**: Include status updates in your response when marking tasks complete
4. **DEPENDENCY CHECK**: Verify all prerequisites are complete before starting new tasks

### Git Workflow Rules
1. **PRE-COMMIT BACKUP**: Always suggest creating a git commit before major changes
2. **COMMIT MESSAGES**: Use format: `feat: [component] - brief description` or `fix: [component] - issue resolved`
3. **ROLLBACK READY**: Include rollback instructions in responses for significant changes
4. **BRANCH STRATEGY**: Always work on main branch for this project

## GIT WORKFLOW INTEGRATION

### Before Making Changes
```bash
# Agent should suggest this command sequence
git add .
git commit -m "checkpoint: before [feature/fix description]"
git push origin main
```

### Rollback Instructions Template
When providing significant changes, always include:
```markdown
## 🔄 Rollback Instructions
If these changes cause issues, run:
```bash
git log --oneline -5  # Find the checkpoint commit
git reset --hard [checkpoint-hash]
git push --force-with-lease origin main
```

### Commit Message Standards
- **feat**: New feature implementation
- **fix**: Bug fixes
- **refactor**: Code restructuring without functionality change
- **docs**: Documentation updates
- **test**: Adding or updating tests
- **style**: Code formatting changes
- **checkpoint**: Safe state before major changes

## TASK STATUS MANAGEMENT

### When to Update Status
1. **Starting Work**: Change from N to O
2. **Completing Work**: Change from O to Y
3. **Encountering Blockers**: Add notes but keep as O
4. **Dependencies Met**: Check if blocked tasks can now start

### Status Update Format
```markdown
### Task X.X: Task Name [STATUS: Y/N/O]
**Status**: Y (Complete) / N (Not Started) / O (Ongoing)
**Last Updated**: YYYY-MM-DD
**Notes**: Any relevant completion notes or blockers
```

## Code Quality Standards
1. **PyQt6 ONLY**: Never use PyQt5 or other GUI frameworks
2. **Type Hints**: Always include type hints for parameters and return values
3. **Docstrings**: Every method needs a clear docstring explaining purpose
4. **Error Handling**: Include try-catch blocks for API calls and file operations
5. **Logging**: Use appropriate logging levels for debugging and user feedback

## Architecture Principles
1. **Separation of Concerns**: Keep GUI, business logic, and data models separate
2. **Data Model First**: Always update data models before GUI changes
3. **Thread Safety**: Use QThread for long-running operations
4. **Signal-Slot Pattern**: Use PyQt6 signals for inter-component communication

## RESPONSE FORMAT FOR TASK COMPLETION

When completing any task, your response must include:

### 1. Context Assessment (FIRST)
```markdown
## 📊 Context Assessment
**Changed Files**: [list from git status]
**Open in Editor**: [current VS Code file]
**Recent Activity**: [relevant changes that affect this response]
**Status Check**: [current branch, uncommitted changes]
```

### 2. Git Backup Command
### 3. Code Implementation  
### 4. Status Update
### 5. Testing Instructions
### 6. Rollback Instructions

## VS CODE CONTEXT DETECTION

### Standard Pre-Prompt Workflow
Every agent response should begin with context gathering:

```markdown
## 🔍 Context Analysis
```bash
# Check current workspace state
git status --porcelain
git diff --name-only HEAD~1
git log --oneline -3
```

### Analysis:
- Modified files: [list files with changes]
- Current branch: [branch name]
- Uncommitted changes: [Y/N and description]
- Recent activity: [summary of last few commits]
```
### Context Integration Rules
1. **File Change Awareness**: If files have been modified, read current state before making further changes
2. **Conflict Detection**: Check if changes conflict with planned work
3. **Progress Tracking**: Use git history to understand what work has been completed
4. **State Verification**: Ensure current state matches expected phase progression

### Workspace State Commands
```bash
# Comprehensive workspace analysis
git status --porcelain                    # Changed files summary
git diff --stat                          # Overview of changes
git diff --name-only HEAD~1              # Recently modified files  
git log --oneline --since="1 day ago"    # Recent activity
git branch --show-current                # Current branch
git show --name-only HEAD                # Last commit details
```

### Context Response Template
```markdown
## 🔍 Pre-Prompt Context Check

**Modified Files**: [list from git status]
**Recent Changes**: [summary from git diff]  
**Current Phase**: [from current_status.md]
**Last Commits**: [from git log]
**Workspace State**: [clean/dirty/conflicts]

**Context Summary**: [What this tells us about current work state]
```

## Naming Conventions
- **Classes**: PascalCase (e.g., `FloorData`, `CPTManager`)
- **Methods/Variables**: snake_case (e.g., `floor_index`, `update_table`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_ELEVATION`)
- **Files**: snake_case (e.g., `floor_data.py`, `ram_api_gui.py`)
