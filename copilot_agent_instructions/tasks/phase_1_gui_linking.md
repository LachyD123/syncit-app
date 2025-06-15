# Phase 1: GUI & Linking Implementation

## 🎯 Phase Goal
Establish a stable three-table GUI with automatic synchronization based on GA Numbers.

## 📋 Phase Requirements Table

| Requirement ID | Description | User Story | Expected Behavior/Outcome | Status |
|----------------|-------------|------------|---------------------------|---------|
| P1-FR001 | Story Data Table Creation | As a developer, I need a left panel table to display floor data so users can edit floor properties | Table widget created with proper columns and layout integration | N |
| P1-FR002 | Table Population Logic | As a user, I want to see all floors from the active CPT version so I can manage them | Table automatically populates when CPT version changes | N |
| P1-FR003 | Floor Property Editing | As a user, I want to edit elevation and typical count so I can update floor parameters | Direct table editing updates FloorData objects in real-time | N |
| P1-FR004 | To Be Updated Checkbox | As a user, I want to mark floors for processing so the system knows which floors to include in operations | Checkbox column controls FloorData.to_be_updated flag | N |
| P1-FR005 | Three-Table Synchronization | As a user, I want all tables to stay in sync so changes propagate correctly | PDF GA selection triggers CPT table updates, Story Data reflects current floor state | N |
| P1-FR006 | Project State Persistence | As a user, I want my table selections saved so I don't lose work when reopening projects | Save/load preserves all table states and user selections | N |
| P1-FR007 | Data Validation | As a user, I want invalid input rejected so I can't break the system | Input validation with user-friendly error messages | N |
| P1-FR008 | GUI Responsiveness | As a user, I want the interface to stay responsive so large files don't freeze the application | Threading for file operations, progress indicators | N |

**Legend**: Y = Complete, N = Not Started, O = Ongoing

## 📝 Detailed Task Breakdown

### Task 1.1: Story Data Table Creation [STATUS: N]
**Status**: N (Not Started)
**Dependencies**: Foundation setup complete
**Location**: `gui/ram_api_gui.py`
**Priority**: HIGH - Blocks all other Phase 1 tasks

#### Prerequisites Check:
- [ ] FloorData class implemented
- [ ] Basic GUI framework exists
- [ ] CPT manager functionality available

#### Implementation Steps:
1. **Create Table Widget** [STATUS: N]
   ```python
   # filepath: gui/ram_api_gui.py
   # Add to RamApiGuiPyQt.__init__()
   self.story_data_table = QTableWidget()
   self.setup_story_data_table()
   ```

2. **Define Table Structure** [STATUS: N]
   - Columns: ["Floor Name", "Elevation", "Typical Count", "To Be Updated"]
   - Editable: Elevation, Typical Count, To Be Updated checkbox
   - Read-only: Floor Name

3. **Setup Table Properties** [STATUS: N]
   - Column widths and headers
   - Row selection behavior
   - Edit triggers and validation

#### Completion Criteria:
- [ ] Table widget exists and is visible in left panel
- [ ] Correct column headers and structure
- [ ] Proper edit flags set for each column
- [ ] Table integrated into main layout

### Task 1.2: Table Population Logic [STATUS: N]
**Status**: N (Not Started)
**Dependencies**: Task 1.1 complete
**Trigger**: When active CPT version changes
**Data Source**: `self.structure_model.floors` (FloorData objects)

#### Implementation Steps:
1. **Create Population Method** [STATUS: N]
   ```python
   # filepath: gui/ram_api_gui.py
   def populate_story_data_table(self):
       """Fill table with current floor data from active CPT version"""
       # Clear existing rows
       # Iterate through structure_model.floors
       # Create table items for each floor
       # Set edit flags and initial values
   ```

2. **Data Binding** [STATUS: N]
   - Floor Name → `floor_data.name`
   - Elevation → `floor_data.elevation`
   - Typical Count → `floor_data.typical_count`
   - To Be Updated → `floor_data.to_be_updated`

3. **Refresh Triggers** [STATUS: N]
   - CPT version selection change
   - Project load
   - Floor data modification

#### Completion Criteria:
- [ ] Table populates with all floors from active CPT version
- [ ] Data correctly mapped from FloorData objects
- [ ] Table refreshes when CPT version changes
- [ ] Empty state handled gracefully

### Task 1.3: Edit Functionality [STATUS: N]
**Status**: N (Not Started)
**Dependencies**: Tasks 1.1, 1.2 complete
**Requirement**: Direct editing updates FloorData objects

