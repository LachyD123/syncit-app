# core_logic/cpt_manager.py
import os
import shutil
from datetime import datetime
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ram_concept.concept import Concept # type: ignore
    from ram_concept.model import Model as RAMModel # type: ignore
    from data_model.floor_data import FloorData
    from data_model.structure_model import StructureModel
else:
    # Minimal placeholders
    class Concept: 
        @staticmethod
        def start_concept(headless=True, log_file_path=None): pass
        def open_file(self, path): pass
        def create_new_file(self): pass # Hypothetical
    class RAMModel:
        def save_file(self, path): pass
        def close_model(self): pass


class CPTManager:
    def __init__(self, structure_model: "StructureModel"):
        self.structure_model = structure_model

    def create_cpt_from_template_for_floor(
        self,
        floor_data: "FloorData",
        target_version_path: str, # Absolute path to the version folder
        base_cpt_template_name: str = "default_ram_template.cpt" # Fallback, but name should come from floor_data
    ) -> bool:
        """
        Creates a .cpt file for the given FloorData by copying a master template.
        Assumes floor_data.ram_model_name is already set to the desired CPT filename.
        Updates FloorData with the filepath and listpath.
        """
        if not floor_data.floor_name: # Internal unique key
            print("Error: FloorData is missing an internal floor_name, cannot process CPT creation logic.")
            return False

        # The CPT filename should now be pre-set in floor_data.ram_model_name
        new_cpt_filename = floor_data.ram_model_name
        if not new_cpt_filename:
            # This case should ideally not be reached if GUI prepares FloorData correctly
            print(f"Error: FloorData for '{floor_data.floor_name}' is missing a ram_model_name. Cannot create CPT.")
            # Fallback naming if absolutely necessary, but this indicates a logic flaw elsewhere
            # sanitized_floor_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in floor_data.floor_name)
            # new_cpt_filename = f"{sanitized_floor_name}.cpt"
            # floor_data.ram_model_name = new_cpt_filename # Update it back
            return False


        target_cpt_filepath = os.path.join(target_version_path, new_cpt_filename)

        # ... (rest of the template finding and copying logic remains largely the same)
        # Ensure project_root is available from self.structure_model.gui_data.root_directory
        project_root = self.structure_model.gui_data.root_directory
        if not project_root:
            print("Error: Project root directory not set. Cannot locate master CPT template.")
            return False

        master_template_relative_path = self.structure_model.gui_data.master_cpt_template_path
        if os.path.isabs(master_template_relative_path):
            master_cpt_template_abs_path = master_template_relative_path
        else:
            master_cpt_template_abs_path = os.path.join(project_root, master_template_relative_path)

        if not os.path.exists(master_cpt_template_abs_path):
            print(f"Error: Master CPT template not found at '{master_cpt_template_abs_path}'. Cannot create CPT for '{floor_data.floor_name}'.")
            # Optional: create placeholder template (as in your original code)
            # ...
            return False # Fail if template is crucial

        try:
            if not os.path.exists(target_version_path):
                os.makedirs(target_version_path)

            shutil.copy2(master_cpt_template_abs_path, target_cpt_filepath)

            # Update FloorData instance (ram_model_name already set)
            floor_data.update_paths(target_cpt_filepath, project_root)

            print(f"Created CPT '{new_cpt_filename}' for floor '{floor_data.floor_name}' (GA Index: {floor_data.floor_index}) in version '{os.path.basename(target_version_path)}'.")
            return True
        except Exception as e:
            print(f"Error creating CPT for '{floor_data.floor_name}': {e}")
            return False

    def open_concept_model_api(self, file_path) -> Tuple["Concept | None", "RAMModel | None"]:
        """Opens a RAM Concept model using the API."""
        # This is from your original structure_model.py
        # Ensure ram_concept library is available in the environment
        try:
            from ram_concept.concept import Concept # type: ignore
        except ImportError:
            print("ERROR: ram_concept library not found. Cannot open CPT files via API.")
            return None, None

        local_folder = os.path.dirname(file_path)
        concept_log_dir = os.path.join(self.structure_model.gui_data.root_directory, "logs")
        if not os.path.exists(concept_log_dir):
            os.makedirs(concept_log_dir)
        concept_log = os.path.join(concept_log_dir, f"ConceptAPI_{datetime.now().strftime('%Y%m%dT%H%M%S')}.log")
        
        try:
            # TODO: Determine if headless should be a setting from gui_data
            headless_setting = not self.structure_model.gui_data.debug # Example: run headless if not debugging
            concept_instance = Concept.start_concept(headless=headless_setting, log_file_path=concept_log)
            model_instance = concept_instance.open_file(file_path)
            return concept_instance, model_instance
        except Exception as e:
            print(f"Error opening RAM Concept model '{file_path}': {e}")
            return None, None

