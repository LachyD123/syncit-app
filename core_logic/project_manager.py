import os
import pickle
import shutil
from datetime import datetime
from typing import TYPE_CHECKING, Tuple, Optional, List
import re

from data_model.structure_model import StructureModel # StructureModel imports GUIData
from data_model.floor_data import FloorsData # Import FloorsData
from gui.gui_data import GUIData, SETTINGS_DEFAULT, PDF_BINDERS_DIR_NAME

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QMessageBox # For type hinting parent

# --- Constants for directory names ---
RAM_CONCEPT_DIR_NAME = "RAM_CONCEPT"
PICKLED_DATA_DIR_NAME = "pickled_project_data"
PICKLED_DATA_FILENAME = "project_session.pkl"
FILE_TEMPLATES_DIR_NAME = "file_templates"
# PDF_BINDERS_DIR_NAME is imported from gui_data

class ProjectManager:
    def __init__(self, structure_model_instance: StructureModel, gui_parent=None):
        self.model = structure_model_instance # This is StructureModel instance
        self.gui_parent = gui_parent # For showing messages

    def _show_message(self, level: str, title: str, message: str):
        """Helper to show messages, ideally via GUI if parent is set."""
        print(f"[{level.upper()}] {title}: {message}")
        if self.gui_parent:
            try:
                from PyQt6.QtWidgets import QMessageBox
                if level == "info": QMessageBox.information(self.gui_parent, title, message)
                elif level == "warning": QMessageBox.warning(self.gui_parent, title, message)
                elif level == "critical": QMessageBox.critical(self.gui_parent, title, message)
                elif level == "error": QMessageBox.critical(self.gui_parent, title, message) # Added error level
            except ImportError:
                print("PyQt6 not available for showing GUI message in ProjectManager.")
            except Exception as e:
                print(f"Error showing GUI message: {e}")

    def _check_or_create_subfolders(self, base_path: str) -> None:
        """
        Checks for essential subfolders in the base_path and creates them if they don't exist.
        """
        if not base_path or not os.path.isdir(base_path):
            self._show_message("warning", "Folder Setup Error",
                               f"Base path '{base_path}' is invalid. Cannot create subfolders.")
            return

        required_folders: List[str] = [
            'excel', 'logs', 'backups',
            RAM_CONCEPT_DIR_NAME,
            PICKLED_DATA_DIR_NAME,
            FILE_TEMPLATES_DIR_NAME,
            PDF_BINDERS_DIR_NAME
        ]

        for folder_name in required_folders:
            folder_path = os.path.join(base_path, folder_name)
            if not os.path.isdir(folder_path):
                try:
                    os.makedirs(folder_path)
                    print(f"ProjectManager: Created subfolder: {folder_path}")
                except Exception as e:
                    self._show_message("warning", "Folder Creation Error",
                                       f"Could not create required subfolder '{folder_path}':\n{e}")

    def get_pickle_data_path(self) -> Optional[str]:
        if not self.model.gui_data.root_directory: # gui_data is directly on StructureModel
            return None
        return os.path.join(self.model.gui_data.root_directory, PICKLED_DATA_DIR_NAME, PICKLED_DATA_FILENAME)    

    def save_project_data(self) -> bool:
        pickle_path = self.get_pickle_data_path()
        if not pickle_path:
            self._show_message("warning", "Save Error", "Project root directory not set. Cannot save.")
            return False

        pickle_dir = os.path.dirname(pickle_path)
        if not os.path.exists(pickle_dir):
            try:
                os.makedirs(pickle_dir)
            except Exception as e:
                self._show_message("critical", "Save Error", f"Could not create directory for project data:\n{pickle_dir}\nError: {e}")
                return False

        if os.path.exists(pickle_path):
            self.backup_project_file(self.model.gui_data.root_directory, pickle_path, "project_session_autosave")

        try:
            # Ensure included_files in gui_data is up-to-date before saving
            self.model.update_gui_included_files_from_floors()
            
            with open(pickle_path, 'wb') as f:
                pickle.dump(self.model, f) # self.model is StructureModel, which contains GUIData
            print(f"Project data saved to '{pickle_path}'.")
            return True
        except Exception as e:
            self._show_message("critical", "Pickle Save Error", f"Could not save project data to:\n{pickle_path}\nError: {e}")
            return False

    def load_project_data(self) -> Tuple[bool, Optional[StructureModel]]:
        pickle_path = self.get_pickle_data_path()
        
        current_root_dir_from_gui = None
        if self.model and self.model.gui_data and self.model.gui_data.root_directory:
            current_root_dir_from_gui = self.model.gui_data.root_directory

        if not pickle_path or not os.path.exists(pickle_path):
            print(f"No project data file found at '{pickle_path}'. Starting with defaults for current root.")    
            # Create a new StructureModel with default GUIData, preserving current root if available
            default_gui_data = GUIData.from_dict(SETTINGS_DEFAULT)
            if current_root_dir_from_gui: # If GUI had a root_directory (e.g. user just set it)
                default_gui_data.root_directory = current_root_dir_from_gui
            
            new_model = StructureModel(gui_data=default_gui_data)
            new_model.floors_data = FloorsData(model=new_model) # Ensure floors_data is initialized
            return False, new_model

        try:
            with open(pickle_path, 'rb') as f:
                loaded_model: StructureModel = pickle.load(f)

            if not isinstance(loaded_model, StructureModel):
                raise TypeError("Loaded data is not a compatible StructureModel instance.")

            # Ensure gui_data exists and is an instance of GUIData.
            # Merge with defaults to handle fields added since the pickle was saved.
            if loaded_model.gui_data is None:
                # If gui_data is None in the pickle, create from defaults
                loaded_gui_data_dict = SETTINGS_DEFAULT.copy()
                print("Warning: Loaded model had no gui_data. Initializing from defaults.")
            elif isinstance(loaded_model.gui_data, dict):
                # If gui_data was pickled as a dict (older format), convert and merge
                print("Warning: Loaded gui_data was a dict. Converting to GUIData object.")
                loaded_gui_data_dict = SETTINGS_DEFAULT.copy()
                loaded_gui_data_dict.update(loaded_model.gui_data) # loaded_model.gui_data is the dict
            elif isinstance(loaded_model.gui_data, GUIData):
                # If it's already a GUIData object, convert to dict to merge with defaults
                # This ensures new fields in SETTINGS_DEFAULT are added if missing from pickled GUIData
                temp_dict = loaded_model.gui_data.to_variable_dict()
                loaded_gui_data_dict = SETTINGS_DEFAULT.copy()
                loaded_gui_data_dict.update(temp_dict)
            else:
                # Should not happen if types are consistent
                raise TypeError(f"Unexpected type for loaded_model.gui_data: {type(loaded_model.gui_data)}")

            # Preserve the root_directory from the loaded pickle if it was valid,
            # otherwise, if the current GUI context has a root_directory (e.g. user just set it), use that.
            # The pickle_path implies a root directory, so loaded_gui_data_dict['ROOT_DIRECTORY'] should be correct if pickle_path was derived from it.
            if pickle_path: # pickle_path is based on a root_directory
                 expected_root = os.path.dirname(os.path.dirname(pickle_path))
                 loaded_gui_data_dict['ROOT_DIRECTORY'] = expected_root
            elif current_root_dir_from_gui : # Fallback if somehow pickle_path was None but file existed
                 loaded_gui_data_dict['ROOT_DIRECTORY'] = current_root_dir_from_gui


            # Re-initialize gui_data from the potentially merged dictionary
            loaded_model.gui_data = GUIData.from_dict(loaded_gui_data_dict)
            
            # Ensure floors_data and its parent links are correctly set up
            if loaded_model.floors_data is None:
                loaded_model.floors_data = FloorsData(model=loaded_model)
            else:
                loaded_model.floors_data.model = loaded_model # Relink parent
                for fd_key in list(loaded_model.floors_data.floors.keys()):
                    fd = loaded_model.floors_data.floors[fd_key]
                    fd.structure_model = loaded_model
                    fd.floors_data_parent = loaded_model.floors_data
                    # Ensure legacy fields exist
                    if not hasattr(fd, 'pdf_page_ref_text'): setattr(fd, 'pdf_page_ref_text', "")
                    if not hasattr(fd, 'ga_page_fitz'): setattr(fd, 'ga_page_fitz', None) # Fitz page restored later
                    if not hasattr(fd, '_ga_page_index'): setattr(fd, '_ga_page_index', None)
                    if not hasattr(fd, 'linked_pdf_page_identifier'): setattr(fd, 'linked_pdf_page_identifier', None)


            # Synchronize FloorData.is_included with gui_data.included_files (gui_data is source of truth after load)
            model_included_ram_names = set(loaded_model.gui_data.included_files or [])
            for fd_obj in loaded_model.floors_data.floors.values():
                setattr(fd_obj, 'is_included', fd_obj.ram_model_name in model_included_ram_names)

            # The StructureModel.__setstate__ will handle reloading the PDF document
            # based on paths in the now-populated loaded_model.gui_data.
            # Call __post_init__ or equivalent logic if __setstate__ doesn't cover everything.
            # For StructureModel, __setstate__ reloads PDF, which is what we want.
            # No, __setstate__ should have been called by pickle.load().
            # We might need to explicitly trigger parts of its logic if paths changed during GUIData merge.
            # Let's assume StructureModel's __setstate__ correctly uses its now-updated gui_data.
            # Explicitly call load_pdf_document if it wasn't loaded or path changed.
            pdf_to_load_after_merge = loaded_model.gui_data.current_pdf_binder_full_path
            if pdf_to_load_after_merge and os.path.exists(pdf_to_load_after_merge):
                if not loaded_model.pdf_document or \
                   (hasattr(loaded_model.pdf_document, "name") and loaded_model.pdf_document.name != os.path.abspath(pdf_to_load_after_merge)):
                    loaded_model.load_pdf_document(pdf_to_load_after_merge)
            elif loaded_model.pdf_document: # If no valid path but doc exists, clear it
                loaded_model.pdf_document = None
                loaded_model.all_pdf_pages.clear()


            print(f"Project data loaded from '{pickle_path}'.")
            return True, loaded_model
            
        except Exception as e:
            self._show_message("critical", "Pickle Load Error", f"Error loading project data from '{pickle_path}': {e}")
            # Fallback to a new model if loading fails critically
            default_gui_data = GUIData.from_dict(SETTINGS_DEFAULT)
            if current_root_dir_from_gui: # Preserve root if available from GUI context
                default_gui_data.root_directory = current_root_dir_from_gui
            
            new_model_on_error = StructureModel(gui_data=default_gui_data)
            new_model_on_error.floors_data = FloorsData(model=new_model_on_error)
            return False, new_model_on_error

    def backup_project_file(self, root_path_for_backup_folder: str, file_to_backup_absolute_path: str, backup_reason: str = "backup"):
        # This method seems fine as is.
        backup_dir = os.path.join(root_path_for_backup_folder, 'backups')
        if not os.path.isdir(backup_dir):
            try:
                os.makedirs(backup_dir)
            except Exception as e:
                print(f"Warning: Could not create backup directory '{backup_dir}': {e}")
                return

        if os.path.exists(file_to_backup_absolute_path):
            base_filename = os.path.basename(file_to_backup_absolute_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{os.path.splitext(base_filename)[0]}_{backup_reason}_{timestamp}{os.path.splitext(base_filename)[1]}.bak"
            backup_dest = os.path.join(backup_dir, backup_filename)
            try:
                shutil.copy2(file_to_backup_absolute_path, backup_dest)
                print(f"Backed up '{base_filename}' to '{backup_dest}'")
            except Exception as e:
                print(f"Warning: Could not back up '{base_filename}': {e}")

    def get_ram_concept_base_path(self) -> Optional[str]:
        if not self.model.gui_data.root_directory or not os.path.isdir(self.model.gui_data.root_directory):    
            return None
        return os.path.join(self.model.gui_data.root_directory, RAM_CONCEPT_DIR_NAME)

    def get_pdf_binders_base_path(self) -> Optional[str]:
        if not self.model.gui_data.root_directory or not os.path.isdir(self.model.gui_data.root_directory):    
            self._show_message("warning", "PDF Path Error", "Project root directory not set for PDF binders.") # Message change
            return None
        return os.path.join(self.model.gui_data.root_directory, PDF_BINDERS_DIR_NAME)

    def _parse_version_string_semantic(self, version_str_part: str) -> Optional[Tuple[int, int, int]]:
        # This method seems fine as is.
        if not version_str_part: return None
        match = re.match(r"V(\d+)\.(\d+)\.(\d+)", version_str_part, re.IGNORECASE)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
        return None

    def _generate_next_version_semantic(self, current_version_tuple: Tuple[int, int, int], change_type: str) -> str:
        # This method seems fine as is.
        major, minor, patch = current_version_tuple
        if change_type == "Breaking": major += 1; minor = 0; patch = 0
        elif change_type == "Moderate": minor += 1; patch = 0
        elif change_type == "Minor": patch += 1
        else: patch +=1 # Default to patch
        return f"V{major}.{minor}.{patch}"

    def create_new_ram_version(self, change_type: str = "Minor", description_suffix: str = "New Version", copy_from_active: bool = True) -> Optional[str]:
        # This method correctly uses self.model.gui_data for active CPT version info.
        # It should remain largely the same.
        ram_versions_base_path = self.get_ram_concept_base_path()
        if not ram_versions_base_path:
            self._show_message("warning", "Version Error", f"'{RAM_CONCEPT_DIR_NAME}' subfolder path is invalid. Cannot create CPT version.")
            return None

        if not os.path.isdir(ram_versions_base_path):
            try:
                os.makedirs(ram_versions_base_path)
            except Exception as e:
                self._show_message("critical", "Version Error", f"Could not create '{RAM_CONCEPT_DIR_NAME}' folder: {e}")
                return None

        current_version_tuple_for_increment = (0, 0, 0) 
        source_for_copy_path: Optional[str] = None
        active_version_semantic_tag = "N/A"

        if self.model.gui_data.cpt_active_folder_name and self.model.gui_data.cpt_active_folder_path:
            potential_version_part = self.model.gui_data.cpt_active_folder_name.split(' ')[0]
            parsed_tuple = self._parse_version_string_semantic(potential_version_part)
            if parsed_tuple:
                current_version_tuple_for_increment = parsed_tuple
                active_version_semantic_tag = f"V{parsed_tuple[0]}.{parsed_tuple[1]}.{parsed_tuple[2]}"
            else: # Fallback if parsing fails
                active_version_semantic_tag = potential_version_part 
                existing_folders = [d for d in os.listdir(ram_versions_base_path) if os.path.isdir(os.path.join(ram_versions_base_path, d))]
                if existing_folders: # Try to find max existing version if current active name is not semantic
                    max_existing_sem_ver = (0,0,-1) # Start before V0.0.0
                    for folder_name_existing in existing_folders:
                        parsed_existing = self._parse_version_string_semantic(folder_name_existing.split(' ')[0])
                        if parsed_existing and parsed_existing > max_existing_sem_ver:
                            max_existing_sem_ver = parsed_existing
                    if max_existing_sem_ver[2] != -1: # if we found any semantic version
                         current_version_tuple_for_increment = max_existing_sem_ver


            if copy_from_active and os.path.isdir(self.model.gui_data.cpt_active_folder_path):
                source_for_copy_path = self.model.gui_data.cpt_active_folder_path
        else: # No active version, check existing folders to determine next version
            existing_folders = [d for d in os.listdir(ram_versions_base_path) if os.path.isdir(os.path.join(ram_versions_base_path, d))]
            if existing_folders:
                max_existing_sem_ver = (0,0,-1)
                for folder_name_existing in existing_folders:
                    parsed_existing = self._parse_version_string_semantic(folder_name_existing.split(' ')[0])
                    if parsed_existing and parsed_existing > max_existing_sem_ver:
                        max_existing_sem_ver = parsed_existing
                if max_existing_sem_ver[2] != -1:
                     current_version_tuple_for_increment = max_existing_sem_ver


        new_version_vxvyvz = self._generate_next_version_semantic(current_version_tuple_for_increment, change_type)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

        final_description = description_suffix
        if copy_from_active and source_for_copy_path:
            final_description = f"{description_suffix} (copied from {active_version_semantic_tag})"
        
        safe_description = re.sub(r'[\\/*?:"<>|]', '_', final_description)
        new_version_folder_name = f"{new_version_vxvyvz} - {timestamp} - {safe_description}"
        new_version_full_path = os.path.join(ram_versions_base_path, new_version_folder_name)

        if os.path.exists(new_version_full_path):
            self._show_message("warning", "Version Exists", f"CPT Version folder '{new_version_folder_name}' already exists.")
            return None # Or generate with a slightly different timestamp/suffix
        try:
            if copy_from_active and source_for_copy_path:
                shutil.copytree(source_for_copy_path, new_version_full_path)
            else:
                os.makedirs(new_version_full_path)
            
            self._show_message("info", "CPT Version Created", f"CPT Version '{new_version_folder_name}' created at {new_version_full_path}.")
            return new_version_full_path
        except Exception as e:
            self._show_message("critical", "CPT Version Creation Error", f"Failed to create CPT version '{new_version_folder_name}': {e}")
            return None

    def create_new_pdf_binder_version(self, source_pdf_abs_path: str, change_type: str = "Minor", description_suffix: str = "New PDF Version") -> Tuple[Optional[str], Optional[str]]:
        # This method correctly uses self.model.gui_data for active PDF version info.
        # It should remain largely the same.
        pdf_versions_base_path = self.get_pdf_binders_base_path()
        if not pdf_versions_base_path:
            # Message already shown by get_pdf_binders_base_path
            return None, None

        if not os.path.isdir(pdf_versions_base_path):
            try:
                os.makedirs(pdf_versions_base_path)
            except Exception as e:
                self._show_message("critical", "PDF Version Error", f"Could not create '{PDF_BINDERS_DIR_NAME}' folder: {e}")
                return None, None

        if not os.path.exists(source_pdf_abs_path):
            self._show_message("error", "PDF Not Found", f"Source PDF for versioning not found at: {source_pdf_abs_path}")
            return None, None

        current_version_tuple_for_increment = (0, 0, 0)
        if self.model.gui_data.active_pdf_binder_version_name:
            potential_version_part = self.model.gui_data.active_pdf_binder_version_name.split(' ')[0]
            parsed_tuple = self._parse_version_string_semantic(potential_version_part)
            if parsed_tuple:
                current_version_tuple_for_increment = parsed_tuple
            else: # Fallback if parsing fails
                existing_folders = [d for d in os.listdir(pdf_versions_base_path) if os.path.isdir(os.path.join(pdf_versions_base_path, d))]
                if existing_folders:
                    max_existing_sem_ver = (0,0,-1)
                    for folder_name_existing in existing_folders:
                        parsed_existing = self._parse_version_string_semantic(folder_name_existing.split(' ')[0])
                        if parsed_existing and parsed_existing > max_existing_sem_ver:
                             max_existing_sem_ver = parsed_existing
                    if max_existing_sem_ver[2] != -1:
                         current_version_tuple_for_increment = max_existing_sem_ver
        else: # No active version, check existing folders
            existing_folders = [d for d in os.listdir(pdf_versions_base_path) if os.path.isdir(os.path.join(pdf_versions_base_path, d))]
            if existing_folders:
                max_existing_sem_ver = (0,0,-1)
                for folder_name_existing in existing_folders:
                    parsed_existing = self._parse_version_string_semantic(folder_name_existing.split(' ')[0])
                    if parsed_existing and parsed_existing > max_existing_sem_ver:
                         max_existing_sem_ver = parsed_existing
                if max_existing_sem_ver[2] != -1:
                     current_version_tuple_for_increment = max_existing_sem_ver


        new_version_vxvyvz = self._generate_next_version_semantic(current_version_tuple_for_increment, change_type)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        original_pdf_filename = os.path.basename(source_pdf_abs_path)
        
        safe_description = re.sub(r'[\\/*?:"<>|]', '_', description_suffix if description_suffix else "PDF Update")
        new_pdf_version_folder_name = f"{new_version_vxvyvz} - {timestamp} - {safe_description}"
        new_pdf_version_full_path = os.path.join(pdf_versions_base_path, new_pdf_version_folder_name)

        if os.path.exists(new_pdf_version_full_path):
            self._show_message("warning", "PDF Version Exists", f"PDF Version folder '{new_pdf_version_folder_name}' already exists.")
            return None, None # Or generate with a slightly different timestamp/suffix
        try:
            os.makedirs(new_pdf_version_full_path)
            target_pdf_path_in_version = os.path.join(new_pdf_version_full_path, original_pdf_filename)
            shutil.copy2(source_pdf_abs_path, target_pdf_path_in_version)

            self._show_message("info", "PDF Version Created", f"PDF Version '{new_pdf_version_folder_name}' created with '{original_pdf_filename}'.")
            return new_pdf_version_full_path, original_pdf_filename
        except Exception as e:
            self._show_message("critical", "PDF Version Creation Error", f"Failed to create PDF version '{new_pdf_version_folder_name}': {e}")
            if os.path.exists(new_pdf_version_full_path): 
                try: shutil.rmtree(new_pdf_version_full_path)
                except Exception as e_clean: print(f"Error cleaning up version folder: {e_clean}")
            return None, None

    def set_active_version(self, version_name: Optional[str], version_path: Optional[str]):
        """Sets the active CPT version in GUIData."""
        self.model.gui_data.cpt_active_folder_name = version_name
        self.model.gui_data.cpt_active_folder_path = version_path
        print(f"ProjectManager: Active CPT version set to Name: {version_name}, Path: {version_path}")

    def set_active_pdf_binder_version(self, version_folder_name: Optional[str], version_folder_path: Optional[str], pdf_filename_in_folder: Optional[str]):
        """Sets the active PDF binder version details in GUIData and triggers PDF load in StructureModel."""
        self.model.gui_data.active_pdf_binder_version_name = version_folder_name
        self.model.gui_data.active_pdf_binder_version_path = version_folder_path
        self.model.gui_data.pdf_binder_filename_in_version = pdf_filename_in_folder

        # Update the general pdf_binder_path for legacy/fallback if needed.
        # current_pdf_binder_full_path property is now the primary way to get the active PDF.
        if version_folder_path and pdf_filename_in_folder:
            self.model.gui_data.pdf_binder_path = os.path.join(version_folder_path, pdf_filename_in_folder)
        elif not version_folder_name: # Clearing active PDF version
             self.model.gui_data.pdf_binder_path = None # Set to None or empty string


        print(f"ProjectManager: Active PDF Binder version set to Name: {version_folder_name}, Folder: {version_folder_path}, File: {pdf_filename_in_folder}")

        # Trigger PDF load in structure_model
        active_pdf_full_path = self.model.gui_data.current_pdf_binder_full_path
        if active_pdf_full_path and os.path.exists(active_pdf_full_path):
            self.model.load_pdf_document(active_pdf_full_path)
        else:
            if self.model.pdf_document: self.model.pdf_document.close()
            self.model.pdf_document = None 
            self.model.all_pdf_pages.clear()
            print("ProjectManager: Cleared PDF document in model as no active/valid PDF path.")
