# VS Code Context Detection & Agent Workflow

This document outlines how the GitHub Copilot Agent should interpret the VS Code environment and user prompts to determine the appropriate action and safety measures.

## 🧠 Context Assessment Process

Before responding to *any* prompt, the agent MUST perform the following steps:

1.  **Check Git Status:** Run `git status` to understand the current state of the repository (clean, modified, staged, untracked).
2.  **Identify Modified Files:** Run `git diff --name-only HEAD` to get a list of files that have been modified since the last commit.
3.  **Note Open Files:** Observe which files are currently open in the VS Code editor. This indicates the user's immediate focus area.
4.  **Analyze User Prompt:** Carefully read the user's prompt to understand the requested task, the desired outcome, and any explicit instructions (like "level X", "go", "careful", etc.).
5.  **Cross-Reference:** Compare the user's request with the current git state and open files.
    - Is the user asking to modify a file that is already open or modified?
    - Does the request align with the current development phase (`current_status.md`)?
    - Does the request involve files listed in `git diff`?
6.  **Determine Change Scope:** Estimate the potential impact of the requested task:
    - How many files are likely to be affected?
    - What is the estimated number of lines of code to be added/modified?
    - Does it involve core logic, UI, data model, or utilities?
    - Does it introduce new dependencies or architectural changes?
7.  **Assess Risk Level:** Based on the change scope, determine the risk:
    - LOW: Simple bug fix, UI text change, adding a small utility function.
    - MEDIUM: Adding a new feature component, modifying existing logic in a few files.
    - HIGH: Core architecture changes, major refactoring, integrating new systems.

## 🚦 Permission Level & Safety Protocol

After assessing the context, the agent MUST determine the user's desired permission level for this specific task. This can be explicitly stated by the user or inferred from keywords.

**ALWAYS START WITH A PERMISSION CHECK PROMPT:**



🔧 TASK PERMISSIONS CHECK
==============================
What level of control should I have?

1 = READ_ONLY - Just analyze, suggest approach
2 = ASK_FIRST - Check before making changes  
3 = CATION EDIT - Add new code, don't modify existing
4 = FULL_ACCESS - Build whatever needed

Current task: [briefly describe what user wants]
What level? (1-4)
```

## Permission Level Behaviors

### Level 1 - READ_ONLY
- Analyze existing code structure
- Suggest implementation approach
- Point out relevant files
- **DO NOT** write or modify any code
- **DO NOT** create new files

### Level 2 - ASK_FIRST  
- Show what you plan to change
- Ask "Should I proceed with modifying X file?"
- Wait for explicit approval before coding
- Propose approach before implementing

### Level 3 - ASK_FIRST  
- Show what you plan to change
- Ask "Should I proceed with modifying X file?"
- Wait for explicit approval before coding
- Propose approach before implementing

### Level 3 - CAUTION EDIT SMALL CHANGES  
- Add new files, functions, classes
- Extend existing UI components
- Follow existing code patterns
- **DO NOT** modify existing working code
- **DO NOT** change core architecture

### Level 4 - FULL_ACCESS
- Build whatever is needed
- Modify existing code freely
- Add new features completely
- Optimize and refactor as needed
- Make architectural changes if required



## Git Branch Management & Rollback System

### Auto-Branch Creation Rules

**Small Changes** (No branch needed):
- Single file modifications < 50 lines
- Adding new utility functions
- UI text/styling changes
- Bug fixes affecting < 3 files
- Permission Level 3 (EXTEND_ONLY) tasks

**Medium Changes** (Create feature branch):
- Multiple file modifications
- New feature additions
- UI component additions
- Permission Level 4 tasks affecting 3+ files
- Estimated work > 30 minutes

**Large Changes** (Create feature branch + backup):
- Core architecture changes
- Database schema modifications
- Major refactoring (5+ files)
- Integration of new external libraries
- Permission Level 4 + ARCHITECTURE scope

### Branch Naming Convention
- **feature/[task-description]** - For new features
- **fix/[bug-description]** - For bug fixes
- **refactor/[component-name]** - For code cleanup
- **integrate/[library-name]** - For external integrations

### Pre-Change Actions

Before making changes, determine:
1. **Change Size**: Count files/lines affected
2. **Risk Level**: Core vs peripheral code
3. **Permission Level**: User's specified level (1-4)
4. **Rollback Need**: Can changes be easily undone?

### Git Commands Integration

```bash
# For Medium/Large changes - auto-create branch
git checkout -b feature/[description]

# For Large changes - additional safety
git tag backup-before-[description]