#### Implementation Steps:
1. **Connect Edit Signals** [STATUS: N]
   ```python
   # filepath: gui/ram_api_gui.py
   # In setup_story_data_table()
   self.story_data_table.itemChanged.connect(self.on_story_data_edited)
   ```

2. **Edit Handler Method** [STATUS: N]
   ```python
   # filepath: gui/ram_api_gui.py
   def on_story_data_edited(self, item):
       """Handle user edits to Story Data table"""
       # Identify which floor and property was edited
       # Update corresponding FloorData object
       # Validate input (e.g., elevation is numeric)
       # Mark project as dirty for save prompt
   ```

3. **Validation Rules** [STATUS: N]
   - Elevation: Must be numeric, reasonable range
   - Typical Count: Must be positive integer
   - To Be Updated: Boolean checkbox

#### Completion Criteria:
- [ ] Table edits update FloorData objects immediately
- [ ] Input validation prevents invalid data
- [ ] User-friendly error messages for invalid input
- [ ] Project marked as dirty when changes made

### Task 1.4: Synchronization Integration [STATUS: N]
**Status**: N (Not Started)
**Dependencies**: Tasks 1.1-1.3 complete
**Goal**: Story Data table syncs with CPT Files table

#### Sync Logic Implementation:
1. **Population Source**: Story Data populated from same FloorData objects that link to CPT files
2. **Update Propagation**: Changes to FloorData in Story table affect CPT table display
3. **Bi-directional**: CPT file changes refresh Story Data table

#### Implementation:
```python
# filepath: gui/ram_api_gui.py
def refresh_all_tables(self):
    """Refresh all three tables to maintain synchronization"""
    self.populate_story_data_table()
    self.populate_cpt_files_table()
    self.populate_pdf_pages_table()
```

#### Completion Criteria:
- [ ] PDF GA checkbox selection triggers CPT table updates
- [ ] Story Data changes reflect in other tables
- [ ] CPT version changes refresh Story Data
- [ ] All tables stay synchronized during operations

### Task 1.5: Testing & Validation [STATUS: N]
**Status**: N (Not Started)
**Dependencies**: All previous tasks complete

#### Manual Test Cases:
1. **Table Population Test** [STATUS: N]
   - Load project with multiple floors
   - Verify all floors appear in Story Data table
   - Check initial values match FloorData objects

2. **Edit Functionality Test** [STATUS: N]
   - Edit elevation value, verify FloorData.elevation updates
   - Toggle "To Be Updated" checkbox, verify flag changes
   - Test invalid input shows user-friendly error

3. **Synchronization Test** [STATUS: N]
   - Change CPT version, verify Story Data refreshes
   - Edit in Story Data, verify related displays update
   - Save and reload project, verify all edits persist

#### Completion Criteria:
- [ ] All manual test cases pass
- [ ] Error scenarios handled gracefully
- [ ] Performance acceptable with large datasets
- [ ] User experience is intuitive

## 🔄 Phase 1 Completion Criteria

### Prerequisites for Phase 2:
- [ ] P1-FR001 through P1-FR008 all marked as Y (Complete)
- [ ] All three tables functional and synchronized
- [ ] Project save/load preserves all table states
- [ ] FloorData objects properly updated by GUI edits
- [ ] Error handling for edge cases implemented
- [ ] Manual testing completed successfully

### Phase 2 Readiness Indicators:
- [ ] User can edit floor properties through GUI
- [ ] "To Be Updated" flags control which floors are processed
- [ ] GA Number synchronization works reliably
- [ ] GUI remains responsive with multiple files

## 🐛 Current Issues & Next Actions

### **CRITICAL**: Foundation Must Be Complete First
Before ANY Phase 1 tasks can begin:
- [ ] All Python files and directory structure created
- [ ] FloorData class implemented with required properties
- [ ] Basic GUI framework established
- [ ] PyQt6 application can launch successfully

### Once Foundation Complete:
1. **START**: Task 1.1 - Create Story Data table widget
2. **IMPLEMENT**: Basic table structure with correct columns
3. **INTEGRATE**: Table into main GUI layout

### Agent Instructions:
When working on Phase 1:
1. Verify foundation is complete before starting any task
2. Update task status from N to O when starting
3. Create git checkpoint before implementation
4. Mark as Y only when fully tested and integrated
5. Move to next task only when current task dependencies are met

This completes Phase 1 detailed implementation guide. Each step provides specific code guidance while maintaining the modular response format required by the development rules.
