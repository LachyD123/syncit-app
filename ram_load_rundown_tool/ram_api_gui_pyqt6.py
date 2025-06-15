import sys
import os
import json
import configparser
from datetime import datetime
import shutil

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QCheckBox,
    QFileDialog, QMessageBox, QGroupBox, QSizePolicy, QInputDialog, QTextEdit,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QColor, QBrush, QPen

# This path should point to where your 'scripts' and other core modules are located
SCRIPT_DIR_ABS = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_ABS = os.path.dirname(SCRIPT_DIR_ABS) # Adjust as necessary

if PROJECT_ROOT_ABS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_ABS)

from ram_load_rundown_tool.scripts.default_settings import SETTINGS_DEFAULT # type: ignore
# For type hinting StructureModel and FloorData
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from data_model.structure_model import StructureModel
    from data_model.floor_data import FloorData

def to_json_string(list_of_dicts) -> str:
    """Convert a list of dictionaries to a JSON string."""
    return json.dumps(list_of_dicts)

def from_json_string(json_string) -> list[dict]:
    """Convert a JSON string to a list of dictionaries."""
    if not json_string:
        return []
    return json.loads(json_string)

def to_list_string(list_of_strings) -> str:
    """Convert a list of strings to a string."""
    return str(",".join(list_of_strings))

def from_list_string(string) -> list[str]:
    """Convert a string to a list of strings."""
    if not string:
        return []
    return string.split(",")