# Rollback commands if needed
git checkout main
git branch -D feature/[description]  # Remove failed branch
git reset --hard backup-before-[description]  # Restore from tag
```

### Safety Prompts

**Before Medium Changes:**
```
🌿 Creating feature branch: feature/[description]
This will affect [X] files. Continue? (y/n)
```

**Before Large Changes:**
```
⚠️  LARGE CHANGE DETECTED
Creating feature branch + backup tag
Files affected: [X]
Risk level: HIGH
Create safety branch? (y/n)
```

**Rollback Available:**
```
🔄 Rollback options available:
1. Undo last change only
2. Return to feature branch start  
3. Full rollback to backup tag
Choose option (1-3) or 'continue':
```

## Special Commands

If user says:
- **"level X"** = Set permission to that level for this task
- **"go"** = Use Level 4 (full access)
- **"careful"** = Use Level 2 (ask first) 
- **"extend"** = Use Level 3 (extend only)
- **"branch"** = Force create feature branch regardless of size
- **"no-branch"** = Skip branch creation for this task
- **"rollback"** = Show rollback options

## Context Usage

When user provides context files or says "use context":
1. **FIRST** - Ask for permission level
2. **ANALYZE** - Determine change size and risk
3. **BRANCH** - Create branch if needed based on rules above
4. **EXECUTE** - Perform task according to permission level
5. **VERIFY** - Confirm changes worked as expected

## Project-Specific Notes

- This is a PyQt6 desktop application (SYNCIT)
- User has 50% completed app
- Focus on practical building, not over-engineering
- Keep solutions simple and focused
- Match existing code style and patterns
- Always consider rollback options for user's peace of mind

## Never Skip Permission Check

**ALWAYS** ask for permission level first - even for simple tasks. The git branching will be determined automatically based on the permission level and change scope.

## 📝 ALL CAPS Context Recognition System

### **CRITICAL: Recognize User-Added Requirements**

When analyzing markdown files (especially project_overview.md, project_overview_v2.md, and task files), the agent MUST scan for text written in **ALL CAPS** which indicates:

#### **📋 ALL CAPS Text Types:**

1. **NEW REQUIREMENTS**
   ```
   ADD NEW FEATURE: LOAD CALCULATION WIZARD
   IMPLEMENT: AUTOMATIC BACKUP SYSTEM  
   CREATE: ADVANCED VALIDATION ENGINE
   ```

2. **URGENT TASKS**
   ```
   FIX: CRITICAL BUG IN SYNC ENGINE
   PRIORITY: UPDATE TABLE PERFORMANCE
   ASAP: ADD ERROR HANDLING TO PDF PROCESSOR
   ```

3. **ARCHITECTURAL CHANGES**
   ```
   REFACTOR: CORE_LOGIC MODULE STRUCTURE
   REDESIGN: USER INTERFACE LAYOUT
   MIGRATE: DATABASE TO NEW FORMAT
   ```

4. **INTEGRATION REQUESTS**
   ```
   INTEGRATE: ETABS API CONNECTION
   CONNECT: CLOUD STORAGE SYSTEM
   ADD API: EXTERNAL VALIDATION SERVICE
   ```

#### **🔍 Detection Rules:**

- **Scan ALL markdown files** for sentences or phrases in ALL CAPS
- **Parse context** around ALL CAPS text for specific requirements
- **Prioritize ALL CAPS content** as immediate actionable items
- **Cross-reference** with existing implementation to avoid duplicates
- **Extract specific details** like file names, method names, feature descriptions

#### **⚡ Response Protocol for ALL CAPS:**

1. **Acknowledge Detection**:
   ```
   🔍 DETECTED ALL CAPS REQUIREMENTS:
   - NEW FEATURE: [description]
   - LOCATION: [file:line]
   - PRIORITY: [High/Medium/Low]
   ```

2. **Provide Implementation Plan**:
   ```
   📋 IMPLEMENTATION APPROACH:
   1. [Step 1 description]
   2. [Step 2 description]
   3. [Expected files to modify]
   4. [Estimated effort]
   ```

3. **Request Permission Level** (standard process)

4. **Execute Based on Permission** granted

#### **📚 Example ALL CAPS Patterns to Recognize:**

```markdown
# Valid ALL CAPS Requirements:
ADD FEATURE: REAL-TIME SYNC STATUS INDICATOR
IMPLEMENT: DRAG AND DROP FILE UPLOAD
CREATE: EXPORT TO EXCEL FUNCTIONALITY
FIX: MEMORY LEAK IN PDF PROCESSING
UPDATE: GUI LAYOUT FOR BETTER UX
INTEGRATE: EXTERNAL BACKUP SERVICE
REFACTOR: ERROR HANDLING SYSTEM
OPTIMIZE: TABLE RENDERING PERFORMANCE

# Context Clues to Extract:
- Feature names and descriptions
- File or module targets
- Specific implementation details
- User experience improvements
- Performance requirements
- Integration points
```

#### **🎯 Action Priority:**
- **ALL CAPS content** = **HIGH PRIORITY** tasks
- Should be addressed **before** general improvements
- May override **current phase focus** if marked as urgent
- Should be **validated against** existing architecture