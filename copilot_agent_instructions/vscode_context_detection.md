# VS Code Context Detection Guide

## 🔍 Critical: Context Before Code

**MANDATORY**: Every agent response must begin with workspace context analysis to understand what has changed in VS Code since the last interaction.

## Standard Context Detection Workflow

### Step 1: Gather Git State
```bash
# Essential commands to run first
git status --porcelain          # Modified/staged files
git diff --name-only HEAD~1     # Recently changed files
git log --oneline -3            # Recent commits
git branch --show-current       # Current branch
```

### Step 2: Analyze Changes
```bash
# Detailed analysis commands
git diff --stat                 # Summary of changes
git diff                        # Detailed unstaged changes
git diff --cached               # Detailed staged changes
git show --stat HEAD            # What was in last commit
```

### Step 3: Workspace State Assessment
```bash
# Check for conflicts or issues
git status                      # Full status
ls -la syncit_app/             # Directory structure check
```

## Context Response Template

Every agent response should start with:

```markdown
## 🔍 VS Code Context Analysis

### Git Workspace State:
- **Modified Files**: [files from git status --porcelain]
- **Recently Changed**: [files from git diff --name-only HEAD~1]
- **Branch**: [current branch]
- **Staged Changes**: [Y/N - what's staged]
- **Uncommitted Changes**: [Y/N - what's modified]

### Recent Activity:
[Summary from git log --oneline -3]

### Workspace Assessment:
- **Phase Status**: [check current_status.md]
- **Last Work**: [what was completed based on git history]
- **Current State**: [ready for work/conflicts/issues]

### Context Summary:
[Brief summary of what this tells us about where we are and what needs to be done]
```

## Context Integration Rules

### When Files Are Modified:
1. **Read Current State**: Use read_file tool to see current content
2. **Understand Changes**: Compare with expected state from instructions
3. **Assess Impact**: How do changes affect planned work?
4. **Adjust Approach**: Modify implementation based on current state

### When Files Are Staged:
1. **Review Staged Changes**: Understand what's ready to commit
2. **Check Dependencies**: Are prerequisites met for next tasks?
3. **Update Status**: Reflect completed work in task status
4. **Plan Next Steps**: What should happen after commit

### When Conflicts Exist:
1. **Identify Conflicts**: What's conflicting and why
2. **Resolve Strategy**: How to resolve without losing work
3. **Backup Plan**: Create checkpoint before resolution
4. **Recovery Path**: Clear rollback instructions

## Context-Aware Response Examples

### Example 1: Clean Workspace
```markdown
## 🔍 VS Code Context Analysis
- **Modified Files**: None
- **Recently Changed**: syncit_app/README.md (last commit)
- **Workspace Assessment**: Clean, ready for new work
- **Phase Status**: Foundation setup required
```

### Example 2: Work in Progress
```markdown
## 🔍 VS Code Context Analysis
- **Modified Files**: syncit_app/data_model/floor_data.py (modified)
- **Recently Changed**: Multiple files in last 2 commits
- **Workspace Assessment**: Foundation work partially complete
- **Phase Status**: Can proceed with Task 1.1 once floor_data.py is committed
```

### Example 3: Conflicts Detected
```markdown
## 🔍 VS Code Context Analysis
- **Modified Files**: 5 files with uncommitted changes
- **Workspace Assessment**: Need to resolve state before proceeding
- **Recommendation**: Create checkpoint commit before new work
```

## Context Commands Reference

### Quick State Check:
```bash
git status --porcelain && git log --oneline -2
```

### Detailed Analysis:
```bash
git status
git diff --stat
git log --oneline --since="1 hour ago"
```

### File-Specific Context:
```bash
git diff [filename]               # What changed in specific file
git log --oneline -3 -- [filename]  # Recent commits affecting file
```

### Branch Context:
```bash
git branch -v                     # Branch info with last commits
git log --graph --oneline -5      # Visual commit history
```

## Integration with Task Management

### Before Starting Tasks:
1. Check context to verify prerequisites are met
2. Ensure no conflicting changes exist
3. Confirm current phase status matches workspace state

### During Task Work:
1. Regular context checks to avoid conflicts
2. Monitor file changes that might affect current work
3. Update task status based on actual file state

### After Completing Tasks:
1. Verify workspace state matches expected completion
2. Update status files to reflect actual progress
3. Create appropriate commit with context-aware message

This context detection system ensures agents always have full awareness of VS Code workspace state and can make informed decisions about how to proceed with development work.
