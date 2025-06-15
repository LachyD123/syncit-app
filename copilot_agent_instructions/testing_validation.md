# Testing & Validation Environment

## Testing Philosophy

### Test-Driven Validation
- **GUI Changes**: Manual testing with documented workflows
- **Business Logic**: Automated unit tests
- **Integration**: Semi-automated testing with real files
- **Performance**: Benchmarking with large datasets

## Testing Environment Setup

### Required Test Data Structure
```
syncit_app/test_data/
├── sample_cpt_files/
│   ├── GA_01_Level_1.cpt
│   ├── GA_02_Level_2.cpt
│   └── GA_03_Level_3.cpt
├── sample_pdfs/
│   └── Test_GA_Drawings.pdf
└── pickled_projects/
    └── test_project.pkl
```

### Development Dependencies
```python
# Add to requirements.txt
PyQt6>=6.5.0
PyMuPDF>=1.23.0
pandas>=2.0.0
openpyxl>=3.1.0
pytest>=7.0.0
pytest-qt>=4.0.0
pytest-mock>=3.0.0
coverage>=6.0.0
```

## Validation Rules for Agent Responses

### ✅ MUST VALIDATE Before Providing Code

1. **Syntax Check**: Code must be syntactically correct Python
2. **Import Validation**: All imports must be available in the environment
3. **Type Consistency**: Type hints must match actual usage
4. **PyQt6 Compatibility**: All Qt code must use PyQt6 syntax
5. **Method Signatures**: Must match existing class interfaces

### 🧪 Testing Requirements for New Code

#### For Data Model Changes
```python
def test_new_feature():
    """Template for data model tests"""
    # Arrange
    test_object = ClassName(test_data)
    
    # Act
    result = test_object.new_method()
    
    # Assert
    assert result == expected_value
    assert test_object.state_is_valid()
```

#### For GUI Components
```python
def test_gui_component(qtbot):
    """Template for GUI tests"""
    # Create widget
    widget = NewWidget()
    qtbot.addWidget(widget)
    
    # Test user interaction
    qtbot.click(widget.button)
    
    # Verify result
    assert widget.state == expected_state
```

### 🔍 Manual Testing Checklists

#### Foundation Testing (Required Before Phase 1)
- [ ] Python files import without errors
- [ ] Basic GUI window launches successfully
- [ ] FloorData objects can be created and modified
- [ ] Project save/load doesn't crash
- [ ] All required directories exist

#### Story Data Table Testing
- [ ] Table populates with correct floor data
- [ ] Editing Elevation updates FloorData object
- [ ] "To Be Updated" checkbox affects data model
- [ ] Table refresh works after CPT file changes
- [ ] Save/load preserves table state

#### Synchronization Testing
- [ ] PDF GA checkbox triggers CPT table update
- [ ] GA Number calculation works correctly
- [ ] Linked PDF Page column updates properly
- [ ] Multiple GA selections work independently

## Error Handling Validation

### Required Error Scenarios
1. **Missing Files**: Graceful handling of deleted/moved files
2. **Corrupted Data**: Recovery from malformed pickle files
3. **API Failures**: RAM Concept API connection issues
4. **Permission Issues**: Read-only file access problems
5. **Memory Limits**: Large file processing boundaries

### Error Message Standards
```python
# Good error message format
try:
    risky_operation()
except SpecificException as e:
    logger.error(f"Failed to {operation_description}: {str(e)}")
    show_user_message(f"Could not {user_friendly_action}. Please check {suggestion}.")
```

## Validation Checkpoints for Agents

### Before Code Generation
1. ✅ Read current_status.md to understand context
2. ✅ Verify the request aligns with current phase goals
3. ✅ Check that dependencies are met
4. ✅ Confirm the approach follows development rules

### After Code Generation
1. ✅ Code follows modular response format
2. ✅ All imports are correct for the environment
3. ✅ Type hints are complete and accurate
4. ✅ Error handling is appropriate
5. ✅ Method fits within existing class structure

### Integration Verification
1. ✅ New code integrates with existing data models
2. ✅ GUI changes maintain responsive behavior
3. ✅ Signals and slots are properly connected
4. ✅ Threading considerations are addressed
5. ✅ Persistence (pickle) compatibility maintained

## Performance Benchmarks

### Acceptable Performance Targets
- **GUI Responsiveness**: All user interactions < 100ms response
- **File Loading**: CPT files < 2 seconds, PDFs < 5 seconds
- **Synchronization**: Table updates < 500ms
- **Project Save/Load**: < 3 seconds for typical projects
- **Memory Usage**: < 500MB for large projects

## Foundation Validation Checklist

Before proceeding to Phase 1 tasks, verify:

### File Structure Validation
- [ ] All required directories exist
- [ ] All __init__.py files are present
- [ ] Import statements work correctly
- [ ] No circular import dependencies

### Core Class Validation
- [ ] FloorData class has all required properties
- [ ] StructureModel can contain FloorData objects
- [ ] GUI framework initializes without errors
- [ ] Project manager can save/load basic data

### Basic Functionality Test
```python
# Test sequence to verify foundation
def test_foundation():
    # 1. Import test
    from syncit_app.data_model.floor_data import FloorData
    from syncit_app.gui.ram_api_gui import RamApiGuiPyQt
    
    # 2. Object creation test
    floor = FloorData(name="Test Floor", elevation=100.0)
    
    # 3. GUI launch test
    app = QApplication([])
    gui = RamApiGuiPyQt()
    gui.show()
    
    # 4. Basic operation test
    assert floor.name == "Test Floor"
    assert floor.elevation == 100.0
```

This validation framework ensures code quality and proper foundation before Phase 1 development begins.
