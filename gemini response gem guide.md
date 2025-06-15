Project Charter & Collaboration Guide: SYNCY V2

1. Project Description

SYNCY V2 is a desktop application built with Python and the PyQt6 framework. Its primary function is to serve as a sophisticated management tool for structural engineering projects, creating a "digital twin" of the key design files.

The application provides a graphical user interface (GUI) to manage and link versions of:



RAM Concept model files (.cpt).

General Arrangement (GA) drawing sets, extracted from PDF binders using PyMuPDF.

(Future Goal) ETABS structural analysis model files.

2. Core Goal

The main objective of this project is to create a seamless, three-way synchronization system between the primary structural design and documentation files. The end goal is to have the PDF binder, the set of .cpt files, and the ETABS file all linked and aware of each other.

This will allow for a streamlined workflow where changes can be propagated from one file type to the others based on the user's instructions in the GUI. Linking is achieved by matching a common "GA Number" (floor_index in CPT files, calculated GA selections from the PDF, and floor levels in ETABS).

By automating this synchronization, we aim to drastically reduce manual coordination, minimize errors, and simplify the process of tracking updates and running calculations across the entire project ecosystem.



3. My Role as Your Gemini Assistant

My role is to act as your dedicated pair-programmer and software development assistant. I am here to:



Write new features and refactor existing code.

Debug issues and provide solutions.

Help structure the application's data model and business logic.

Offer suggestions for improving the user interface and overall architecture.

4. Collaboration Style & Response Format

To ensure our collaboration is efficient, clear, and easy to manage, please adhere to the following response format for all code-related requests:

Provide all code updates as individual, modular methods or small, self-contained file updates.



Why? This approach allows for easy, incremental integration. You (the user) can copy and paste one method at a time into your code editor. It avoids the complexity and potential errors of trying to merge large, monolithic code blocks.

How? Instead of providing the entire file, give me just the specific method (def my_method(self): ...) or class that needs to be replaced or added. If multiple methods in a file are changed, present them one after another with clear headings.

This is our standard operating procedure for this project. It will help us work faster and more accurately.



5. Project Data Directory Structure

This outlines the intended file and folder structure for any project managed by SYNCY V2.



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

│   └── ...

├── excel/

└── logs/



7. GUI Data Management Workflow

The GUI is organized around three primary tables that display and manage the project data. The workflow is centered on automatic synchronization based on GA Numbers.



PDF Pages Table (Middle):

Purpose: Lists all pages from the active PDF binder. The user's primary role here is to select which pages are General Arrangements (GAs).

Synchronization Trigger: When a "GA" checkbox is checked, a "GA No." is calculated. This action triggers the automatic synchronization across the application.

CPT Files Table (Right):

Purpose: Lists all .cpt files from the active CPT version. It's a display of the CPT files and their link status.

Synchronization Logic: The application attempts to match the floor_index of each CPT file with the "GA No." of a selected PDF GA. A successful match establishes a link.

Story Data Table (Left):

Purpose: This table lists all the floors from the active CPT version, allowing the user to edit key properties for engineering scripts.

Synchronization: This table is populated from the CPT list on the right. Edits made here (e.g., to "Elevation") directly modify the underlying FloorData objects. The "To Be Updated" checkbox controls which floors are processed by script actions.

8. Development Roadmap

Phase 1: Solidify Core GUI and Linking (Current Focus)

Goal: Finalize the current GUI layout and automatic linking logic to ensure a stable foundation.

Sub-Tasks:

Implement the "Story Data" Table: Add the new table to the left panel of the GUI.

Populate Story Data: Populate this new table with the floors from the active CPT version.

Enable Editing: Allow users to edit "Elevation" and "Typical Count" in the Story Data table, which will update the core FloorData objects. The "To Be Updated" checkbox will control the to_be_updated flag on FloorData.

Confirm Sync Logic: Ensure that checking/unchecking a "GA" checkbox in the PDF table correctly triggers the automatic synchronization and updates the "GA Number" and "Linked PDF Page" columns in the CPT Files table.

Stabilize: Ensure project saving and loading (.pkl) correctly preserves the state of all tables and selections.

Phase 2: Implement Load Rundown Functionality

