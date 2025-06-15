
import sys # type: ignore
import os
import pickle
from datetime import datetime
import shutil
import re
import fitz
try:
    import openpyxl
except ImportError:
    print("CRITICAL ERROR: The 'openpyxl' library is required. Please install it: pip install openpyxl")    
    sys.exit(1)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QCheckBox,
    QFileDialog, QMessageBox, QGroupBox, QSizePolicy, QInputDialog, QTextEdit,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QDialogButtonBox, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QColor, QBrush, QPen

SCRIPT_DIR_ABS = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_ABS = os.path.dirname(SCRIPT_DIR_ABS) 

if PROJECT_ROOT_ABS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_ABS)

from data_model.structure_model import StructureModel, ModelPage
from data_model.floor_data import FloorData
from gui.gui_data import GUIData, SETTINGS_DEFAULT, PDF_BINDERS_DIR_NAME, DEFAULT_MASTER_CPT_TEMPLATE_PATH
from core_logic.project_manager import ProjectManager, RAM_CONCEPT_DIR_NAME, PICKLED_DATA_FILENAME
from core_logic.pdf_processor import PDFProcessor
from core_logic.cpt_manager import CPTManager
from ram_load_rundown_tool.ram_api_gui_pyqt6 import RamApiGuiPyQt6
from gui.load_rundown_window import LoadRundownWindow # Import the new window

class PlaceholderScripts:
    @staticmethod
    def validate_settings_wrapped(settings, parent=None):
        # print(f"[STUB] validate_settings_wrapped called with settings: {settings}")
        QMessageBox.information(parent, "Validation", "Settings validation (stub) called.")
        return True

    @staticmethod
    def run_click(settings, parent=None):
        # print(f"[STUB] run_click called with settings: {settings}")
        QMessageBox.information(parent, "Run Calcs", "Run calculations (stub) initiated.")

    @staticmethod
    def get_data_click(settings, parent=None):
        # print(f"[STUB] get_data_click called with settings: {settings}")
        QMessageBox.information(parent, "Get Data", "Get data (stub) initiated.")