class RamApiGuiPyQt6(QMainWindow):
    def __init__(self, structure_model: 'StructureModel', parent=None):
        super().__init__()
        self.structure_model = structure_model
        self.parent_main_app = parent # Could be used for callbacks if needed

        self.setWindowTitle("RAM API GUI (PyQt6) - Operations Module")
        self.setGeometry(100, 100, 1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.left_frame = QWidget()
        self.mid_frame = QWidget()
        self.right_frame = QWidget()

        self.left_layout = QVBoxLayout(self.left_frame)
        self.mid_layout = QVBoxLayout(self.mid_frame)
        self.right_layout = QVBoxLayout(self.right_frame)

        self._create_left_frame_content(self.left_layout)
        self._create_mid_frame_content(self.mid_layout)
        self._create_right_frame_content(self.right_layout)

        self.main_layout.addWidget(self.left_frame, 3)
        self.main_layout.addWidget(self.mid_frame, 5)
        self.main_layout.addWidget(self.right_frame, 4)

        self._populate_ui_from_structure_model()

    def _create_left_frame_content(self, parent_layout: QVBoxLayout):
        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QGridLayout()
        settings_group.setLayout(settings_layout)

        settings_layout.addWidget(QLabel("Reinforced Concrete Density (kN/m3):"), 0, 0)
        self.reinforced_concrete_density_edit = QLineEdit(str(SETTINGS_DEFAULT["REINFORCED_CONCRETE_DENSITY"]))
        settings_layout.addWidget(self.reinforced_concrete_density_edit, 0, 1)

        settings_layout.addWidget(QLabel("PDF Drawing Scale 1:?"), 1, 0)
        self.drawing_scale_edit = QLineEdit(str(SETTINGS_DEFAULT["DRAWING_SCALE_1_TO"]))
        settings_layout.addWidget(self.drawing_scale_edit, 1, 1)

        settings_layout.addWidget(QLabel("MAX Column Stiffness Ratio:"), 2, 0)
        self.max_column_stiffness_ratio_edit = QLineEdit(str(SETTINGS_DEFAULT["MAX_COLUMN_STIFFNESS_RATIO"]))
        settings_layout.addWidget(self.max_column_stiffness_ratio_edit, 2, 1)

        settings_layout.addWidget(QLabel("MIN Column Stiffness Ratio:"), 3, 0)
        self.min_column_stiffness_ratio_edit = QLineEdit(str(SETTINGS_DEFAULT["MIN_COLUMN_STIFFNESS_RATIO"]))
        settings_layout.addWidget(self.min_column_stiffness_ratio_edit, 3, 1)

        self.generate_mesh_checkbox = QCheckBox("Generate Mesh")
        self.generate_mesh_checkbox.setChecked(SETTINGS_DEFAULT["GENERATE_MESH"])
        settings_layout.addWidget(self.generate_mesh_checkbox, 4, 0, 1, 2)

        self.create_backup_files_checkbox = QCheckBox("Create Backup Files")
        self.create_backup_files_checkbox.setChecked(SETTINGS_DEFAULT["CREATE_BACKUP_FILES"])
        settings_layout.addWidget(self.create_backup_files_checkbox, 5, 0, 1, 2)

        parent_layout.addWidget(settings_group)

        # Loadings Names
        loadings_group = QGroupBox("RAM C Loading Names")
        loadings_layout = QGridLayout()
        loadings_group.setLayout(loadings_layout)

        loadings_layout.addWidget(QLabel("Transfer Dead:"), 0, 0)
        self.transfer_dead_edit = QLineEdit(SETTINGS_DEFAULT["TRANSFER_DEAD"])
        loadings_layout.addWidget(self.transfer_dead_edit, 0, 1)

        loadings_layout.addWidget(QLabel("Transfer LL Reducible:"), 1, 0)
        self.transfer_ll_reducible_edit = QLineEdit(SETTINGS_DEFAULT["TRANSFER_LL_REDUCIBLE"])
        loadings_layout.addWidget(self.transfer_ll_reducible_edit, 1, 1)

        loadings_layout.addWidget(QLabel("Transfer LL Unreducible:"), 2, 0)
        self.transfer_ll_unreducible_edit = QLineEdit(SETTINGS_DEFAULT["TRANSFER_LL_UNREDUCIBLE"])
        loadings_layout.addWidget(self.transfer_ll_unreducible_edit, 2, 1)

        loadings_layout.addWidget(QLabel("LL Unreducible:"), 3, 0)
        self.ll_unreducible_edit = QLineEdit(SETTINGS_DEFAULT["LL_UNREDUCIBLE"])
        loadings_layout.addWidget(self.ll_unreducible_edit, 3, 1)

        parent_layout.addWidget(loadings_group)

        # Load Combination Names
        load_combinations_group = QGroupBox("RAM C Load Combination Names")
        load_combinations_layout = QGridLayout()
        load_combinations_group.setLayout(load_combinations_layout)

        load_combinations_layout.addWidget(QLabel("All Dead LC:"), 0, 0)
        self.all_dead_lc_edit = QLineEdit(SETTINGS_DEFAULT["ALL_DEAD_LC"])
        load_combinations_layout.addWidget(self.all_dead_lc_edit, 0, 1)

        load_combinations_layout.addWidget(QLabel("All Live Load LC:"), 1, 0)
        self.all_live_load_lc_edit = QLineEdit(SETTINGS_DEFAULT["ALL_LIVE_LOADS_LC"])
        load_combinations_layout.addWidget(self.all_live_load_lc_edit, 1, 1)

        parent_layout.addWidget(load_combinations_group)

    def _create_mid_frame_content(self, parent_layout: QVBoxLayout):
        # Level Files
        files_group = QGroupBox("Level Files (from Main App)")
        files_layout = QVBoxLayout()
        files_group.setLayout(files_layout)

        self.file_listbox = QListWidget() # This will display files from the main app's StructureModel
        files_layout.addWidget(self.file_listbox)

        parent_layout.addWidget(files_group)

        # Project Folder
        root_group = QGroupBox("Project Folder (from Main App)")
        root_layout = QVBoxLayout()
        root_group.setLayout(root_layout)

        self.root_box = QLineEdit() # Changed to QLineEdit for simple display
        self.root_box.setReadOnly(True)
        root_layout.addWidget(self.root_box)

        parent_layout.addWidget(root_group)

    def _create_right_frame_content(self, parent_layout: QVBoxLayout):
        # Update Typical
        update_group = QGroupBox("Update Typical")
        update_layout = QGridLayout()
        update_group.setLayout(update_layout)

        update_layout.addWidget(QLabel("Update Typical:"), 0, 0)
        self.update_typical_edit = QLineEdit()
        update_layout.addWidget(self.update_typical_edit, 0, 1)
        self.update_typical_button = QPushButton("Update Typical")
        update_layout.addWidget(self.update_typical_button, 1, 0, 1, 2)

        parent_layout.addWidget(update_group)

        # Error Handling
        error_handling_group = QGroupBox("Error Handling")
        error_handling_layout = QGridLayout()
        error_handling_group.setLayout(error_handling_layout)

        error_handling_layout.addWidget(QLabel("Max Attempts if Errors Raised:"), 0, 0)
        self.max_attempts_edit = QLineEdit(str(SETTINGS_DEFAULT["MAX_ATTEMPTS_IF_ERRORS_RAISED"]))
        error_handling_layout.addWidget(self.max_attempts_edit, 0, 1)

        error_handling_layout.addWidget(QLabel("Exit Code After X Seconds:"), 1, 0)
        self.exit_code_edit = QLineEdit(str(SETTINGS_DEFAULT["EXIT_CODE_AFTER_X_SECONDS"]))
        error_handling_layout.addWidget(self.exit_code_edit, 1, 1)

        self.debug_checkbox = QCheckBox("Debug")
        self.debug_checkbox.setChecked(SETTINGS_DEFAULT["DEBUG"])
        error_handling_layout.addWidget(self.debug_checkbox, 2, 0, 1, 2)

        parent_layout.addWidget(error_handling_group)

        # Run Files
        run_files_group = QGroupBox("Run Files")
        run_files_layout = QVBoxLayout()
        run_files_group.setLayout(run_files_layout)

        self.do_load_rundown_checkbox = QCheckBox("Do Load Rundown")
        self.do_load_rundown_checkbox.setChecked(SETTINGS_DEFAULT["DO_LOAD_RUNDOWN"])
        run_files_layout.addWidget(self.do_load_rundown_checkbox)

        self.do_centroid_calcs_checkbox = QCheckBox("Do Centroid Calcs")
        self.do_centroid_calcs_checkbox.setChecked(SETTINGS_DEFAULT["DO_CENTROID_CALCS"])
        run_files_layout.addWidget(self.do_centroid_calcs_checkbox)

        self.update_column_stiffness_checkbox = QCheckBox("Update Column I Factor")
        self.update_column_stiffness_checkbox.setChecked(SETTINGS_DEFAULT["UPDATE_COLUMN_STIFNESS_CALCS"])
        run_files_layout.addWidget(self.update_column_stiffness_checkbox)

        self.run_calcs_button = QPushButton("Run Calcs")
        run_files_layout.addWidget(self.run_calcs_button)

        self.validate_inputs_button = QPushButton("Validate Inputs")
        run_files_layout.addWidget(self.validate_inputs_button)

        parent_layout.addWidget(run_files_group)

    def _populate_ui_from_structure_model(self):
        """Populates UI elements that depend on the StructureModel passed from the main app."""
        if not self.structure_model:
            return

        # Populate Project Folder display
        if self.structure_model.gui_data and self.structure_model.gui_data.root_directory:
            self.root_box.setText(self.structure_model.gui_data.root_directory)
        else:
            self.root_box.setText("N/A - Project Root not set in main app.")

        # Populate File Listbox
        self.file_listbox.clear()
        ordered_floors = self.structure_model.get_ordered_floors()
        if not ordered_floors:
            self.file_listbox.addItem("No CPT files loaded in main application.")
            return

        for floor_data in ordered_floors:
            # Display format similar to Tkinter: f"{filename}, [typical{file['typical']}], {listpath}"
            display_text = f"{floor_data.ram_model_name or 'N/A'}, [typical {floor_data.typical_count}], {floor_data.listpath or 'N/A'}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, floor_data.floor_name) # Store internal key
            self.file_listbox.addItem(item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # --- Mock StructureModel for standalone testing ---
    class MockFloorData:
        def __init__(self, name, index, ram_name, typical, listpath_val, floor_name_key):
            self.floor_name = floor_name_key
            self.floor_index = index
            self.ram_model_name = ram_name
            self.typical_count = typical
            self.listpath = listpath_val
            self.is_included = True # Assuming included for display

    class MockFloorsData:
        def __init__(self):
            self.floors = {
                "L1_key": MockFloorData("Level 1", 1, "L1.cpt", 1, "root/L1.cpt", "L1_key"),
                "L2_key": MockFloorData("Level 2", 2, "L2.cpt", 2, "root/L2.cpt", "L2_key")
            }
        def get_ordered_floors(self):
            return sorted(self.floors.values(), key=lambda fd: fd.floor_index)

    class MockGUIData:
        def __init__(self):
            self.root_directory = "/mock/project/root"
            self.included_files = ["L1.cpt", "L2.cpt"] # Example

    class MockStructureModel:
        def __init__(self):
            self.gui_data = MockGUIData()
            self.floors_data = MockFloorsData()
        
        def get_ordered_floors(self):
            return self.floors_data.get_ordered_floors()

    mock_model = MockStructureModel()
    main_window = RamApiGuiPyQt6(structure_model=mock_model)
    main_window.show()
    sys.exit(app.exec())