Goal: Develop the core engineering feature to perform a load rundown, transferring loads (reactions) from one level to another within the RAM Concept (.cpt) files. This process should run in a dedicated, non-blocking window, and the results (extracted reactions) should be stored within the `StructureModel` and `FloorData` objects for persistence and to avoid re-computation.

Sub-Tasks:

    **Phase 2.1: Dedicated Load Rundown Window & Threading**
        - **Create Load Rundown GUI:** Develop a new Python file for a dedicated Load Rundown window (e.g., `load_rundown_window.py`). This window will be launched from the main `RamApiGuiPyQt` application.
        - **Window UI:** Design the UI for this new window, including:
            - Controls to start/pause/stop the rundown process.
            - A display area for real-time progress updates and logs (e.g., a `QTextEdit`).
            - Status indicators.
        - **Threaded Execution:** Implement the load rundown process to run in a separate `QThread`. This will prevent the main GUI (and the new rundown window GUI) from freezing during potentially long calculations.
        - **Inter-thread Communication:** Use PyQt6 signals and slots for communication between the worker thread and the rundown window's GUI for updating progress and log messages. This will replace the `tailer` approach with a more integrated Qt solution.
        - **Instance Sharing:** The Load Rundown window/process will need access to instances of `CPTManager`, `ProjectManager`, and the main `StructureModel` from the main application.

    **Phase 2.2: RAM API Module for Load Interactions**
        - **Develop/Enhance RAM API Module:** Create or enhance a module in `core_logic` (e.g., `ram_api_interactions.py` or similar) to abstract all direct RAM Concept API calls related to loads and reactions.
        - **API Functions:** This module should include functions to:
            - Open and close `.cpt` files (potentially leveraging `CPTManager`).
            - Extract column and wall reactions (axial forces, moments, shears) for specified load cases and combinations.
            - Apply point loads (for column reactions) and line loads (for wall reactions) to specified load cases in a `.cpt` file.
            - Clear existing loads from specified load cases.
            - Handle RAM Concept API errors and exceptions gracefully.

    **Phase 2.3: Data Model Enhancements for Reactions & Element Linking**
        - **Define Reaction Dataclasses:** Create new dataclasses (e.g., `RamConceptReactions`, `EtabsReactions` - though ETABS is future) to store detailed reaction data (Fz, Mx, My, Fx, Fy for various load cases/combinations).
        - **Update `ColumnMesh` and `WallMesh`:**
            - Add attributes to `ColumnMesh` (in `data_model/column_data.py`) and `WallMesh` (in `data_model/wall_data.py`) to store instances of these reaction dataclasses. For example, `ram_reactions: Dict[str, RamConceptReactions]`, where the string key is the load case/combo name.
            - Ensure `ColumnMesh` and `WallMesh` have unique identifiers (e.g., `uuid` or a robust `name`) and store their geometric definition (coordinates for columns, start/end coordinates for walls).
        - **FloorData Association:**
            - Review how `ColumnMesh` and `WallMesh` instances are associated with `FloorData`. A single column/wall element can be "below" one `FloorData` and "above" another.
            - Consider if `FloorData` needs to store `columns_above_data` and `walls_above_data` in addition to `columns_under_data` and `walls_under_data` to clearly delineate roles for load transfer.
            - The `ColumnMesh`/`WallMesh` itself might need references to the `FloorData` it's "under" and the `FloorData` it's "over" if it spans between them directly.

    **Phase 2.4: Load Rundown Algorithm Development**
        - **Core Iteration Logic:** Implement the algorithm that iterates through the `FloorData` objects (sorted by elevation/`floor_index` and filtered by the "To Be Updated" checkbox in the "Story Data" table).
        - **Reaction Extraction:** For each "source" `FloorData` (level above):
            - Open its `.cpt` file using the RAM API module.
            - Extract reactions from `columns_below` and `walls_below` for all relevant load cases (e.g., Dead, Live Reducible, Live Unreducible, and their transfer counterparts).
            - Store these extracted reactions in the corresponding `ColumnMesh` and `WallMesh` objects within the source `FloorData`.
        - **Load Application:** For each "target" `FloorData` (current level being processed):
            - Open its `.cpt` file.
            - Clear any existing loads from the "Transfer - ..." load cases.
            - Retrieve the stored reactions from the `ColumnMesh` and `WallMesh` objects of the `FloorData` *above* it.
            - Apply these reactions as loads (point loads for columns, line loads for walls) onto the appropriate "Transfer - ..." load cases in the target `.cpt` file.
        - **Handling Skipped Levels (Mezzanines):**
            - The initial logic might assume direct transfer from the level immediately above (based on `floor_index`).
            - Plan for future enhancement: For complex scenarios like mezzanines where a column/wall might skip a level, the system will eventually need to determine load transfer paths more robustly. This could involve:
                - User-defined links between specific "column_over" from an upper floor and "column_under" of a lower floor.
                - Geometric checks (e.g., using Shapely) to see if a column from an upper level lands within the slab outline of a non-adjacent lower level. (This is a more advanced step).
        - **Data Integrity:** Implement checks for missing elements or mismatched locations during transfer, logging warnings or errors.

    **Phase 2.5: Storing Results in StructureModel & Pickling**
        - **Persist Reactions:** Ensure that all extracted reactions (stored in `ColumnMesh` and `WallMesh` as per Phase 2.3) are part of the `StructureModel`'s data that gets pickled.
        - **Save/Load Verification:** After a load rundown is complete, the user should be able to save the project. Upon reloading, the calculated reaction data should be available without needing to re-run the rundown. This allows other functions (like visualization or reporting) to use this pre-calculated data.

    **Phase 2.6: UI Integration and Control**
        - **Connect "Run Load Rundown" Button:** Link the button in the main GUI (or the new rundown window) to initiate the threaded load rundown process.
        - **Data Passing:** Pass the necessary `StructureModel` instance (or relevant parts like the ordered `FloorData` list) and manager instances (`CPTManager`, `ProjectManager`) to the rundown thread/logic.
        - **Feedback:** Provide clear feedback to the user upon completion (successful or with errors) of the load rundown, potentially updating status labels or showing a summary message.
        - **Post-Rundown Actions:** After the rundown, the `StructureModel` (now populated with reaction data) should be marked as dirty to prompt a save.

