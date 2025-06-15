# SYNCIT App

A sophisticated desktop application for structural engineering project management that creates a "digital twin" synchronization system for structural design files.

## Overview

SYNCIT App is a PyQt6-based desktop application that links and synchronizes:
- **RAM Concept model files (.cpt)** - Structural analysis models
- **PDF General Arrangement drawings** - Extracted from PDF binders  
- **ETABS structural models** (future integration)

## Key Features

- **Three-way synchronization** between RAM Concept, PDF drawings, and ETABS models
- **GA Number linking** - Common General Arrangement Numbers link floors across all file types
- **Manual coordination elimination** - Automated updates and change propagation
- **Project tracking** - Monitor updates and calculations across the entire project ecosystem
- **Intuitive GUI** - Three-panel layout for easy file management

## Project Structure

```
syncit_app/
├── core_logic/          # Core business logic and managers
├── data_model/          # Data structures and models
├── gui/                 # User interface components
├── ram_load_rundown_tool/  # RAM Concept integration tools
├── utils/               # Utility functions
├── file_templates/      # Default templates
└── copilot_agent_instructions/  # Development documentation
```

## Requirements

- Python 3.11+
- PyQt6
- Additional dependencies listed in individual module requirements

## Getting Started

1. Clone the repository
2. Install required dependencies
3. Run `main_app.py` to start the application

## Architecture

The application uses a three-panel GUI layout:
- **Story Data Table (Left)** - Edit floor properties for engineering scripts
- **PDF Pages Table (Middle)** - Select which pages are GAs, triggers sync
- **CPT Files Table (Right)** - Display CPT files and their link status

## Development Status

This project is in active development as part of a structural engineering workflow optimization initiative.

## License

[Add your license information here]
