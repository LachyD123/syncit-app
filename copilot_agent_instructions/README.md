# GitHub Copilot Agent Instructions

## 🚨 READ THIS FIRST 🚨

Before responding to any prompt in the syncit_app project, you MUST:

### 1. Check VS Code Context Changes FIRST
- Run `git status` to see current workspace state
- Check `git diff --name-only HEAD` for modified files  
- Note currently open files in VS Code editor
- Assess how recent changes affect your response

### 2. Read Required Files in Order:
1. **[project_overview.md](project_overview.md)** - Understand what we're building
2. **[development_rules.md](development_rules.md)** - Follow these rules strictly  
3. **[current_status.md](current_status.md)** - Know where we are in development
4. **[testing_validation.md](testing_validation.md)** - Understand testing requirements
5. **Relevant task file from /tasks/** - Get specific guidance for the current phase

## How to Use This System

1. **FIRST**: Run git context commands to understand current workspace state
2. Always check `current_status.md` to understand which phase/step we're on
3. Reference the appropriate task file for detailed step-by-step guidance
4. Follow all rules in `development_rules.md` without exception
5. Use the context from the user's prompt + git state to determine what specific action to take
6. Provide modular, incremental code updates as specified in the rules

## Pre-Prompt Context Requirements

Before ANY response, gather workspace context:
```bash
git status --porcelain
git diff --name-only HEAD~1
git log --oneline -3
```

## Quick Navigation

- **Current Phase**: [Check current_status.md](current_status.md)
- **Phase 1**: [GUI & Linking](tasks/phase_1_gui_linking.md)
- **Phase 2**: [Load Rundown](tasks/phase_2_load_rundown.md)
- **Phase 3**: [Visualization](tasks/phase_3_visualization.md)
- **Phase 4**: [PDF Generation](tasks/phase_4_pdf_generation.md)

## Agent Response Format

Every response involving code changes MUST include:
1. � **Context Assessment** - What has changed since last interaction
2. �🔄 **Pre-Change Git Backup** commands
3. 📝 **Modular code implementation**
4. ✅ **Task status updates**
5. 🧪 **Testing instructions**  
6. 🔄 **Rollback instructions**