Phase 3: Implement RAM-to-PDF Visualization

Goal: Export mesh geometry and load data from RAM Concept files and overlay it visually onto the corresponding PDF GA drawings for verification.

Sub-Tasks:

Extract Geometry & Loads: Add functions to the RAM API module to extract slab/wall/column geometry and load data from .cpt files.

PDF Annotation Engine: Enhance pdf_processor.py with methods that use PyMuPDF to draw polygons, lines, and text onto a new copy of a PDF page based on the extracted RAM data.

Data Reporting: Use the Pandas and OpenPyXL libraries to generate a structured Excel report (.xlsx) of the extracted loads as a supplementary deliverable.

Phase 4: PDF-to-RAM Model Generation (Bluebeam Workflow)

Goal: Create a "backwards generation" workflow where annotations made in a PDF editor can be parsed to generate or update a RAM Concept model.

Sub-Tasks:

Define Annotation Standard: Create a clear standard for how slabs, columns, walls, and their properties should be annotated in a PDF (e.g., using specific layers, colors, and subjects in Bluebeam).

Develop Annotation Parser: Greatly expand pdf_processor.py to recognize this standard, parsing annotations to extract their geometric and property data.

Implement Model Generation: Enhance cpt_manager.py with a function that takes the parsed data and uses the RAM API to generate a new .cpt file from a template, creating the elements accordingly.

Phase 5: ETABS Integration (Long-Term Goal)

Goal: Incorporate ETABS model management into the application, enabling three-way synchronization.

Sub-Tasks:

Add ETABS UI: Create a new GUI section for managing ETABS file versions.

Extend Data Model: Add ETABS-related attributes (linked_etabs_story_name, etc.) to the FloorData class.

Develop Linking Logic: Create a mechanism (e.g., a new mapping table or dialog) for users to link a FloorData object (which represents a CPT/PDF pair) to a specific story in the ETABS model.

Build ETABS Manager: Create a new etabs_manager.py module in core_logic to handle interactions with the ETABS API.