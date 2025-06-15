from dataclasses import dataclass, field, fields, asdict, MISSING
import os

# Directory name for storing PDF binder versions
PDF_BINDERS_DIR_NAME = "PDF_BINDERS" # Retained as it's used by ProjectManager

# Default master CPT template path relative to project root
DEFAULT_MASTER_CPT_TEMPLATE_PATH = "file_templates/default_ram_template.cpt"

@dataclass
class CPTFile:
    """Placeholder for CPT file data if detailed row data is needed."""
    # Example fields, assuming these might come from a CPT table or GUI
    name: str | None = None
    path: str | None = None
    is_included: bool = True
    order_index: int | None = None
    # Add other fields as necessary


@dataclass
class CPTFiles:
    """Placeholder for a collection of CPTFile objects."""
    cpt_files: list[CPTFile] = field(default_factory=list)


@dataclass
class PDFBinderPage:
    """Placeholder for PDF binder page data if detailed row data is needed."""
    page_name: str | None = None
    page_index: int | None = None
    is_ga: bool = False
    linked_cpt_name: str | None = None
    # Add other fields as necessary


@dataclass
class PDFBinderPages:
    """Placeholder for a collection of PDFBinderPage objects."""
    pdf_pages: list[PDFBinderPage] = field(default_factory=list)


@dataclass
class GUIData:
    """
    Central data store for GUI settings and state.
    This object is part of StructureModel and is pickled with it.
    """
    root_directory: str | None = None

    # CPT Version Management
    cpt_active_folder_name: str | None = None
    cpt_active_folder_path: str | None = None
    # cpt_files: CPTFiles | None = None # Kept as placeholder; main CPT list is in FloorsData

    # PDF Binder Version Management
    active_pdf_binder_version_name: str | None = None # Name of the version folder (e.g., "V1.0.0 - Initial Import")
    active_pdf_binder_version_path: str | None = None # Full path to the PDF version folder
    pdf_binder_filename_in_version: str | None = None   # Filename of the PDF within that version folder (e.g., "Binder.pdf")
    # pdf_binder_pages: PDFBinderPages | None = None # Kept as placeholder; main PDF page list is in StructureModel.all_pdf_pages

    # General paths and settings
    pdf_binder_path: str | None = None # Legacy or fallback if not using versioning, or can be derived.
                                     # Generally, current_pdf_binder_full_path should be preferred.
    included_files: list[str] = field(default_factory=list) # List of ram_model_names of CPTs to include
    master_cpt_template_path: str = DEFAULT_MASTER_CPT_TEMPLATE_PATH # Relative to project root or absolute

    # Other UI related settings (examples)
    drawing_scale_1_to: float = 100.0
    debug: bool = False # Example setting that might influence core logic (e.g., headless for CPTManager)

    # UI State (less common to store here unless critical for project, e.g., last active tab)
    # last_active_tab_index: int = 0

    @property
    def current_pdf_binder_full_path(self) -> str | None:
        """
        Returns the full absolute path to the PDF binder file in the active PDF version.
        If versioned PDF is not set, falls back to pdf_binder_path.
        """
        if self.active_pdf_binder_version_path and self.pdf_binder_filename_in_version:
            return os.path.join(self.active_pdf_binder_version_path, self.pdf_binder_filename_in_version)
        
        # Fallback for non-versioned or older data:
        # If pdf_binder_path is an absolute path to an existing file, use it.
        if self.pdf_binder_path and os.path.isabs(self.pdf_binder_path) and os.path.exists(self.pdf_binder_path):
            return self.pdf_binder_path
        
        # If pdf_binder_path is relative and root_directory is set, try to resolve it.
        if self.pdf_binder_path and self.root_directory and \
           os.path.exists(os.path.join(self.root_directory, self.pdf_binder_path)):
            return os.path.join(self.root_directory, self.pdf_binder_path)
            
        return None

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a GUIData instance from a dictionary.
        Uses default values for missing keys.
        """
        # Get all field names and their default values from the dataclass definition
        known_fields = {f.name: f.default if f.default is not MISSING else (f.default_factory() if f.default_factory is not MISSING else None)
                        for f in fields(cls)}
        
        # Prepare arguments for instantiation, using data values or defaults
        instance_args = {}
        for f_name, f_default in known_fields.items():
            instance_args[f_name] = data.get(f_name, f_default)

        # Handle specific type conversions if necessary (e.g., for nested dataclasses if they were actively used)
        # For CPTFiles and PDFBinderPages, if they were to be populated from dict:
        # if 'cpt_files' in instance_args and isinstance(instance_args['cpt_files'], dict):
        #     instance_args['cpt_files'] = CPTFiles.from_dict(instance_args['cpt_files']) # Assuming CPTFiles has from_dict
        # if 'pdf_binder_pages' in instance_args and isinstance(instance_args['pdf_binder_pages'], dict):
        #     instance_args['pdf_binder_pages'] = PDFBinderPages.from_dict(instance_args['pdf_binder_pages'])

        return cls(**instance_args)

    def to_variable_dict(self) -> dict:
        """
        Converts the GUIData instance to a dictionary.
        This is useful for passing to scripts or other serialization needs,
        though pickling is the primary persistence.
        """
        # asdict handles nested dataclasses correctly if they are used
        return asdict(self)

# SETTINGS_DEFAULT: This dictionary is used for initializing a new GUIData
# object when no pickled data is found, or for merging with older pickled data.
SETTINGS_DEFAULT = {
    "ROOT_DIRECTORY": None,
    "CPT_ACTIVE_FOLDER_NAME": None,
    "CPT_ACTIVE_FOLDER_PATH": None,
    # "CPT_FILES": {}, # For CPTFiles, if it were a dict in SETTINGS_DEFAULT
    "ACTIVE_PDF_BINDER_VERSION_NAME": None,
    "ACTIVE_PDF_BINDER_VERSION_PATH": None,
    "PDF_BINDER_FILENAME_IN_VERSION": None,
    # "PDF_BINDER_PAGES": {}, # For PDFBinderPages
    "PDF_BINDER_PATH": None,
    "INCLUDED_FILES": [],
    "MASTER_CPT_TEMPLATE_PATH": DEFAULT_MASTER_CPT_TEMPLATE_PATH,
    "DRAWING_SCALE_1_TO": 100.0,
    "DEBUG": False,
    # "LAST_ACTIVE_TAB_INDEX": 0,
}