class RamApiGuiPyQt(QMainWindow):
  # Floor Data Table Columns (Right Table)
    COL_FD_INCLUDE = 0
    COL_FD_GA_NUMBER = 1
    COL_FD_CPT_FILENAME = 2
    COL_FD_TYPICAL = 3
    COL_FD_LINKED_PDF_PAGE_DISPLAY = 4
    COL_FD_CPT_FILEPATH_DISPLAY = 5
    NUM_FD_COLUMNS = 6

    # PDF Pages Table Columns (Middle Table)
    COL_PP_IS_GA = 0
    COL_PP_GA_NUMBER_DISPLAY = 1
    COL_PP_PDF_PAGE_REF = 2
    NUM_PP_COLUMNS = 3 # Reduced from 4

    # New Story Data Table Columns (Left Table)
    COL_STORY_UPDATE = 0
    COL_STORY_NAME = 1
    COL_STORY_ELEV = 2
    COL_STORY_TYPICAL = 3
    NUM_STORY_COLUMNS = 4

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAM API GUI - Automated GA Linking")
        self.setGeometry(100, 100, 1900, 980)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.left_section_widget = QWidget()
        self.middle_section_widget = QWidget()
        self.right_section_widget = QWidget()

        self.left_section_layout = QVBoxLayout(self.left_section_widget)
        self.middle_section_layout = QVBoxLayout(self.middle_section_widget)
        self.right_section_layout = QVBoxLayout(self.right_section_widget)

        default_gui_data_init = GUIData.from_dict(SETTINGS_DEFAULT)
        self.structure_model_instance = StructureModel(gui_data=default_gui_data_init)

        self.project_manager = ProjectManager(self.structure_model_instance, self)
        self.pdf_processor = PDFProcessor(self.structure_model_instance)
        self.cpt_manager = CPTManager(self.structure_model_instance)

        self._table_update_in_progress = False
        self._pdf_table_update_in_progress = False
        self._programmatic_checkbox_update = False
        self._programmatic_pdf_checkbox_update = False
        self.load_rundown_dialog = None # Attribute for the new dialog
        self.ram_api_operations_module_window = None # Attribute for the RamApiGuiPyQt6 window
        self._programmatic_ui_update = False

        self._create_left_frame_content(self.left_section_layout)
        self._create_middle_frame_content(self.middle_section_layout)
        self._create_right_frame_content(self.right_section_layout)

        self.left_scroll_area = QScrollArea(); self.left_scroll_area.setWidgetResizable(True); self.left_scroll_area.setWidget(self.left_section_widget)
        self.middle_scroll_area = QScrollArea(); self.middle_scroll_area.setWidgetResizable(True); self.middle_scroll_area.setWidget(self.middle_section_widget)
        self.right_scroll_area = QScrollArea(); self.right_scroll_area.setWidgetResizable(True); self.right_scroll_area.setWidget(self.right_section_widget)

        self.main_layout.addWidget(self.left_scroll_area, 4)
        self.main_layout.addWidget(self.middle_scroll_area, 6)
        self.main_layout.addWidget(self.right_scroll_area, 6)

        self._connect_signals()
        self._setup_shortcuts()
        self._perform_initial_checks()

    def _create_left_frame_content(self, parent_layout):
        # --- Project (Folder & Data Operations) Group ---
        project_ops_layout = self._create_group_box("PROJECT (Folder & Data Operations)", parent_layout)
        project_ops_layout.addWidget(QLabel("Project Root Directory:"))
        self.root_directory_edit = QLineEdit()
        self.root_directory_edit.setReadOnly(True)
        project_ops_layout.addWidget(self.root_directory_edit)
        self.select_project_dir_btn = QPushButton("Select New/Existing Project Directory...")
        project_ops_layout.addWidget(self.select_project_dir_btn)
        save_load_grid = QGridLayout()
        self.save_project_btn = QPushButton("Save Project Data")
        self.save_project_btn.setEnabled(False)
        self.save_project_as_btn = QPushButton("Save Project Data As...")
        save_load_grid.addWidget(self.save_project_btn, 0, 0)
        save_load_grid.addWidget(self.save_project_as_btn, 0, 1)
        project_ops_layout.addLayout(save_load_grid)

        # --- New Story Data Table ---
        story_data_layout = self._create_group_box("FLOOR/STORY DATA (for Script Actions)", parent_layout)
        self.story_data_table = QTableWidget()
        self.story_data_table.setColumnCount(self.NUM_STORY_COLUMNS)
        self.story_data_table.setHorizontalHeaderLabels(["To Be Updated", "Floor Name", "Elevation (TOC)", "Typical Count"])
        self.story_data_table.verticalHeader().setVisible(False)
        story_header = self.story_data_table.horizontalHeader()
        story_header.setSectionResizeMode(self.COL_STORY_UPDATE, QHeaderView.ResizeMode.ResizeToContents)
        story_header.setSectionResizeMode(self.COL_STORY_NAME, QHeaderView.ResizeMode.Stretch)
        story_header.setSectionResizeMode(self.COL_STORY_ELEV, QHeaderView.ResizeMode.Interactive)
        story_header.setSectionResizeMode(self.COL_STORY_TYPICAL, QHeaderView.ResizeMode.Interactive)
        story_data_layout.addWidget(self.story_data_table)

        parent_layout.addStretch(1)
    def _create_middle_frame_content(self, parent_layout):
        pdf_version_mgmt_layout = self._create_group_box("PDF GA BINDER VERSION MANAGEMENT", parent_layout)
        self.active_pdf_version_label = QLabel("Active PDF Version: None")
        pdf_version_mgmt_layout.addWidget(self.active_pdf_version_label)
        self.pdf_version_explorer_listbox = QListWidget()
        self.pdf_version_explorer_listbox.setFixedHeight(80)
        pdf_version_mgmt_layout.addWidget(self.pdf_version_explorer_listbox)
        pdf_version_buttons_layout_1 = QHBoxLayout()
        self.refresh_pdf_versions_btn = QPushButton("Refresh List"); pdf_version_buttons_layout_1.addWidget(self.refresh_pdf_versions_btn)
        self.set_active_pdf_version_btn = QPushButton("Set Active Version"); pdf_version_buttons_layout_1.addWidget(self.set_active_pdf_version_btn)
        pdf_version_mgmt_layout.addLayout(pdf_version_buttons_layout_1)
        pdf_version_buttons_layout_2 = QHBoxLayout()
        self.import_pdf_to_new_version_btn = QPushButton("Import PDF to New Version..."); pdf_version_buttons_layout_2.addWidget(self.import_pdf_to_new_version_btn)
        self.delete_pdf_version_btn = QPushButton("Delete PDF Version"); pdf_version_buttons_layout_2.addWidget(self.delete_pdf_version_btn)
        pdf_version_mgmt_layout.addLayout(pdf_version_buttons_layout_2)
        pdf_version_mgmt_layout.addWidget(QLabel("Active PDF Path (Read-only):"))
        self.active_pdf_path_display_edit = QLineEdit()
        self.active_pdf_path_display_edit.setReadOnly(True)
        self.active_pdf_path_display_edit.setPlaceholderText("No active PDF version selected")
        pdf_version_mgmt_layout.addWidget(self.active_pdf_path_display_edit)

        pdf_pages_table_group_layout = self._create_group_box("DETECTED PDF PAGES (GAs)", parent_layout)
        self.pdf_pages_table = QTableWidget()
        self.pdf_pages_table.setColumnCount(self.NUM_PP_COLUMNS)
        self.pdf_pages_table.setHorizontalHeaderLabels(["GA", "GA No.", "PDF Page Ref"]) # Headers updated
        self.pdf_pages_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.pdf_pages_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.pdf_pages_table.verticalHeader().setVisible(False)
        self.pdf_pages_table.setMinimumHeight(200)


        pp_header = self.pdf_pages_table.horizontalHeader()
        pp_header.setSectionResizeMode(self.COL_PP_IS_GA, QHeaderView.ResizeMode.ResizeToContents)
        pp_header.setSectionResizeMode(self.COL_PP_GA_NUMBER_DISPLAY, QHeaderView.ResizeMode.ResizeToContents)
        pp_header.setSectionResizeMode(self.COL_PP_PDF_PAGE_REF, QHeaderView.ResizeMode.Stretch)
        pdf_pages_table_group_layout.addWidget(self.pdf_pages_table)

        pdf_processing_group_layout = self._create_group_box("CPT CREATION (from Selected GAs in Active PDF)", parent_layout)
        pdf_processing_group_layout.addWidget(QLabel("Master CPT Template (for new CPTs from GAs):"))
        self.master_cpt_template_edit = QLineEdit()
        self.master_cpt_template_edit.setPlaceholderText(f"e.g., {DEFAULT_MASTER_CPT_TEMPLATE_PATH}")
        pdf_processing_group_layout.addWidget(self.master_cpt_template_edit)
        self.browse_master_cpt_btn = QPushButton("Browse Master CPT...")
        pdf_processing_group_layout.addWidget(self.browse_master_cpt_btn)
        self.process_pdf_to_cpts_btn = QPushButton("Process SELECTED GAs & Create Template CPTs in New CPT Version")
        self.process_pdf_to_cpts_btn.setStyleSheet("font-weight: bold; padding: 5px;")
        pdf_processing_group_layout.addWidget(self.process_pdf_to_cpts_btn)

        run_layout = self._create_group_box("RUN ACTIONS / SCRIPTS", parent_layout)
        self.validate_inputs_btn = QPushButton("Validate All Inputs (Stub)"); run_layout.addWidget(self.validate_inputs_btn)
        self.get_data_btn = QPushButton("Get Data from CPTs (Stub)"); run_layout.addWidget(self.get_data_btn)
        self.run_calcs_btn = QPushButton("Run Calculations (Stub)"); self.run_calcs_btn.setStyleSheet("font-weight: bold; background-color: #D5E8D4;")
        # Add new button for Load Rundown
        self.open_ram_operations_module_btn = QPushButton("Open RAM Operations Module")
        run_layout.addWidget(self.open_ram_operations_module_btn)

        self.run_load_rundown_btn = QPushButton("Run Load Rundown")
        run_layout.addWidget(self.run_load_rundown_btn)
        run_layout.addWidget(self.run_calcs_btn)
        parent_layout.addStretch(1)
    
    def _create_right_frame_content(self, parent_layout):
        cpt_version_mgmt_layout = self._create_group_box("RAM CONCEPT VERSION MANAGEMENT (CPT Files)", parent_layout)
        self.active_cpt_version_label = QLabel("Active CPT Version: None")
        cpt_version_mgmt_layout.addWidget(self.active_cpt_version_label)
        self.cpt_version_explorer_listbox = QListWidget(); self.cpt_version_explorer_listbox.setFixedHeight(100)
        cpt_version_mgmt_layout.addWidget(self.cpt_version_explorer_listbox)

        cpt_version_buttons_layout = QHBoxLayout()
        self.refresh_cpt_versions_btn = QPushButton("Refresh"); cpt_version_buttons_layout.addWidget(self.refresh_cpt_versions_btn)
        self.set_active_cpt_version_btn = QPushButton("Set Active"); cpt_version_buttons_layout.addWidget(self.set_active_cpt_version_btn)
        self.create_next_cpt_version_btn = QPushButton("Create Next"); cpt_version_buttons_layout.addWidget(self.create_next_cpt_version_btn)
        self.delete_cpt_version_btn = QPushButton("Delete"); cpt_version_buttons_layout.addWidget(self.delete_cpt_version_btn)
        cpt_version_mgmt_layout.addLayout(cpt_version_buttons_layout)

        floor_data_group_layout = self._create_group_box("FLOOR DATA MANAGEMENT (CPTs in Active Version)", parent_layout)
        self.floor_data_table = QTableWidget(); self.floor_data_table.setColumnCount(self.NUM_FD_COLUMNS)

        self.floor_data_table.setHorizontalHeaderLabels(["Include", "GA Number", "CPT Filename", "Typical", "Linked PDF Page", "Linked .CPT File Path"])
        self.floor_data_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.floor_data_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.floor_data_table.verticalHeader().setVisible(False); self.floor_data_table.setMinimumHeight(200)

        header = self.floor_data_table.horizontalHeader()
        header.setSectionResizeMode(self.COL_FD_INCLUDE, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.COL_FD_GA_NUMBER, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.COL_FD_CPT_FILENAME, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(self.COL_FD_TYPICAL, QHeaderView.ResizeMode.ResizeToContents) # Now read-only display
        header.setSectionResizeMode(self.COL_FD_LINKED_PDF_PAGE_DISPLAY, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(self.COL_FD_CPT_FILEPATH_DISPLAY, QHeaderView.ResizeMode.Stretch)
        self.floor_data_table.setColumnWidth(self.COL_FD_CPT_FILENAME, 150)
        self.floor_data_table.setColumnWidth(self.COL_FD_LINKED_PDF_PAGE_DISPLAY, 120)
        self.floor_data_table.setColumnWidth(self.COL_FD_CPT_FILEPATH_DISPLAY, 150)
        floor_data_group_layout.addWidget(self.floor_data_table)

        self.ga_count_warning_label = QLabel("")
        self.ga_count_warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        floor_data_group_layout.addWidget(self.ga_count_warning_label)

        table_ops_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("Add CPT(s) to Active Version"); table_ops_layout.addWidget(self.add_files_btn)
        self.remove_file_btn = QPushButton("Remove Selected CPT"); table_ops_layout.addWidget(self.remove_file_btn)
        self.move_up_btn = QPushButton("Move Up"); table_ops_layout.addWidget(self.move_up_btn)
        self.move_down_btn = QPushButton("Move Down"); table_ops_layout.addWidget(self.move_down_btn)
        floor_data_group_layout.addLayout(table_ops_layout)

        check_uncheck_layout = QHBoxLayout()
        self.check_all_btn = QPushButton("Check All Include"); check_uncheck_layout.addWidget(self.check_all_btn)
        self.uncheck_all_btn = QPushButton("Uncheck All Include"); check_uncheck_layout.addWidget(self.uncheck_all_btn)
        self.remove_all_files_btn = QPushButton("Remove All CPTs from List"); check_uncheck_layout.addWidget(self.remove_all_files_btn)
        floor_data_group_layout.addLayout(check_uncheck_layout)

        self.included_files_summary_label = QLabel("Number of CPTs marked 'Include': 0")
        floor_data_group_layout.addWidget(self.included_files_summary_label)
        parent_layout.addStretch(1)

    def _create_group_box(self, title, parent_layout):
        group_box = QGroupBox(title)
        group_box_layout = QVBoxLayout(group_box)
        parent_layout.addWidget(group_box)
        return group_box_layout

    def _perform_initial_checks(self):
        print("Performing initial checks...")
        loaded_ok, model_after_load_attempt = self.project_manager.load_project_data()
        
        if model_after_load_attempt:
            self.structure_model_instance = model_after_load_attempt
            self.project_manager.model = self.structure_model_instance
            self.pdf_processor.structure_model = self.structure_model_instance
            self.cpt_manager.structure_model = self.structure_model_instance

        if loaded_ok:
            print(f"Successfully loaded project data from {self.project_manager.get_pickle_data_path()}")
            QMessageBox.information(self, "Project Loaded", f"Project data loaded from:\n{self.structure_model_instance.gui_data.root_directory}")
        elif self.structure_model_instance.gui_data.root_directory: 
             QMessageBox.warning(self, "Load Failed", f"Could not load project data from '{self.structure_model_instance.gui_data.root_directory}'.\nStarting with a new project state for this directory.")
        else: 
            print("No existing project data loaded. Please select a project directory.")

        self._update_gui_from_model_data() 
        self._update_all_explorers_and_tables()


    def _update_gui_from_model_data(self):
        self._programmatic_ui_update = True
        
        gui_data = self.structure_model_instance.gui_data
        if not isinstance(gui_data, GUIData): 
            print("CRITICAL: gui_data is not a GUIData instance in _update_gui_from_model_data. Resetting.")
            self.structure_model_instance.gui_data = GUIData.from_dict(SETTINGS_DEFAULT)
            gui_data = self.structure_model_instance.gui_data

        self.root_directory_edit.setText(gui_data.root_directory or "Project Root Not Set")
        self.save_project_btn.setEnabled(bool(gui_data.root_directory)) 
        self.save_project_as_btn.setEnabled(bool(gui_data.root_directory)) 
        
        self.active_cpt_version_label.setText(f"Active CPT Version: {gui_data.cpt_active_folder_name or 'None'}")
        
        self.active_pdf_version_label.setText(f"Active PDF Version: {gui_data.active_pdf_binder_version_name or 'None'}")
        active_pdf_full_path = gui_data.current_pdf_binder_full_path 
        self.active_pdf_path_display_edit.setText(active_pdf_full_path or "No active PDF binder")

        self.master_cpt_template_edit.setText(gui_data.master_cpt_template_path or DEFAULT_MASTER_CPT_TEMPLATE_PATH)

        self._update_floor_data_table() 
        self._update_pdf_pages_table()  

        self._sync_cpt_checkboxes_to_floor_data() 
        self._sync_pdf_checkboxes_to_model_page_data() 

        num_included_cpts = len(gui_data.included_files) if gui_data.included_files else 0
        self.included_files_summary_label.setText(f"Number of CPTs marked 'Include': {num_included_cpts}")
        
        self._on_floor_table_selection_changed() 
        self._on_pdf_version_selection_changed() 
        self._on_cpt_version_selection_changed() 
        

        self._programmatic_ui_update = False

    def _connect_signals(self):
        # Project Controls
        self.select_project_dir_btn.clicked.connect(self.select_or_create_project_directory)
        self.save_project_btn.clicked.connect(self.save_project_data_explicit)
        self.save_project_as_btn.clicked.connect(self.save_project_data_as)

        # New Story Data Table
        self.story_data_table.itemChanged.connect(self._on_story_table_item_changed)

        # PDF Version Controls
        self.refresh_pdf_versions_btn.clicked.connect(self._update_pdf_version_explorer_listbox)
        self.set_active_pdf_version_btn.clicked.connect(self._set_active_pdf_version_from_explorer)
        self.import_pdf_to_new_version_btn.clicked.connect(self._import_pdf_to_new_version_gui)
        self.delete_pdf_version_btn.clicked.connect(self._delete_selected_pdf_version)
        self.pdf_version_explorer_listbox.itemSelectionChanged.connect(self._on_pdf_version_selection_changed)
        self.pdf_version_explorer_listbox.itemDoubleClicked.connect(self._set_active_pdf_version_from_explorer)

        # PDF Table - only checkboxes have direct signals now, connected in _update_pdf_pages_table_row

        # CPT Creation Controls
        self.browse_master_cpt_btn.clicked.connect(self._browse_master_cpt_template)
        self.master_cpt_template_edit.editingFinished.connect(self._update_master_cpt_path_in_model_and_save)
        self.process_pdf_to_cpts_btn.clicked.connect(self.process_pdf_and_create_cpts)

        # CPT Version Controls
        self.refresh_cpt_versions_btn.clicked.connect(self._update_cpt_version_explorer_listbox)
        self.set_active_cpt_version_btn.clicked.connect(self.set_active_cpt_version_with_sync)
        self.create_next_cpt_version_btn.clicked.connect(self.create_next_ram_version_gui)
        self.delete_cpt_version_btn.clicked.connect(self.delete_selected_cpt_version)
        self.cpt_version_explorer_listbox.itemSelectionChanged.connect(self._on_cpt_version_selection_changed)
        self.cpt_version_explorer_listbox.itemDoubleClicked.connect(self.set_active_cpt_version_with_sync)

        # CPT Table Controls
        self.floor_data_table.itemChanged.connect(self._on_cpt_table_item_changed)
        self.floor_data_table.itemSelectionChanged.connect(self._on_floor_table_selection_changed)
        self.add_files_btn.clicked.connect(self.add_cpt_files_to_active_version)
        self.remove_file_btn.clicked.connect(self.remove_selected_file_from_cpt_list)
        self.move_up_btn.clicked.connect(self.move_cpt_file_up)
        self.move_down_btn.clicked.connect(self.move_cpt_file_down)
        self.check_all_btn.clicked.connect(self._check_all_cpt_include_boxes)
        self.uncheck_all_btn.clicked.connect(self._uncheck_all_cpt_include_boxes)
        self.remove_all_files_btn.clicked.connect(self.remove_all_files_from_cpt_list)

        # Script Execution
        self.run_calcs_btn.clicked.connect(self.wrapped_run_click)
        self.validate_inputs_btn.clicked.connect(self.wrapped_validate_settings)
        self.get_data_btn.clicked.connect(self.wrapped_get_data_click)
        self.open_ram_operations_module_btn.clicked.connect(self._launch_ram_operations_module_window) # type: ignore
        self.run_load_rundown_btn.clicked.connect(self._launch_load_rundown_window)


    def _update_floor_data_table_row(self, row: int, floor_data_obj: FloorData):
        self._table_update_in_progress = True
        
        is_placeholder = floor_data_obj.is_placeholder
        placeholder_color = QColor("#F0F0F0") # Light gray for placeholder rows

        # --- COL_FD_INCLUDE: Include Checkbox ---
        # ... (This part of the method remains the same)
        checkbox_widget_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget_container)
        checkbox_layout.setContentsMargins(5, 0, 5, 0); checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        include_cb = QCheckBox()
        include_cb.setChecked(getattr(floor_data_obj, 'is_included', False))
        include_cb.stateChanged.connect(lambda state, r=row, fd_key=floor_data_obj.floor_name: self._on_cpt_include_checkbox_changed(state, r, fd_key))
        checkbox_layout.addWidget(include_cb)
        self.floor_data_table.setCellWidget(row, self.COL_FD_INCLUDE, checkbox_widget_container)

        # --- GA Number, Filename, etc. ---
        ga_number_text = str(floor_data_obj.floor_index) if floor_data_obj.floor_index is not None else "-"
        ga_number_item = QTableWidgetItem(ga_number_text)

        filename_text = str(floor_data_obj.ram_model_name or 'N/A')
        filename_item = QTableWidgetItem(filename_text)

        typical_item = QTableWidgetItem(str(getattr(floor_data_obj, 'typical_count', '1')))
        
        pdf_page_id_text = floor_data_obj.linked_pdf_page_identifier or "None"
        pdf_page_item = QTableWidgetItem(pdf_page_id_text)

        list_path = getattr(floor_data_obj, 'listpath', 'N/A' if not is_placeholder else "<No File>")
        path_item = QTableWidgetItem(list_path)

        # --- Set common properties for all items in the row ---
        items_to_style = [ga_number_item, filename_item, typical_item, pdf_page_item, path_item]
        for item in items_to_style:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if is_placeholder:
                item.setBackground(placeholder_color)
                font = item.font(); font.setItalic(True); item.setFont(font)
        
        if not is_placeholder and (not floor_data_obj.filepath or not os.path.exists(floor_data_obj.filepath)):
            path_item.setBackground(QColor("pink")) # Highlight if real file is missing
        
        filename_item.setData(Qt.ItemDataRole.UserRole, floor_data_obj.floor_name)
        ga_number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.floor_data_table.setItem(row, self.COL_FD_GA_NUMBER, ga_number_item)
        self.floor_data_table.setItem(row, self.COL_FD_CPT_FILENAME, filename_item)
        self.floor_data_table.setItem(row, self.COL_FD_TYPICAL, typical_item)
        self.floor_data_table.setItem(row, self.COL_FD_LINKED_PDF_PAGE_DISPLAY, pdf_page_item)
        self.floor_data_table.setItem(row, self.COL_FD_CPT_FILEPATH_DISPLAY, path_item)

        self._table_update_in_progress = False


    def _update_master_cpt_path_in_model_and_save(self):
        if self._programmatic_ui_update: return
        new_path = self.master_cpt_template_edit.text()
        if self.structure_model_instance.gui_data.master_cpt_template_path != new_path:
            self.structure_model_instance.gui_data.master_cpt_template_path = new_path
            self._save_project_data_to_pickle()

    def _browse_master_cpt_template(self):
        current_path_in_gui_data = self.structure_model_instance.gui_data.master_cpt_template_path
        
        start_dir = self.structure_model_instance.gui_data.root_directory or PROJECT_ROOT_ABS
        if current_path_in_gui_data:
            if os.path.isabs(current_path_in_gui_data) and os.path.exists(os.path.dirname(current_path_in_gui_data)):
                start_dir = os.path.dirname(current_path_in_gui_data)
            elif self.structure_model_instance.gui_data.root_directory:
                abs_path_attempt = os.path.join(self.structure_model_instance.gui_data.root_directory, current_path_in_gui_data)
                if os.path.exists(os.path.dirname(abs_path_attempt)):
                    start_dir = os.path.dirname(abs_path_attempt)
        
        potential_template_folder = os.path.join(self.structure_model_instance.gui_data.root_directory or PROJECT_ROOT_ABS, "file_templates")
        if os.path.isdir(potential_template_folder):
            start_dir = potential_template_folder

        filepath, _ = QFileDialog.getOpenFileName(self, "Select Master CPT Template File", start_dir, "RAM Concept Files (*.cpt)")
        if filepath:
            root_dir = self.structure_model_instance.gui_data.root_directory
            if root_dir and os.path.abspath(filepath).startswith(os.path.abspath(root_dir)):
                rel_path = os.path.relpath(filepath, root_dir).replace("\\", "/")
                if self.structure_model_instance.gui_data.master_cpt_template_path != rel_path:
                    self.structure_model_instance.gui_data.master_cpt_template_path = rel_path
                    self.master_cpt_template_edit.setText(rel_path) 
                    self._save_project_data_to_pickle()
                elif self.master_cpt_template_edit.text() != rel_path: 
                     self.master_cpt_template_edit.setText(rel_path)

            else: 
                if self.structure_model_instance.gui_data.master_cpt_template_path != filepath:
                    self.structure_model_instance.gui_data.master_cpt_template_path = filepath
                    self.master_cpt_template_edit.setText(filepath) 
                    self._save_project_data_to_pickle()
                elif self.master_cpt_template_edit.text() != filepath: 
                     self.master_cpt_template_edit.setText(filepath)
    
    def _save_project_data_to_pickle(self):
        if not self.structure_model_instance.gui_data.root_directory:
            print("Save aborted: Project root directory not set.")
            return False
        
        self._update_floordata_isincluded_from_cpt_table() 
        self.structure_model_instance.update_gui_included_files_from_floors()

        if self.project_manager.save_project_data():
            return True
        else:
            QMessageBox.critical(self, "Save Error", "Failed to save project data. Check console for details.")
            return False

    def _load_project_data_from_pickle(self, new_root_path: str) -> bool:
        original_root = self.structure_model_instance.gui_data.root_directory
        self.structure_model_instance.gui_data.root_directory = new_root_path
        self.project_manager.model = self.structure_model_instance 

        loaded_ok, model_instance = self.project_manager.load_project_data()
        
        if model_instance:
            self.structure_model_instance = model_instance 
            self.project_manager.model = self.structure_model_instance
            self.pdf_processor.structure_model = self.structure_model_instance
            self.cpt_manager.structure_model = self.structure_model_instance
        
        if not loaded_ok: 
            if self.structure_model_instance.gui_data.root_directory != new_root_path: 
                 self.structure_model_instance.gui_data.root_directory = original_root 
        
        return loaded_ok

    def select_or_create_project_directory(self):
        current_root = self.structure_model_instance.gui_data.root_directory
        path = QFileDialog.getExistingDirectory(self, "Select Project Directory (New or Existing)",
                                                current_root if current_root and os.path.isdir(current_root) else PROJECT_ROOT_ABS)
        if not path: 
            if not current_root: 
                QMessageBox.information(self, "Project Directory", "No project directory selected. Please select a directory to begin.")
            return

        if path == current_root:
            QMessageBox.information(self, "Project Directory", f"Directory '{path}' is already the active project root.")
            return

        self.project_manager._check_or_create_subfolders(path) 
        
        loaded_successfully = self._load_project_data_from_pickle(path) 
        
        if loaded_successfully:
            QMessageBox.information(self, "Project Opened", f"Successfully opened project from:\n{path}")
        else: 
            QMessageBox.information(self, "New Project", 
                                    f"No existing project found in '{path}'.\nInitializing a new project here.")
            self._copy_file_templates(path)
            if not self._save_project_data_to_pickle(): 
                QMessageBox.critical(self, "Error", "Failed to save initial data for the new project.")

        self._update_gui_from_model_data()
        self._update_all_explorers_and_tables()


    def _update_cpt_version_explorer_listbox(self):
        self.cpt_version_explorer_listbox.clear()
        ram_concept_path = self.project_manager.get_ram_concept_base_path() 

        if not ram_concept_path:
            self.cpt_version_explorer_listbox.addItem("Project folder not set."); return
        if not os.path.isdir(ram_concept_path):
            self.cpt_version_explorer_listbox.addItem(f"'{RAM_CONCEPT_DIR_NAME}' folder not found.")
            return

        versions_found = False
        version_items_data = [] 
        for item_name in os.listdir(ram_concept_path):
            full_path = os.path.join(ram_concept_path, item_name)
            if os.path.isdir(full_path):
                version_items_data.append({'name': item_name, 'path': full_path})
        
        sorted_version_items = sorted(
            version_items_data, 
            key=lambda item: (self.project_manager._parse_version_string_semantic(item['name'].split(' ')[0]) or (0,0,-1), item['name'].lower()), 
            reverse=True
        )

        for item_data in sorted_version_items:
            list_item = QListWidgetItem(item_data['name'])
            list_item.setData(Qt.ItemDataRole.UserRole, item_data['path']) 
            self.cpt_version_explorer_listbox.addItem(list_item)
            
            if self.structure_model_instance.gui_data.cpt_active_folder_path == item_data['path']:
                list_item.setSelected(True)
                self.cpt_version_explorer_listbox.setCurrentItem(list_item) 
                list_item.setBackground(QColor("#D5E8D4")) 
            versions_found = True

        if not versions_found:
            self.cpt_version_explorer_listbox.addItem(f"(No versions found in '{RAM_CONCEPT_DIR_NAME}')")
        self._on_cpt_version_selection_changed() 


    def set_active_cpt_version_with_sync(self):
        selected_items = self.cpt_version_explorer_listbox.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a CPT version to set as active.")
            return
        
        selected_version_item = selected_items[0]
        new_active_cpt_version_name = selected_version_item.text()
        new_active_cpt_version_path = selected_version_item.data(Qt.ItemDataRole.UserRole)

        if not new_active_cpt_version_path or not os.path.isdir(new_active_cpt_version_path):
            QMessageBox.critical(self, "Path Error", f"Path for CPT version '{new_active_cpt_version_name}' is invalid.")
            return

        cpts_in_new_version_folder = {}
        try:
            for item_name in os.listdir(new_active_cpt_version_path):
                if item_name.lower().endswith(".cpt"):
                    full_path = os.path.join(new_active_cpt_version_path, item_name)
                    if os.path.isfile(full_path):
                        cpts_in_new_version_folder[item_name] = full_path
        except Exception as e:
            QMessageBox.critical(self, "Error Scanning Version", f"Could not read CPT files from '{new_active_cpt_version_name}': {e}")
            return

        reply = QMessageBox.question(self, "Confirm Set Active CPT Version",
                                     f"Set '{new_active_cpt_version_name}' as active?\n"
                                     "This will clear the current CPT list and populate it with files from the selected version.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.Yes)
        if reply == QMessageBox.StandardButton.No:
            return

        self.project_manager.set_active_version(new_active_cpt_version_name, new_active_cpt_version_path)
        
        self.structure_model_instance.clear_all_floor_data() 

        project_root = self.structure_model_instance.gui_data.root_directory
        for index, (ram_filename, cpt_abs_path) in enumerate(cpts_in_new_version_folder.items()):
            internal_floor_name = f"Floor_{ram_filename.replace('.cpt', '')}_{index}" 
            new_fd = FloorData(
                floor_name=internal_floor_name,
                floor_index=index + 1,
                ram_model_name=ram_filename,
                is_included=True, 
                typical_count=1,
                structure_model=self.structure_model_instance,
            )
            new_fd.update_paths(cpt_abs_path, project_root)
            self.structure_model_instance.add_floor(new_fd)
        
        self.structure_model_instance.update_gui_included_files_from_floors() 
        self._save_project_data_to_pickle() 
        self._update_gui_from_model_data() 
        self._update_cpt_version_explorer_listbox() 
        
        QMessageBox.information(self, "Active CPT Version Set", f"CPT Version '{new_active_cpt_version_name}' is now active. CPT list updated.")

    def _set_active_pdf_version_from_explorer(self):
        selected_items = self.pdf_version_explorer_listbox.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a PDF version to set as active.")
            return
        
        item_data = selected_items[0].data(Qt.ItemDataRole.UserRole) 
        if not item_data or not item_data.get('path') or not item_data.get('pdf_filename'):
            QMessageBox.critical(self, "Error", "Selected PDF version item has invalid data.")
            return

        self.project_manager.set_active_pdf_binder_version(
            version_folder_name=item_data['name'],
            version_folder_path=item_data['path'],
            pdf_filename_in_folder=item_data['pdf_filename']
        )

        self._save_project_data_to_pickle()
        self._update_gui_from_model_data() 
        self._update_pdf_version_explorer_listbox() 
        QMessageBox.information(self, "Active PDF Version Set", f"PDF Version '{item_data['name']}' is now active.")


    def _on_cpt_table_item_changed(self, item: QTableWidgetItem):
        # This method is now effectively empty as all columns in the floor_data_table
        # are set to be read-only. Editing is handled by the new story_data_table.
        pass

    def _on_cpt_include_checkbox_changed(self, state, row: int, floor_name_key: str):
        if self._programmatic_checkbox_update or self._table_update_in_progress or self._programmatic_ui_update:
            return

        floor_data_obj = self.structure_model_instance.get_floor_by_name(floor_name_key)
        if floor_data_obj:
            new_state = bool(state)
            if floor_data_obj.is_included != new_state:
                floor_data_obj.is_included = new_state
                self.structure_model_instance.update_gui_included_files_from_floors()
                self._update_loaded_vars_display() 
                self._save_project_data_to_pickle()

    def _sync_cpt_checkboxes_to_floor_data(self):
        self._programmatic_checkbox_update = True
        for r in range(self.floor_data_table.rowCount()):
            filename_item = self.floor_data_table.item(r, self.COL_FD_CPT_FILENAME)
            if not filename_item: continue
            floor_name_key = filename_item.data(Qt.ItemDataRole.UserRole)
            floor_data_obj = self.structure_model_instance.get_floor_by_name(floor_name_key)
            
            checkbox_container = self.floor_data_table.cellWidget(r, self.COL_FD_INCLUDE)
            if checkbox_container and floor_data_obj:
                checkbox = checkbox_container.layout().itemAt(0).widget()
                checkbox.setChecked(floor_data_obj.is_included)
        self._programmatic_checkbox_update = False

    def _update_floordata_isincluded_from_cpt_table(self):
        if self._table_update_in_progress: return

        for r in range(self.floor_data_table.rowCount()):
            filename_item = self.floor_data_table.item(r, self.COL_FD_CPT_FILENAME)
            if not filename_item: continue
            floor_name_key = filename_item.data(Qt.ItemDataRole.UserRole)
            floor_data_obj = self.structure_model_instance.get_floor_by_name(floor_name_key)
            
            checkbox_container = self.floor_data_table.cellWidget(r, self.COL_FD_INCLUDE)
            if checkbox_container and floor_data_obj:
                checkbox = checkbox_container.layout().itemAt(0).widget()
                floor_data_obj.is_included = checkbox.isChecked()
    
    
    def _on_pdf_page_checkbox_changed(self, state, row: int, model_page_identifier: str, field_name: str):
        if self._programmatic_pdf_checkbox_update or self._pdf_table_update_in_progress or self._programmatic_ui_update:
            return

        live_model_page = self.structure_model_instance.get_model_page_by_identifier(model_page_identifier)
        if not live_model_page: return

        if field_name == "is_ga":
            live_model_page.is_selected_ga = bool(state)

            # --- Core Sync and Update Logic ---
            self._calculate_and_assign_pdf_ga_numbers()
            self._sync_floor_data_with_ga_selections()

            # Refresh all UI elements
            self._refresh_pdf_table_display()
            self._update_story_data_table()
            self._update_floor_data_table()
            self._update_ga_count_warnings()

            # Save the new state
            self._save_project_data_to_pickle()
        

    def _sync_pdf_checkboxes_to_model_page_data(self):
        self._programmatic_pdf_checkbox_update = True
        for r in range(self.pdf_pages_table.rowCount()):
            page_ref_item = self.pdf_pages_table.item(r, self.COL_PP_PDF_PAGE_REF)
            if not page_ref_item: continue
            page_identifier = page_ref_item.data(Qt.ItemDataRole.UserRole)
            model_page = self.structure_model_instance.get_model_page_by_identifier(page_identifier)
            if not model_page: continue

            ga_cb_container = self.pdf_pages_table.cellWidget(r, self.COL_PP_IS_GA)
            if ga_cb_container:
                ga_cb_container.layout().itemAt(0).widget().setChecked(model_page.is_selected_ga)

        self._programmatic_pdf_checkbox_update = False

    def _update_all_explorers_and_tables(self):
        print("Updating all explorers and tables...")
        self._programmatic_ui_update = True # Prevent premature signals during this comprehensive update
        
        self._update_cpt_version_explorer_listbox()
        self._update_pdf_version_explorer_listbox()
        
        # Crucial: Perform sync after PDF document is loaded and GA statuses are known
        # The _update_pdf_pages_table calls _calculate_and_assign_pdf_ga_numbers
        # but a more explicit sync might be needed if project loaded or versions changed.
        if self.structure_model_instance.pdf_document:
             self._calculate_and_assign_pdf_ga_numbers() # Ensure GA numbers are fresh
             self._perform_automatic_ga_sync() # Establish/update links

        self._update_floor_data_table() 
        self._update_pdf_pages_table()  
        
        self._update_loaded_vars_display()
        self._update_ga_count_warnings()

        
        self._programmatic_ui_update = False

    def _update_floor_data_table(self):
        self._table_update_in_progress = True
        current_selection = self.floor_data_table.currentRow()
        self.floor_data_table.setRowCount(0)

        ordered_floor_data_list = self.structure_model_instance.get_ordered_floors()

        for floor_data_obj in ordered_floor_data_list:
            if not isinstance(floor_data_obj, FloorData): continue
            row_position = self.floor_data_table.rowCount()
            self.floor_data_table.insertRow(row_position)
            self._update_floor_data_table_row(row_position, floor_data_obj)

        self._table_update_in_progress = False
        if 0 <= current_selection < self.floor_data_table.rowCount():
            self.floor_data_table.selectRow(current_selection)
        else:
            self._on_floor_table_selection_changed()

    def _update_pdf_pages_table(self):
            self._pdf_table_update_in_progress = True
            current_selection = self.pdf_pages_table.currentRow()
            self.pdf_pages_table.setRowCount(0)

            if not self.structure_model_instance.pdf_document:
                self.pdf_pages_table.setRowCount(1)
                item = QTableWidgetItem("No active PDF document loaded or PDF has no pages.")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.pdf_pages_table.setItem(0,0, item)
                self.pdf_pages_table.setSpan(0,0, 1, self.NUM_PP_COLUMNS) # Span across all columns
                self._pdf_table_update_in_progress = False
                self._update_ga_count_warnings() # Update warning even if no PDF
                return

            self._calculate_and_assign_pdf_ga_numbers() # Ensure GA numbers are fresh

            for model_page in self.structure_model_instance.all_pdf_pages:
                row_position = self.pdf_pages_table.rowCount()
                self.pdf_pages_table.insertRow(row_position)
                self._update_pdf_pages_table_row(row_position, model_page)

            self._pdf_table_update_in_progress = False
            if 0 <= current_selection < self.pdf_pages_table.rowCount():
                self.pdf_pages_table.selectRow(current_selection)
            self._update_ga_count_warnings() # Update warnings after table is repopulated

    def move_cpt_file_up(self): self._modify_cpt_table_items_order("up")
    def move_cpt_file_down(self): self._modify_cpt_table_items_order("down")
    def remove_selected_file_from_cpt_list(self): self._remove_selected_cpt_from_list()
    def remove_all_files_from_cpt_list(self): self._remove_all_cpts_from_list()
    def _check_all_cpt_include_boxes(self): self._set_all_cpt_include_checkboxes(True)
    def _uncheck_all_cpt_include_boxes(self): self._set_all_cpt_include_checkboxes(False)

    def _on_cpt_version_selection_changed(self): 
        has_selection = bool(self.cpt_version_explorer_listbox.selectedItems())
        self.set_active_cpt_version_btn.setEnabled(has_selection)
        self.delete_cpt_version_btn.setEnabled(has_selection)
        self.create_next_cpt_version_btn.setEnabled(bool(self.structure_model_instance.gui_data.root_directory))

    def _modify_cpt_table_items_order(self, action: str):
        selected_model_indices = self.floor_data_table.selectionModel().selectedRows()
        if not selected_model_indices or len(selected_model_indices) > 1:
            QMessageBox.information(self, "Selection Error", "Please select exactly one row to move.")
            return

        selected_visual_row_idx = selected_model_indices[0].row()
        ordered_floors = self.structure_model_instance.get_ordered_floors()

        if not (0 <= selected_visual_row_idx < len(ordered_floors)):
            return
        
        
        

        # --- Re-order the list in memory ---
        moved_item = ordered_floors.pop(selected_visual_row_idx)
        new_visual_row_idx = -1

        if action == "up" and selected_visual_row_idx > 0:
            new_visual_row_idx = selected_visual_row_idx - 1
            ordered_floors.insert(new_visual_row_idx, moved_item)
        elif action == "down" and selected_visual_row_idx < len(ordered_floors):
            new_visual_row_idx = selected_visual_row_idx + 1
            ordered_floors.insert(new_visual_row_idx, moved_item)
        else:
            # Action was not possible (e.g., moving top item up), put item back and exit
            ordered_floors.insert(selected_visual_row_idx, moved_item)
            return
        
        
        
        

        # --- Re-assign the floor_index for the entire list to match the new visual order ---
        for i, fd_obj in enumerate(ordered_floors):
            fd_obj.floor_index = i  # Re-number from 0 to N

        # --- CRUCIAL: Re-run the sync and update all UI ---
        # This re-links CPTs and PDFs based on the new indices
        self._perform_automatic_ga_sync()
        
        # Save the new state
        self.structure_model_instance.update_gui_included_files_from_floors()
        self._save_project_data_to_pickle()

        # Update all tables to reflect the new order and links
        self._update_floor_data_table()
        self._update_story_data_table()
        self._update_ga_count_warnings()

        # Re-select the item in its new position for a smooth user experience
        if 0 <= new_visual_row_idx < self.floor_data_table.rowCount():
            self.floor_data_table.selectRow(new_visual_row_idx)
        self._on_floor_table_selection_changed()

    def _remove_selected_cpt_from_list(self):
        selected_model_indices = self.floor_data_table.selectionModel().selectedRows()
        if not selected_model_indices:
            QMessageBox.information(self, "No Selection", "Please select a CPT row to remove.")    
            return
        
        visual_row_idx = selected_model_indices[0].row()
        filename_item = self.floor_data_table.item(visual_row_idx, self.COL_FD_CPT_FILENAME)
        if not filename_item: return
        
        floor_name_key = filename_item.data(Qt.ItemDataRole.UserRole) 
        cpt_name_display = filename_item.text() 

        reply = QMessageBox.question(self, "Confirm Remove from List",
                                     f"Remove '{cpt_name_display}' from project CPT list?\n"
                                     "(Does NOT delete the .cpt file from disk).",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if floor_name_key:
                self.structure_model_instance.floors_data.remove_floor(floor_name_key)
                self.structure_model_instance.floors_data.re_index_floors() 
                self.structure_model_instance.update_gui_included_files_from_floors()
                self._save_project_data_to_pickle()
                self._update_floor_data_table()
                self._update_loaded_vars_display()

    def _remove_all_cpts_from_list(self):
        if self.structure_model_instance.floors_data.floors:
            reply = QMessageBox.question(self, "Confirm Remove All CPTs",
                                         "Remove ALL CPT files from the current project list?\n"
                                         "(Does NOT delete .cpt files from disk).",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,    
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.structure_model_instance.clear_all_floor_data() 
                self._save_project_data_to_pickle()
                self._update_floor_data_table()
                self._update_loaded_vars_display()
        else:
            QMessageBox.information(self, "No CPTs", "The CPT list is already empty.")
            
    def _set_all_cpt_include_checkboxes(self, checked_state: bool):
        if self._table_update_in_progress or self._programmatic_ui_update: return
        
        self._programmatic_checkbox_update = True 
        any_change = False
        for r in range(self.floor_data_table.rowCount()):
            checkbox_container = self.floor_data_table.cellWidget(r, self.COL_FD_INCLUDE)
            if checkbox_container:
                checkbox = checkbox_container.layout().itemAt(0).widget()
                if checkbox.isChecked() != checked_state:
                    checkbox.setChecked(checked_state) 
                    any_change = True 
            
            filename_item = self.floor_data_table.item(r, self.COL_FD_CPT_FILENAME)
            if filename_item:
                floor_name_key = filename_item.data(Qt.ItemDataRole.UserRole)
                floor_data_obj = self.structure_model_instance.get_floor_by_name(floor_name_key)
                if floor_data_obj and floor_data_obj.is_included != checked_state:
                    floor_data_obj.is_included = checked_state
                    any_change = True 
        
        self._programmatic_checkbox_update = False

        if any_change:
            self.structure_model_instance.update_gui_included_files_from_floors()
            self._update_loaded_vars_display()
            self._save_project_data_to_pickle()

    def closeEvent(self, event):
        if self.structure_model_instance.gui_data.root_directory: 
            reply = QMessageBox.question(self, 'Exit Application',
                                         "Are you sure you want to exit?\n(Project data is auto-saved on change)",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else: 
                event.ignore()
        else: 
            event.accept()


    def save_project_data_explicit(self):
        if not self.structure_model_instance.gui_data.root_directory:
            QMessageBox.warning(self, "No Project Root", "Please select a project directory before saving.")
            return
        if self._save_project_data_to_pickle():
            QMessageBox.information(self, "Project Saved", "Project data saved successfully.")


    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self.floor_data_table, self.remove_selected_file_from_cpt_list)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Up), self.floor_data_table, self.move_cpt_file_up)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Down), self.floor_data_table, self.move_cpt_file_down)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S), self, self.save_project_data_explicit) 

    def _on_pdf_version_selection_changed(self):
        has_selection = bool(self.pdf_version_explorer_listbox.selectedItems())
        self.set_active_pdf_version_btn.setEnabled(has_selection)
        self.delete_pdf_version_btn.setEnabled(has_selection)
        self.process_pdf_to_cpts_btn.setEnabled(has_selection and bool(self.structure_model_instance.gui_data.current_pdf_binder_full_path))


    def _on_floor_table_selection_changed(self):
        selected_rows = self.floor_data_table.selectionModel().selectedRows()
        has_selection = bool(selected_rows)
        self.remove_file_btn.setEnabled(has_selection)
        
        can_move_up = False
        can_move_down = False
        if has_selection:
            row_index = selected_rows[0].row()
            if row_index > 0:
                can_move_up = True
            if row_index < self.floor_data_table.rowCount() - 1:
                can_move_down = True
        self.move_up_btn.setEnabled(can_move_up)
        self.move_down_btn.setEnabled(can_move_down)

    def _update_loaded_vars_display(self):
        if hasattr(self, 'included_files_summary_label'):
            gui_data = self.structure_model_instance.gui_data
            num_included = len(gui_data.included_files) if gui_data and gui_data.included_files else 0
            self.included_files_summary_label.setText(f"Number of CPTs marked 'Include': {num_included}")

    def _copy_file_templates(self, target_project_root):
        source_templates_dir = os.path.join(PROJECT_ROOT_ABS, "file_templates") 
        if not os.path.isdir(source_templates_dir):
            QMessageBox.information(self, "Templates Not Found",
                                    f"Template directory 'file_templates' not found at application level:\n{source_templates_dir}")
            try:
                os.makedirs(source_templates_dir, exist_ok=True)
                dummy_template_path = os.path.join(source_templates_dir, "default_ram_template.cpt")
                if not os.path.exists(dummy_template_path):
                    with open(dummy_template_path, "w") as f:
                        f.write("This is a placeholder CPT template. Replace with a valid RAM Concept file.")    
                    QMessageBox.information(self, "Template Created", f"A placeholder template directory and file were created at:\n{dummy_template_path}\nPlease replace the .cpt file with a valid template.")
            except Exception as e:
                QMessageBox.warning(self, "Template Creation Error", f"Could not create placeholder template directory: {e}")
                return

        target_file_templates_dir = os.path.join(target_project_root, "file_templates")
        if not os.path.exists(target_file_templates_dir):
            try:
                os.makedirs(target_file_templates_dir)
            except Exception as e:
                QMessageBox.warning(self, "Template Copy Error", f"Could not create '{target_file_templates_dir}': {e}")
                return
        
        copied_count = 0
        for item in os.listdir(source_templates_dir):
            s = os.path.join(source_templates_dir, item)
            d = os.path.join(target_file_templates_dir, item)
            if os.path.exists(d): continue 
            try:
                if os.path.isdir(s): shutil.copytree(s, d)
                elif os.path.isfile(s): shutil.copy2(s, d)
                copied_count +=1
            except Exception as e:
                QMessageBox.warning(self, "Template Copy Error", f"Error copying '{item}': {e}")
        
        if copied_count > 0:
            QMessageBox.information(self, "Templates Copied", f"{copied_count} template item(s) copied to project's 'file_templates' folder.")

    def _update_pdf_version_explorer_listbox(self):
        self.pdf_version_explorer_listbox.clear()
        pdf_binders_base_path = self.project_manager.get_pdf_binders_base_path()
        if not pdf_binders_base_path:
            self.pdf_version_explorer_listbox.addItem("Project folder not set."); return
        if not os.path.isdir(pdf_binders_base_path):
            self.pdf_version_explorer_listbox.addItem(f"'{PDF_BINDERS_DIR_NAME}' folder not found.")
            return
        
        versions_found = False
        version_items = []
        for item_name in os.listdir(pdf_binders_base_path):
            full_path = os.path.join(pdf_binders_base_path, item_name)
            if os.path.isdir(full_path):
                pdf_file_in_version = None
                for sub_item in os.listdir(full_path):
                    if sub_item.lower().endswith(".pdf"):
                        pdf_file_in_version = sub_item
                        break 
                if pdf_file_in_version:
                    version_items.append({'name': item_name, 'path': full_path, 'pdf_filename': pdf_file_in_version})
        
        sorted_version_items = sorted(version_items, key=lambda item: (self.project_manager._parse_version_string_semantic(item['name'].split(' ')[0]) or (0,0,-1), item['name'].lower()), reverse=True)
        
        for item_data in sorted_version_items:
            list_item = QListWidgetItem(item_data['name'])
            list_item.setData(Qt.ItemDataRole.UserRole, item_data) 
            self.pdf_version_explorer_listbox.addItem(list_item)
            if self.structure_model_instance.gui_data.active_pdf_binder_version_path == item_data['path']:    
                list_item.setSelected(True)
                self.pdf_version_explorer_listbox.setCurrentItem(list_item)
                list_item.setBackground(QColor("#D5E8D4"))
            versions_found = True
            
        if not versions_found:
            self.pdf_version_explorer_listbox.addItem(f"(No PDF versions found in '{PDF_BINDERS_DIR_NAME}')")    
        self._on_pdf_version_selection_changed()

    def _import_pdf_to_new_version_gui(self):
        if not self.structure_model_instance.gui_data.root_directory:
            QMessageBox.warning(self, "Project Not Set", "Please set a project root directory first.")
            return
        
        source_pdf_path, _ = QFileDialog.getOpenFileName(self, "Select PDF Binder to Import",
                                                       self.structure_model_instance.gui_data.root_directory,    
                                                       "PDF Files (*.pdf)")
        if not source_pdf_path:
            return
        
        description_suffix, ok = QInputDialog.getText(self, "PDF Version Description",
                                                    "Enter a brief description for this new PDF version:",    
                                                    text=f"Imported {os.path.basename(source_pdf_path)}")    
        if not ok: return
        if not description_suffix: description_suffix = f"Imported {os.path.basename(source_pdf_path)}"
        
        new_version_folder_path, pdf_filename_in_version = self.project_manager.create_new_pdf_binder_version(    
            source_pdf_abs_path=source_pdf_path,
            change_type="Minor", 
            description_suffix=description_suffix
        )
        
        if new_version_folder_path and pdf_filename_in_version:
            self._update_pdf_version_explorer_listbox()
            QMessageBox.information(self, "PDF Version Created", f"New PDF version '{os.path.basename(new_version_folder_path)}' created with '{pdf_filename_in_version}'.")
            reply_set_active = QMessageBox.question(self, "Set Active?",
                                                  f"Do you want to set '{os.path.basename(new_version_folder_path)}' as the active PDF version?",
                                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                  QMessageBox.StandardButton.Yes)
            if reply_set_active == QMessageBox.StandardButton.Yes:
                for i in range(self.pdf_version_explorer_listbox.count()):
                    item = self.pdf_version_explorer_listbox.item(i)
                    item_data = item.data(Qt.ItemDataRole.UserRole)
                    if item_data and item_data['path'] == new_version_folder_path:
                        self.pdf_version_explorer_listbox.setCurrentItem(item)
                        self._set_active_pdf_version_from_explorer()
                        break
            self._save_project_data_to_pickle()

    def _delete_selected_pdf_version(self):
        selected_items = self.pdf_version_explorer_listbox.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a PDF version to delete.")
            return
        
        item_data = selected_items[0].data(Qt.ItemDataRole.UserRole)
        version_name_to_delete = item_data['name']
        version_path_to_delete = item_data['path']
        
        if not version_path_to_delete or not os.path.isdir(version_path_to_delete):
            QMessageBox.critical(self, "Error", f"Path for PDF version '{version_name_to_delete}' is invalid."); return
        
        reply = QMessageBox.question(self, "Confirm Delete PDF Version",
                                     f"Are you sure you want to permanently delete PDF version:\n'{version_name_to_delete}'\n"
                                     f"and all its contents from:\n{version_path_to_delete}\n\nThis cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,    
                                     QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(version_path_to_delete)
                QMessageBox.information(self, "Deleted", f"PDF Version '{version_name_to_delete}' deleted.")    
                was_active = False
                if self.structure_model_instance.gui_data.active_pdf_binder_version_path == version_path_to_delete:
                    self.project_manager.set_active_pdf_binder_version(None, None, None)
                    was_active = True
                
                self._update_pdf_version_explorer_listbox()
                if was_active:
                    self._update_gui_from_model_data() 
                    self._save_project_data_to_pickle()
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Failed to delete PDF version '{version_name_to_delete}': {e}")

    def process_pdf_and_create_cpts(self):
        active_pdf_full_path = self.structure_model_instance.gui_data.current_pdf_binder_full_path
        if not active_pdf_full_path or not os.path.exists(active_pdf_full_path):
            QMessageBox.warning(self, "Active PDF Not Found", "Please select and set an active PDF binder version first.")
            return

        master_cpt_template_path_from_gui = self.structure_model_instance.gui_data.master_cpt_template_path
        project_root = self.structure_model_instance.gui_data.root_directory
        if not project_root:
            QMessageBox.critical(self, "Project Error", "Project root directory not set.")
            return

        abs_master_cpt_template = os.path.join(project_root, master_cpt_template_path_from_gui) \
            if not os.path.isabs(master_cpt_template_path_from_gui) else master_cpt_template_path_from_gui

        if not master_cpt_template_path_from_gui or not os.path.exists(abs_master_cpt_template):
            QMessageBox.warning(self, "Template CPT Not Found", f"Master CPT template not found at: {abs_master_cpt_template}\nPlease specify a valid template.")
            return

        # Ensure PDF GA numbers are calculated and assigned before filtering
        self._calculate_and_assign_pdf_ga_numbers()
        
        ga_model_pages_to_process = []
        for mp in self.structure_model_instance.all_pdf_pages:
            if mp.is_selected_ga and hasattr(mp, 'ga_number_display') and mp.ga_number_display != "-":
                try:
                    # Store the integer GA number for processing
                    mp.temp_ga_number_for_cpt_creation = int(mp.ga_number_display) 
                    ga_model_pages_to_process.append(mp)
                except ValueError:
                    print(f"Warning: Could not parse GA number '{mp.ga_number_display}' for page '{mp.page_name}'. Skipping for CPT creation.")
        
        if not ga_model_pages_to_process:
            QMessageBox.information(self, "No GAs Selected", "No PDF pages are marked as 'GA' (or GA numbers are invalid) to process. Please select GAs in the PDF table first.")
            return
        
        # Sort by the temporary GA number to ensure CPTs are processed in GA order
        ga_model_pages_to_process.sort(key=lambda x: x.temp_ga_number_for_cpt_creation)


        version_description = f"CPTs from GAs in '{self.structure_model_instance.gui_data.active_pdf_binder_version_name or os.path.basename(active_pdf_full_path)}'"
        new_cpt_version_path = self.project_manager.create_new_ram_version(
            change_type="Minor",
            description_suffix=version_description,
            copy_from_active=False 
        )

        if not new_cpt_version_path:
            QMessageBox.critical(self, "CPT Version Creation Failed", "Could not create a new RAM Concept (CPT) version folder.")
            return
        new_cpt_version_name = os.path.basename(new_cpt_version_path)

        created_cpts_count = 0
        newly_created_floor_data_objects: list[FloorData] = []

        for ga_model_page in ga_model_pages_to_process:
            ga_num = ga_model_page.temp_ga_number_for_cpt_creation 
            page_name_part = ga_model_page.page_name or f"Page{ga_model_page.page_properties.page_index if ga_model_page.page_properties else 'Unknown'}"
            sanitized_page_name_for_cpt = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in page_name_part)
            cpt_filename = f"GA_{ga_num}_{sanitized_page_name_for_cpt}.cpt"
            
            # Ensure internal_floor_name is unique if adding to existing list, though here we usually clear first
            internal_floor_name_base = f"FloorData_GA_{ga_num}_{sanitized_page_name_for_cpt}"
            internal_floor_name = internal_floor_name_base
            counter = 1
            while self.structure_model_instance.floors_data.get_floor_by_name(internal_floor_name): # Check for collisions if not clearing list
                internal_floor_name = f"{internal_floor_name_base}_{counter}"
                counter +=1

            fd_stub = FloorData(
                floor_name=internal_floor_name,
                floor_index=ga_num, 
                ram_model_name=cpt_filename, 
                ga_page_fitz=ga_model_page.page_fitz, 
                _ga_page_index=ga_model_page.page_properties.page_index if ga_model_page.page_properties else None,
                pdf_page_ref_text=f"From GA {ga_num} ({ga_model_page.page_name})", 
                linked_pdf_page_identifier=ga_model_page.page_name, 
                is_included=True,
                typical_count=1,
                structure_model=self.structure_model_instance
            )

            if self.cpt_manager.create_cpt_from_template_for_floor(fd_stub, new_cpt_version_path):
                created_cpts_count += 1
                newly_created_floor_data_objects.append(fd_stub)
            else:
                QMessageBox.warning(self, "CPT Creation Failed", f"Failed to create CPT for GA {ga_num} ({ga_model_page.page_name}).")

        if created_cpts_count == 0 and ga_model_pages_to_process:
            QMessageBox.warning(self, "No CPTs Created", "Although GAs were selected, no CPT files were successfully created.")
            try: shutil.rmtree(new_cpt_version_path)
            except Exception as e: print(f"Could not clean up CPT version folder {new_cpt_version_path} after CPT creation failure: {e}")
            return
        
        reply_replace = QMessageBox.question(self, "Replace Floor Data?",
                                       f"{created_cpts_count} CPT(s) created from GAs and placed in new CPT version '{new_cpt_version_name}'.\n"
                                       "Do you want to REPLACE the current CPT file list with these new template CPTs "
                                       "and set this new CPT version as active?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.Yes)
        if reply_replace == QMessageBox.StandardButton.Yes:
            self.structure_model_instance.clear_all_floor_data()
            for fd_new in newly_created_floor_data_objects:
                self.structure_model_instance.add_floor(fd_new)
            
            # Set the new version as active
            self.project_manager.set_active_version(new_cpt_version_name, new_cpt_version_path)
            self.structure_model_instance.update_gui_included_files_from_floors() # Update included files in GUIData
            
            self._update_gui_from_model_data() # This will call table updates
            self._update_cpt_version_explorer_listbox() # Highlight new active version
            
            # Ensure new active version is selected in listbox
            for i in range(self.cpt_version_explorer_listbox.count()):
                if self.cpt_version_explorer_listbox.item(i).text() == new_cpt_version_name:
                    self.cpt_version_explorer_listbox.setCurrentRow(i)
                    # Also visually update the item background if not handled by _on_cpt_version_selection_changed
                    self.cpt_version_explorer_listbox.item(i).setBackground(QColor("#D5E8D4")) 
                    break
            
            self._save_project_data_to_pickle()
            QMessageBox.information(self, "PDF Processed",
                                    f"{created_cpts_count} template CPTs created in CPT version '{new_cpt_version_name}'.\n"
                                    f"This CPT version is now active, and the CPT list has been updated.")
        else:
            QMessageBox.information(self, "PDF Processed (No Change to Active List)",
                                    f"{created_cpts_count} template CPTs created in CPT version '{new_cpt_version_name}'.\n"
                                    "The current CPT list and active CPT version remain unchanged.")
            self._update_cpt_version_explorer_listbox() 
        
        self._update_ga_count_warnings()

    def create_next_ram_version_gui(self):
        change_types = ["Minor", "Moderate", "Breaking"]
        change_type, ok = QInputDialog.getItem(self, "Select CPT Version Change Type",
                                               "Select the type of version change:",
                                               change_types, 0, False)
        if not ok or not change_type: return
        
        description_suffix, ok = QInputDialog.getText(self, "CPT Version Description",
                                                    "Enter a brief description for this new CPT version:",    
                                                    text=f"{change_type} Update")
        if not ok: return 
        if not description_suffix: description_suffix = f"{change_type} Update"
        
        copy_active = False
        if self.structure_model_instance.gui_data.cpt_active_folder_path and \
           os.path.isdir(self.structure_model_instance.gui_data.cpt_active_folder_path):
            reply_copy = QMessageBox.question(self, "Copy Contents?",
                                              f"Do you want to copy the contents from the current active CPT version\n"
                                              f"'{self.structure_model_instance.gui_data.cpt_active_folder_name}'\n"
                                              f"into this new CPT version?",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,    
                                              QMessageBox.StandardButton.Yes)
            if reply_copy == QMessageBox.StandardButton.Yes:
                copy_active = True
                
        new_version_path = self.project_manager.create_new_ram_version(
            change_type=change_type,
            description_suffix=description_suffix,
            copy_from_active=copy_active
        )
        
        if new_version_path:
            self._update_cpt_version_explorer_listbox()
            new_version_name = os.path.basename(new_version_path)
            reply_set_active = QMessageBox.question(self, "Set Active CPT Version?",
                                                    f"New CPT version '{new_version_name}' created.\n"
                                                    "Do you want to set it as the active CPT version?",
                                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                    QMessageBox.StandardButton.Yes)
            if reply_set_active == QMessageBox.StandardButton.Yes:
                for i in range(self.cpt_version_explorer_listbox.count()):
                    item = self.cpt_version_explorer_listbox.item(i)
                    if item.text() == new_version_name:
                        self.cpt_version_explorer_listbox.setCurrentItem(item)
                        self.set_active_cpt_version_with_sync() 
                        break
            self._save_project_data_to_pickle()

    def delete_selected_cpt_version(self):
        items = self.cpt_version_explorer_listbox.selectedItems()
        if not items:
            QMessageBox.warning(self, "No Selection", "Please select a CPT version to delete."); return
            
        version_name_to_delete = items[0].text()
        version_path_to_delete = items[0].data(Qt.ItemDataRole.UserRole)
        
        if not version_path_to_delete or not os.path.isdir(version_path_to_delete):
            QMessageBox.critical(self, "Error", f"Path for CPT version '{version_name_to_delete}' is invalid."); return
            
        reply = QMessageBox.question(self, "Confirm Delete CPT Version",
                                     f"Are you sure you want to permanently delete CPT version:\n'{version_name_to_delete}'\n"
                                     f"and all its contents from:\n{version_path_to_delete}\n\nThis cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,    
                                     QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(version_path_to_delete)
                QMessageBox.information(self, "Deleted", f"CPT Version '{version_name_to_delete}' deleted.")    
                was_active = False
                if self.structure_model_instance.gui_data.cpt_active_folder_path == version_path_to_delete:    
                    self.project_manager.set_active_version(None, None)
                    self.structure_model_instance.clear_all_floor_data() 
                    was_active = True
                
                self._update_cpt_version_explorer_listbox()
                if was_active:
                    self._update_gui_from_model_data()
                    self._save_project_data_to_pickle()
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Failed to delete CPT version '{version_name_to_delete}': {e}")

    def get_settings_dict(self) -> dict:
        settings = {}
        if self.structure_model_instance and self.structure_model_instance.gui_data:
            settings = self.structure_model_instance.gui_data.to_variable_dict()
        else:
            settings = SETTINGS_DEFAULT.copy()
            
        ordered_floor_data_objects = self.structure_model_instance.get_ordered_floors()
        files_data_for_script = []
        for fd in ordered_floor_data_objects:
            if fd.is_included: 
                fd_dict = {
                    "floor_name": fd.floor_name,
                    "floor_index": fd.floor_index,
                    "ram_model_name": fd.ram_model_name,
                    "filename": fd.ram_model_name, 
                    "filepath": fd.filepath,
                    "listpath": fd.listpath,
                    "typical_count": fd.typical_count,
                    "typical": fd.typical_count, 
                    "pdf_page_ref_text": fd.pdf_page_ref_text, 
                    "is_included": fd.is_included,
                }
                files_data_for_script.append(fd_dict)
        settings["FILES"] = files_data_for_script
        settings["FILES_DATA"] = files_data_for_script 
        
        for key_default, default_value in SETTINGS_DEFAULT.items():
            if key_default not in settings: 
                 if hasattr(self.structure_model_instance.gui_data, key_default.lower()):
                     settings[key_default] = getattr(self.structure_model_instance.gui_data, key_default.lower())
                 else:
                     settings[key_default] = default_value
        return settings

    def save_project_data_explicit(self):
        if not self.structure_model_instance.gui_data.root_directory:
            QMessageBox.warning(self, "No Project Root", "Please select a project directory before saving.")
            return
        if self._save_project_data_to_pickle():
            QMessageBox.information(self, "Project Saved", "Project data saved successfully.")

    def save_project_data_as(self):
        new_project_path = QFileDialog.getExistingDirectory(self, "Save Project As - Select Directory",
                                                            self.structure_model_instance.gui_data.root_directory or PROJECT_ROOT_ABS)
        if not new_project_path: return
        
        current_pickle_path_obj = self.project_manager.get_pickle_data_path() 
        current_pickle_path = str(current_pickle_path_obj) if current_pickle_path_obj else ""


        new_potential_pickle_path = os.path.join(new_project_path, self.project_manager.PICKLED_DATA_DIR_NAME, PICKLED_DATA_FILENAME)
        
        if os.path.exists(new_potential_pickle_path) and \
           (not current_pickle_path or os.path.abspath(current_pickle_path).lower() != os.path.abspath(new_potential_pickle_path).lower()):
            reply = QMessageBox.question(self, "Overwrite Existing Project?",
                                         f"A project data file already exists at:\n{new_potential_pickle_path}\n"
                                         "Overwrite it with the current project's data?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,    
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No: return
            
        old_root_dir_before_save_as = self.structure_model_instance.gui_data.root_directory

        self.structure_model_instance.gui_data.root_directory = new_project_path
        self.project_manager.model = self.structure_model_instance 
        
        self.project_manager._check_or_create_subfolders(new_project_path)
        
        for fd_obj in self.structure_model_instance.floors_data.floors.values():
            if fd_obj.filepath: 
                fd_obj.update_paths(fd_obj.filepath, new_project_path) 
                
        if self._save_project_data_to_pickle(): 
            self._copy_file_templates(new_project_path)
            self._update_gui_from_model_data() 
            self._update_all_explorers_and_tables() 
            QMessageBox.information(self, "Project Saved As", f"Project data saved to:\n'{new_project_path}'.") 
        else:
            QMessageBox.critical(self, "Save As Error", "Failed to save project to the new location.")
            self.structure_model_instance.gui_data.root_directory = old_root_dir_before_save_as 
            self.project_manager.model = self.structure_model_instance 

    def wrapped_run_click(self): 
        s = self.get_settings_dict()
        if s: PlaceholderScripts.run_click(s, self)
    def wrapped_validate_settings(self): 
        s = self.get_settings_dict()
        if s: PlaceholderScripts.validate_settings_wrapped(s, self)
    def wrapped_get_data_click(self): 
        s = self.get_settings_dict()
        if s: PlaceholderScripts.get_data_click(s, self)

    def _launch_ram_operations_module_window(self): # type: ignore
        if not self.structure_model_instance:
            QMessageBox.critical(self, "Error", "StructureModel not initialized. Cannot open RAM Operations Module.")
            return

        if self.ram_api_operations_module_window is None or not self.ram_api_operations_module_window.isVisible():
            self.ram_api_operations_module_window = RamApiGuiPyQt6(
                structure_model=self.structure_model_instance,
                parent=self
            )
        self.ram_api_operations_module_window.show()
        self.ram_api_operations_module_window.activateWindow()
        self.ram_api_operations_module_window.raise_()


    def _launch_load_rundown_window(self):
        if not self.structure_model_instance or \
           not self.cpt_manager or \
           not self.project_manager:
            QMessageBox.critical(self, "Error", "Core components not initialized. Cannot open Load Rundown.")
            return

        if self.load_rundown_dialog is None or not self.load_rundown_dialog.isVisible():
            self.load_rundown_dialog = LoadRundownWindow(
                structure_model=self.structure_model_instance,
                cpt_manager=self.cpt_manager,
                project_manager=self.project_manager,
                parent=self
            )
        self.load_rundown_dialog.show()
        self.load_rundown_dialog.activateWindow()
        self.load_rundown_dialog.raise_()

    def _update_floor_data_table_row(self, row: int, floor_data_obj: FloorData):
        self._table_update_in_progress = True

        # COL_FD_INCLUDE: Include Checkbox
        checkbox_widget_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget_container)
        checkbox_layout.setContentsMargins(5,0,5,0); checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        include_cb = QCheckBox()
        include_cb.setChecked(getattr(floor_data_obj, 'is_included', False))
        include_cb.stateChanged.connect(lambda state, r=row, fd_key=floor_data_obj.floor_name: self._on_cpt_include_checkbox_changed(state, r, fd_key))
        checkbox_layout.addWidget(include_cb)
        self.floor_data_table.setCellWidget(row, self.COL_FD_INCLUDE, checkbox_widget_container)

        # COL_FD_GA_NUMBER: GA Number (Text, from linked PDF GA or floor_index)
        ga_number_text = "-" # Default if not a linked GA
        if floor_data_obj.linked_pdf_page_identifier:
            linked_model_page = self.structure_model_instance.get_model_page_by_identifier(floor_data_obj.linked_pdf_page_identifier)
            if linked_model_page and linked_model_page.is_selected_ga and \
               hasattr(linked_model_page, 'ga_number_display') and linked_model_page.ga_number_display != "-":
                try:
                    # Check if the CPT's floor_index matches the GA number of the linked PDF page
                    if floor_data_obj.floor_index == int(linked_model_page.ga_number_display):
                        ga_number_text = str(linked_model_page.ga_number_display)
                except ValueError:
                    pass # Should not happen if ga_number_display is correctly formatted
        
        ga_number_item = QTableWidgetItem(ga_number_text)
        ga_number_item.setFlags(ga_number_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        ga_number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.floor_data_table.setItem(row, self.COL_FD_GA_NUMBER, ga_number_item)

        # COL_FD_CPT_FILENAME: CPT Filename (Text, Read-only)
        filename_item = QTableWidgetItem(str(getattr(floor_data_obj, 'ram_model_name', 'N/A')))
        filename_item.setFlags(filename_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        filename_item.setData(Qt.ItemDataRole.UserRole, floor_data_obj.floor_name) 
        self.floor_data_table.setItem(row, self.COL_FD_CPT_FILENAME, filename_item)

        # COL_FD_TYPICAL: Typical Count (Editable Text)
        typical_item = QTableWidgetItem(str(getattr(floor_data_obj, 'typical_count', '1')))
        self.floor_data_table.setItem(row, self.COL_FD_TYPICAL, typical_item)

        # COL_FD_LINKED_PDF_PAGE_DISPLAY: Linked PDF Page Identifier (Text, Read-only)
        pdf_page_id_text = floor_data_obj.linked_pdf_page_identifier or "None"
        pdf_page_item = QTableWidgetItem(pdf_page_id_text)
        pdf_page_item.setFlags(pdf_page_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.floor_data_table.setItem(row, self.COL_FD_LINKED_PDF_PAGE_DISPLAY, pdf_page_item)

        # COL_FD_CPT_FILEPATH_DISPLAY: Linked .CPT File Path (Relative, Read-only)
        list_path = getattr(floor_data_obj, 'listpath', 'N/A')
        path_item = QTableWidgetItem(list_path)
        path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if not floor_data_obj.filepath or not os.path.exists(floor_data_obj.filepath):
            path_item.setBackground(QColor("pink")) # Highlight if file is missing
        else:
            path_item.setBackground(QBrush(Qt.GlobalColor.transparent))
        self.floor_data_table.setItem(row, self.COL_FD_CPT_FILEPATH_DISPLAY, path_item)

        self._table_update_in_progress = False


    def _update_floor_data_table(self):
        self._table_update_in_progress = True
        current_selection = self.floor_data_table.currentRow()
        self.floor_data_table.setRowCount(0)

        ordered_floor_data_list = self.structure_model_instance.get_ordered_floors()

        for floor_data_obj in ordered_floor_data_list:
            if not isinstance(floor_data_obj, FloorData): continue
            row_position = self.floor_data_table.rowCount()
            self.floor_data_table.insertRow(row_position)
            self._update_floor_data_table_row(row_position, floor_data_obj)

        self._table_update_in_progress = False
        if 0 <= current_selection < self.floor_data_table.rowCount():
            self.floor_data_table.selectRow(current_selection)
        else:
            self._on_floor_table_selection_changed()

    def _update_pdf_pages_table_row(self, row: int, model_page: ModelPage):
        self._pdf_table_update_in_progress = True

        # COL_PP_IS_GA: Checkbox for marking as GA
        ga_checkbox_container = QWidget()
        ga_layout = QHBoxLayout(ga_checkbox_container)
        ga_layout.setContentsMargins(0,0,0,0); ga_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ga_cb = QCheckBox()
        ga_cb.setChecked(model_page.is_selected_ga)
        ga_cb.setProperty("row", row); ga_cb.setProperty("col", self.COL_PP_IS_GA)
        ga_cb.stateChanged.connect(lambda state, r=row, mp_ident=model_page.page_name:
                                   self._on_pdf_page_checkbox_changed(state, r, mp_ident, "is_ga"))
        ga_layout.addWidget(ga_cb)
        self.pdf_pages_table.setCellWidget(row, self.COL_PP_IS_GA, ga_checkbox_container)

        # COL_PP_GA_NUMBER_DISPLAY: Display calculated GA Number (0-indexed or "-")
        ga_num_display_text = getattr(model_page, 'ga_number_display', '-')
        ga_num_item = QTableWidgetItem(str(ga_num_display_text)) # Ensure string
        ga_num_item.setFlags(ga_num_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        ga_num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_pages_table.setItem(row, self.COL_PP_GA_NUMBER_DISPLAY, ga_num_item)

        # COL_PP_INCLUDE_LINK: Checkbox for including in linking consideration
        include_checkbox_container = QWidget()
        include_layout = QHBoxLayout(include_checkbox_container)
        include_layout.setContentsMargins(0,0,0,0); include_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        include_cb = QCheckBox()
        include_cb.stateChanged.connect(lambda state, r=row, mp_ident=model_page.page_name:
                                     self._on_pdf_page_checkbox_changed(state, r, mp_ident, "is_included"))
        include_layout.addWidget(include_cb)

        # COL_PP_PDF_PAGE_REF: PDF Page Identifier (e.g., "Page_1")
        page_ref_text = model_page.page_name or f"Page {model_page.page_properties.page_index + 1 if model_page.page_properties else 'N/A'}"
        page_ref_item = QTableWidgetItem(page_ref_text)
        page_ref_item.setData(Qt.ItemDataRole.UserRole, model_page.page_name) 
        page_ref_item.setFlags(page_ref_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.pdf_pages_table.setItem(row, self.COL_PP_PDF_PAGE_REF, page_ref_item)

        self._pdf_table_update_in_progress = False


    def _update_pdf_pages_table(self):
        self._pdf_table_update_in_progress = True
        current_selection = self.pdf_pages_table.currentRow()
        self.pdf_pages_table.setRowCount(0)

        if not self.structure_model_instance.pdf_document:
            self.pdf_pages_table.setRowCount(1)
            item = QTableWidgetItem("No active PDF document loaded or PDF has no pages.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pdf_pages_table.setItem(0,0, item)
            self.pdf_pages_table.setSpan(0,0, 1, self.NUM_PP_COLUMNS) # Span across all columns
            self._pdf_table_update_in_progress = False
            self._update_ga_count_warnings() # Update warning even if no PDF
            return

        self._calculate_and_assign_pdf_ga_numbers() # Calculate GA numbers first

        for model_page in self.structure_model_instance.all_pdf_pages:
            row_position = self.pdf_pages_table.rowCount()
            self.pdf_pages_table.insertRow(row_position)
            self._update_pdf_pages_table_row(row_position, model_page)

        self._pdf_table_update_in_progress = False
        if 0 <= current_selection < self.pdf_pages_table.rowCount():
            self.pdf_pages_table.selectRow(current_selection)
        self._update_ga_count_warnings() # Update warnings after table is repopulated


    def add_cpt_files_to_active_version(self):
        active_v_path = self.structure_model_instance.gui_data.cpt_active_folder_path
        if not active_v_path or not os.path.isdir(active_v_path):
            QMessageBox.warning(self, "No Active CPT Version", "Please set an active RAM Concept (CPT) version first.")
            return
        
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Select RAM CPT Files to Add",
                                                   active_v_path, "RAM Concept Files (*.cpt)")
        if not filepaths: return
        
        added_count = 0; skipped_messages = []
        root_dir = self.structure_model_instance.gui_data.root_directory
        if not root_dir:
            QMessageBox.critical(self, "Project Error", "Project root directory not set."); return
            
        floors_dict = self.structure_model_instance.floors_data.floors
        max_current_index = 0
        if floors_dict:
            valid_indices = [int(fd.floor_index) for fd in floors_dict.values() if fd.floor_index is not None and str(fd.floor_index).isdigit()]
            if valid_indices: max_current_index = max(valid_indices)
            
        for i, fp_source_absolute in enumerate(filepaths):
            source_filename = os.path.basename(fp_source_absolute)
            fp_target_absolute = os.path.join(active_v_path, source_filename)
            
            if any(fd.ram_model_name == source_filename for fd in floors_dict.values()):
                skipped_messages.append(f"Skipped '{source_filename}': A CPT with this filename already exists in the list.")
                continue
                
            if os.path.abspath(fp_source_absolute).lower() != os.path.abspath(fp_target_absolute).lower():    
                try:
                    if not os.path.exists(os.path.dirname(fp_target_absolute)):
                        os.makedirs(os.path.dirname(fp_target_absolute))
                    shutil.copy2(fp_source_absolute, fp_target_absolute)
                except Exception as e:
                    skipped_messages.append(f"Error copying '{source_filename}' to active CPT version: {e}"); continue
            
            internal_floor_name_candidate = f"Floor_{source_filename.replace('.cpt', '')}"
            unique_internal_floor_name = internal_floor_name_candidate
            suffix_counter = 1
            while unique_internal_floor_name in floors_dict:
                unique_internal_floor_name = f"{internal_floor_name_candidate}_add_{suffix_counter}"
                suffix_counter += 1
                
            new_floor = FloorData(
                floor_name=unique_internal_floor_name,
                floor_index=max_current_index + i + 1, 
                ram_model_name=source_filename,
                is_included=True, typical_count=1,
                structure_model=self.structure_model_instance,
                floors_data_parent=self.structure_model_instance.floors_data
            )
            new_floor.update_paths(fp_target_absolute, root_dir)
            self.structure_model_instance.add_floor(new_floor)
            added_count += 1
            
        if skipped_messages:
            QMessageBox.warning(self, "Files Skipped/Errors", "\n".join(skipped_messages))
                
            
        if added_count > 0:
            self.structure_model_instance.floors_data.re_index_floors()
            self.structure_model_instance.update_gui_included_files_from_floors()
            self._save_project_data_to_pickle()
            self._update_floor_data_table()
            self._update_loaded_vars_display()
            QMessageBox.information(self, "Files Added", f"{added_count} CPT file(s) added to the project and active CPT version.")

    def _update_pdf_pages_table(self):
        self._pdf_table_update_in_progress = True
        current_selection = self.pdf_pages_table.currentRow()
        self.pdf_pages_table.setRowCount(0)

        if not self.structure_model_instance.pdf_document:
            self.pdf_pages_table.setRowCount(1)
            item = QTableWidgetItem("No active PDF document loaded or PDF has no pages.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pdf_pages_table.setItem(0,0, item)
            self.pdf_pages_table.setSpan(0,0, 1, self.NUM_PP_COLUMNS) # Span across all columns
            self._pdf_table_update_in_progress = False
            self._update_ga_count_warnings() # Update warning even if no PDF
            return

        self._calculate_and_assign_pdf_ga_numbers() # Ensure GA numbers are fresh

        for model_page in self.structure_model_instance.all_pdf_pages:
            row_position = self.pdf_pages_table.rowCount()
            self.pdf_pages_table.insertRow(row_position)
            self._update_pdf_pages_table_row(row_position, model_page)

        self._pdf_table_update_in_progress = False
        if 0 <= current_selection < self.pdf_pages_table.rowCount():
            self.pdf_pages_table.selectRow(current_selection)
        self._update_ga_count_warnings() # Update warnings after table is repopulated

        self._calculate_and_assign_pdf_ga_numbers() # Ensure GA numbers are fresh
    
    def _calculate_and_assign_pdf_ga_numbers(self): # type: ignore
        ga_counter = 0
        # Sort by original page index to ensure GA numbers are sequential
        # This assumes page_properties and page_index are correctly set when ModelPage is created/loaded
        sorted_pdf_pages = sorted(
            self.structure_model_instance.all_pdf_pages,
            key=lambda mp: mp.page_properties.page_index if mp.page_properties and mp.page_properties.page_index is not None else float('inf')
        )
        for mp in sorted_pdf_pages:
            if mp.is_selected_ga: # Only assign a GA number if it's selected as a GA
                mp.ga_number_display = str(ga_counter) # 0-indexed
                ga_counter += 1
            else:
                mp.ga_number_display = "-" # Mark as not a GA for display

    def _update_ga_count_warnings(self):
        if not hasattr(self, 'ga_count_warning_label'):
            return

        # --- Calculate Counts ---
        total_cpt_count = len(self.structure_model_instance.floors_data.floors)
        pdf_ga_selected_count = sum(1 for mp in self.structure_model_instance.all_pdf_pages if mp.is_selected_ga)

        cpts_successfully_linked_to_a_selected_ga = 0
        for fd_obj in self.structure_model_instance.floors_data.floors.values():
            if fd_obj.linked_pdf_page_identifier:
                linked_pdf_page = self.structure_model_instance.get_model_page_by_identifier(fd_obj.linked_pdf_page_identifier)
                if linked_pdf_page and linked_pdf_page.is_selected_ga:
                    cpts_successfully_linked_to_a_selected_ga += 1

        # --- Determine Warning Level ---
        # GREEN: Perfect match
        if pdf_ga_selected_count == total_cpt_count and pdf_ga_selected_count == cpts_successfully_linked_to_a_selected_ga:
            if pdf_ga_selected_count == 0:
                self.ga_count_warning_label.setText("<font color='green'>No GAs selected.</font>")
            else:
                self.ga_count_warning_label.setText(
                    f"<font color='green'>OK: {pdf_ga_selected_count} PDF GAs linked to {total_cpt_count} CPTs.</font>"
                )
            self.ga_count_warning_label.setStyleSheet("color: green; font-weight: normal;")

        # ORANGE: More CPTs than GAs (non-critical, but user should know)
        elif total_cpt_count > pdf_ga_selected_count:
            unlinked_cpts = total_cpt_count - cpts_successfully_linked_to_a_selected_ga
            self.ga_count_warning_label.setText(
                f"<font color='#E59400'>Warning: {total_cpt_count} CPTs vs {pdf_ga_selected_count} GAs. ({unlinked_cpts} CPT file(s) are unlinked).</font>"
            )
            self.ga_count_warning_label.setStyleSheet("color: #E59400; font-weight: bold;")

        # RED: Critical mismatch (e.g., more GAs than CPTs, or broken links)
        else:
            unlinked_gas = pdf_ga_selected_count - cpts_successfully_linked_to_a_selected_ga
            msg = (f"<font color='red'>Mismatch! PDF GAs: {pdf_ga_selected_count}, Linked CPTs: {cpts_successfully_linked_to_a_selected_ga}. "
                   f"({unlinked_gas} GA(s) are unlinked).</font>")
            self.ga_count_warning_label.setText(msg)
            self.ga_count_warning_label.setStyleSheet("color: red; font-weight: bold;")


    def _perform_automatic_ga_sync(self):
        if not self.structure_model_instance or \
           not self.structure_model_instance.all_pdf_pages or \
           not self.structure_model_instance.floors_data:
            return False

        print("Performing automatic GA sync...")
        model_changed_by_sync = False
        
        self._calculate_and_assign_pdf_ga_numbers()

        pdf_ga_map_by_number: dict[int, ModelPage] = {}
        for mp in self.structure_model_instance.all_pdf_pages:
            if mp.is_selected_ga and hasattr(mp, 'ga_number_display') and mp.ga_number_display != "-":
                try:
                    ga_num = int(mp.ga_number_display)
                    pdf_ga_map_by_number[ga_num] = mp
                except (ValueError, TypeError):
                    continue

        # Clear all existing links first
        for fd_clear in self.structure_model_instance.floors_data.floors.values():
            if fd_clear.linked_pdf_page_identifier is not None:
                fd_clear.linked_pdf_page_identifier = None
                model_changed_by_sync = True
        for mp_clear in self.structure_model_instance.all_pdf_pages:
            if mp_clear.linked_cpt_floor_name is not None:
                mp_clear.linked_cpt_floor_name = None
                model_changed_by_sync = True
        
        # Establish new links based on matching GA numbers
        for fd in self.structure_model_instance.floors_data.floors.values():
            cpt_ga_number_candidate = fd.floor_index
            if cpt_ga_number_candidate is not None and cpt_ga_number_candidate >= 0:
                matching_pdf_ga_page = pdf_ga_map_by_number.get(cpt_ga_number_candidate)
                if matching_pdf_ga_page:
                    fd.linked_pdf_page_identifier = matching_pdf_ga_page.page_name
                    matching_pdf_ga_page.linked_cpt_floor_name = fd.floor_name
                    model_changed_by_sync = True
        
        if model_changed_by_sync:
            print("Automatic GA sync: Model links updated.")
        return model_changed_by_sync
    
    def _update_story_data_table(self):
        self._table_update_in_progress = True
        self.story_data_table.setRowCount(0)
        ordered_floor_data_list = self.structure_model_instance.get_ordered_floors()

        for floor_data_obj in ordered_floor_data_list:
            if not isinstance(floor_data_obj, FloorData): continue
            row_position = self.story_data_table.rowCount()
            self.story_data_table.insertRow(row_position)
            self._update_story_data_table_row(row_position, floor_data_obj)

        self._table_update_in_progress = False


    def _update_story_data_table_row(self, row: int, floor_data_obj: FloorData):
        # COL_STORY_UPDATE: "To Be Updated" Checkbox
        # ... (This part of the method remains the same)
        checkbox_widget_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget_container)
        checkbox_layout.setContentsMargins(5, 0, 5, 0)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        update_cb = QCheckBox()
        update_cb.setChecked(getattr(floor_data_obj, 'to_be_updated', True))
        update_cb.stateChanged.connect(lambda state, fd_key=floor_data_obj.floor_name:
                                        self._on_story_update_checkbox_changed(state, fd_key))
        checkbox_layout.addWidget(update_cb)
        self.story_data_table.setCellWidget(row, self.COL_STORY_UPDATE, checkbox_widget_container)


        # COL_STORY_NAME: Floor Name
        display_name = (floor_data_obj.ram_model_name or floor_data_obj.floor_name).replace('.cpt', '')
        name_item = QTableWidgetItem(display_name)

        if floor_data_obj.is_placeholder:
            # Make placeholder names italic and not editable
            font = name_item.font()
            font.setItalic(True)
            name_item.setFont(font)
            name_item.setForeground(QColor('gray'))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        name_item.setData(Qt.ItemDataRole.UserRole, floor_data_obj.floor_name)
        self.story_data_table.setItem(row, self.COL_STORY_NAME, name_item)

        # COL_STORY_ELEV: Elevation (TOC)
        toc_val = getattr(floor_data_obj, 'toc', "")
        elev_item = QTableWidgetItem(str(toc_val) if toc_val is not None else "")
        self.story_data_table.setItem(row, self.COL_STORY_ELEV, elev_item)

        # COL_STORY_TYPICAL: Typical Count
        typical_item = QTableWidgetItem(str(getattr(floor_data_obj, 'typical_count', '1')))
        self.story_data_table.setItem(row, self.COL_STORY_TYPICAL, typical_item)



    def _on_story_update_checkbox_changed(self, state, floor_name_key: str):
        if self._programmatic_checkbox_update or self._table_update_in_progress:
            return
        floor_data_obj = self.structure_model_instance.get_floor_by_name(floor_name_key)
        if floor_data_obj:
            floor_data_obj.to_be_updated = bool(state)
            self._save_project_data_to_pickle()

    def _on_story_table_item_changed(self, item: QTableWidgetItem):
        if self._table_update_in_progress or self._programmatic_ui_update: return

        row, col = item.row(), item.column()
        name_item = self.story_data_table.item(row, self.COL_STORY_NAME)
        if not name_item: return

        floor_name_key = name_item.data(Qt.ItemDataRole.UserRole)
        floor_data_obj = self.structure_model_instance.get_floor_by_name(floor_name_key)
        if not floor_data_obj: return

        changed = False
        if col == self.COL_STORY_ELEV:
            try:
                new_val = float(item.text())
                if floor_data_obj.toc != new_val:
                    floor_data_obj.toc = new_val
                    changed = True
            except (ValueError, TypeError):
                item.setText(str(floor_data_obj.toc or ""))
        elif col == self.COL_STORY_TYPICAL:
            try:
                new_val = int(item.text())
                if new_val < 1: new_val = 1
                if floor_data_obj.typical_count != new_val:
                    floor_data_obj.typical_count = new_val
                    changed = True
            except (ValueError, TypeError):
                item.setText(str(floor_data_obj.typical_count))
        
        if changed:
            self._save_project_data_to_pickle()
            # Refresh the right-hand table to show updated values
            self._update_floor_data_table()


    def _update_all_explorers_and_tables(self):
        print("Updating all explorers and tables...")
        self._programmatic_ui_update = True
        
        self._update_cpt_version_explorer_listbox()
        self._update_pdf_version_explorer_listbox()
        
        if self.structure_model_instance.pdf_document:
            self._calculate_and_assign_pdf_ga_numbers()
            self._perform_automatic_ga_sync()

        self._update_floor_data_table()
        self._update_pdf_pages_table()
        self._update_story_data_table() # <-- ADD THIS LINE

        self._update_loaded_vars_display()
        self._update_ga_count_warnings()
        
        self._programmatic_ui_update = False

    def _update_story_data_table(self):
        self._table_update_in_progress = True
        self.story_data_table.setRowCount(0)
        ordered_floor_data_list = self.structure_model_instance.get_ordered_floors()

        for floor_data_obj in ordered_floor_data_list:
            if not isinstance(floor_data_obj, FloorData): continue
            row_position = self.story_data_table.rowCount()
            self.story_data_table.insertRow(row_position)
            self._update_story_data_table_row(row_position, floor_data_obj)

        self._table_update_in_progress = False

    def _update_story_data_table_row(self, row: int, floor_data_obj: FloorData):
        # COL_STORY_UPDATE: "To Be Updated" Checkbox
        checkbox_widget_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget_container)
        checkbox_layout.setContentsMargins(5, 0, 5, 0)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        update_cb = QCheckBox()
        update_cb.setChecked(getattr(floor_data_obj, 'to_be_updated', True))
        update_cb.stateChanged.connect(lambda state, fd_key=floor_data_obj.floor_name:
                                        self._on_story_update_checkbox_changed(state, fd_key))
        checkbox_layout.addWidget(update_cb)
        self.story_data_table.setCellWidget(row, self.COL_STORY_UPDATE, checkbox_widget_container)

        # COL_STORY_NAME: Floor Name (Read-only)
        name_item = QTableWidgetItem(floor_data_obj.ram_model_name or floor_data_obj.floor_name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        name_item.setData(Qt.ItemDataRole.UserRole, floor_data_obj.floor_name) # Store internal key
        self.story_data_table.setItem(row, self.COL_STORY_NAME, name_item)

        # COL_STORY_ELEV: Elevation (TOC)
        toc_val = getattr(floor_data_obj, 'toc', "")
        elev_item = QTableWidgetItem(str(toc_val) if toc_val is not None else "")
        self.story_data_table.setItem(row, self.COL_STORY_ELEV, elev_item)

        # COL_STORY_TYPICAL: Typical Count
        typical_item = QTableWidgetItem(str(getattr(floor_data_obj, 'typical_count', '1')))
        self.story_data_table.setItem(row, self.COL_STORY_TYPICAL, typical_item)

    def _on_story_update_checkbox_changed(self, state, floor_name_key: str):
        if self._programmatic_checkbox_update or self._table_update_in_progress:
            return
        floor_data_obj = self.structure_model_instance.get_floor_by_name(floor_name_key)
        if floor_data_obj:
            floor_data_obj.to_be_updated = bool(state)
            self._save_project_data_to_pickle()

    def _on_story_table_item_changed(self, item: QTableWidgetItem):
        if self._table_update_in_progress or self._programmatic_ui_update: return

        row, col = item.row(), item.column()
        name_item = self.story_data_table.item(row, self.COL_STORY_NAME)
        if not name_item: return

        floor_name_key = name_item.data(Qt.ItemDataRole.UserRole)
        floor_data_obj = self.structure_model_instance.get_floor_by_name(floor_name_key)
        if not floor_data_obj: return

        changed = False
        if col == self.COL_STORY_ELEV:
            try:
                new_val = float(item.text())
                if floor_data_obj.toc != new_val:
                    floor_data_obj.toc = new_val
                    changed = True
            except (ValueError, TypeError):
                item.setText(str(floor_data_obj.toc or ""))
        elif col == self.COL_STORY_TYPICAL:
            try:
                new_val = int(item.text())
                if new_val < 1: new_val = 1
                if floor_data_obj.typical_count != new_val:
                    floor_data_obj.typical_count = new_val
                    changed = True
            except (ValueError, TypeError):
                item.setText(str(floor_data_obj.typical_count))

        if changed:
            self._save_project_data_to_pickle()
            # Refresh the right-hand table to show updated values
            self._update_floor_data_table()

    def _update_all_explorers_and_tables(self):
        print("Updating all explorers and tables...")
        self._programmatic_ui_update = True

        self._update_cpt_version_explorer_listbox()
        self._update_pdf_version_explorer_listbox()

        if self.structure_model_instance.pdf_document:
            self._calculate_and_assign_pdf_ga_numbers()
            self._perform_automatic_ga_sync()

        self._update_floor_data_table()
        self._update_pdf_pages_table()
        self._update_story_data_table() # <-- Ensures left table is updated

        self._update_loaded_vars_display()
        self._update_ga_count_warnings()

        self._programmatic_ui_update = False

    def _refresh_pdf_table_display(self):
        """
        Updates the content of the PDF pages table without clearing it to preserve scroll position.
        """
        self._pdf_table_update_in_progress = True
        sorted_pdf_pages = sorted(
            self.structure_model_instance.all_pdf_pages,
            key=lambda mp: mp.page_properties.page_index if mp.page_properties and mp.page_properties.page_index is not None else float('inf')
        )

        for row, model_page in enumerate(sorted_pdf_pages):
            # We assume the number of rows hasn't changed, only the data within them.
            if row < self.pdf_pages_table.rowCount():
                # Update GA Number display
                ga_num_display_text = getattr(model_page, 'ga_number_display', '-')
                ga_num_item = QTableWidgetItem(str(ga_num_display_text))
                ga_num_item.setFlags(ga_num_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                ga_num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.pdf_pages_table.setItem(row, self.COL_PP_GA_NUMBER_DISPLAY, ga_num_item)

        self._pdf_table_update_in_progress = False


    def _sync_floor_data_with_ga_selections(self):
        """
        The new core logic that synchronizes the FloorData model with the selected GAs.
        It creates placeholder FloorData objects for selected GAs that have no CPT yet,
        and removes them if the GA is deselected. It then attempts to link any real CPTs.
        """
        if not self.structure_model_instance: return
        model_changed = False

        # --- 1. Identify all selected GAs and existing placeholders ---
        selected_ga_pages = {
            mp.page_name: mp for mp in self.structure_model_instance.all_pdf_pages if mp.is_selected_ga
        }
        
        current_floor_data = list(self.structure_model_instance.floors_data.floors.values())
        placeholders_to_remove = []
        
        # --- 2. Remove placeholders whose GAs are no longer selected ---
        for fd in current_floor_data:
            if fd.is_placeholder:
                # If a placeholder's linked PDF page is no longer in the selected GA list...
                if fd.linked_pdf_page_identifier not in selected_ga_pages:
                    placeholders_to_remove.append(fd.floor_name)
                    model_changed = True
        
        for key in placeholders_to_remove:
            self.structure_model_instance.floors_data.remove_floor(key)
            print(f"Removed placeholder: {key}")

        # --- 3. Create new placeholders for newly selected GAs ---
        # Get a set of PDF pages that are already linked to a FloorData object
        linked_pdf_ids = {fd.linked_pdf_page_identifier for fd in self.structure_model_instance.floors_data.floors.values()}

        for page_name, model_page in selected_ga_pages.items():
            if page_name not in linked_pdf_ids:
                # This GA is selected but nothing is linked to it yet. Create a placeholder.
                ga_num = int(model_page.ga_number_display)
                placeholder_name = f"<Placeholder for GA {ga_num}>"
                internal_key = f"placeholder_{page_name}"

                new_fd = FloorData(
                    floor_name=internal_key,
                    floor_index=ga_num,
                    ram_model_name=placeholder_name,
                    is_placeholder=True,
                    is_included=True,
                    to_be_updated=True,
                    linked_pdf_page_identifier=page_name,
                    structure_model=self.structure_model_instance,
                )
                self.structure_model_instance.add_floor(new_fd)
                model_page.linked_cpt_floor_name = internal_key
                model_changed = True
                print(f"Created placeholder: {internal_key}")
        
        # --- 4. Run the automatic CPT-to-GA linking logic ---
        # This will link any actual CPT files based on their floor_index matching a GA number.
        if self._perform_automatic_ga_sync():
            model_changed = True

        return model_changed
    
    