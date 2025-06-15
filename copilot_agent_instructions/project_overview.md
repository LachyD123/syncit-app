# SYNCIT_APP Project Overview

## Project Identity
- **Name**: syncit_app (formerly SYNCY V2)
- **Type**: Desktop PyQt6 Application
- **Domain**: Structural Engineering Project Management
- **Core Purpose**: Create a "digital twin" synchronization system for structural design files

## What We're Building

A sophisticated management tool that links and synchronizes:
1. **RAM Concept model files (.cpt)** - Structural analysis models
2. **PDF General Arrangement drawings** - Extracted from PDF binders
3. **ETABS structural models** (future integration)

## The Big Picture Goal

Create seamless three-way synchronization where:
- Changes propagate between file types based on user instructions
- Common "GA Numbers" link floors across all file types
- Manual coordination is eliminated, errors minimized
- Updates and calculations are tracked across the entire project ecosystem

## Core Synchronization Logic

**Linking Key**: GA Numbers (General Arrangement Numbers)
- `floor_index` in CPT files
- Calculated GA selections from PDF pages
- Floor levels in ETABS models

## Application Architecture

```
GUI Tables (3-panel layout):
├── Story Data Table (Left) - Edit floor properties for engineering scripts
├── PDF Pages Table (Middle) - Select which pages are GAs, triggers sync
└── CPT Files Table (Right) - Display CPT files and their link status
```

## Project Data Directory Structure

```
/PROJECT_ROOT/
├── RAM_CONCEPT/
│   ├── V1.0.0 - Initial Models/
│   │   └── GA_01_Level_1.cpt
│   └── ...
├── PDF_BINDERS/
│   ├── V1.0.0 - Initial GAs/
│   │   └── Structural_Drawings_R1.pdf
│   └── ...
├── ETABS_MODELS/            <-- TO BE ADDED
│   └── V1_Initial_Scheme.edb
├── pickled_project_data/
│   └── project_session.pkl
├── file_templates/
│   └── default_ram_template.cpt
├── backups/
├── excel/
└── logs/
```

## Application Source Code Structure

```
/syncit_app/  (Application Root)
├── main_app.py
├── core_logic/
│   ├── __init__.py
│   ├── cpt_manager.py
│   ├── pdf_processor.py
│   └── project_manager.py
├── data_model/
│   ├── __init__.py
│   ├── column_data.py
│   ├── floor_data.py
│   ├── pdf_properties.py
│   ├── slab_data.py
│   ├── structure_model.py
│   └── wall_data.py
├── gui/
│   ├── __init__.py
│   ├── gui_data.py
│   └── ram_api_gui.py
└── utils/
    ├── __init__.py
    └── data_type_conversions.py
```

## Long-Term Vision

1. **Phase 1**: Stable GUI with automatic linking
2. **Phase 2**: Load rundown functionality (transfer loads between levels)
3. **Phase 3**: RAM-to-PDF visualization overlay
4. **Phase 4**: PDF-to-RAM model generation (Bluebeam workflow)
5. **Phase 5**: Full ETABS integration

## Success Metrics

- Zero manual file coordination
- Real-time synchronization across all file types
- Automated load transfer calculations
- Visual verification of design consistency
- Error-free project workflow management
