# data_model/floor_data.py

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Any, Optional
from fitz import Page as FitzPage # type: ignore

if TYPE_CHECKING:
    from .structure_model import StructureModel
    from .slab_data import SlabMeshData
    from .wall_data import WallsData
    from .column_data import ColumnsData

@dataclass
class FloorData:
    floor_name: str
    floor_index: int | None = None

    ram_model_name: str | None = None
    filepath: str | None = None
    listpath: str | None = None

    ga_page_fitz: FitzPage | None = field(default=None, repr=False)
    _ga_page_index: Optional[int] = field(default=None, repr=False)

    pdf_page_ref_text: str | None = None
    linked_pdf_page_identifier: Optional[str] = None

    # --- NEW FIELD ---
    is_placeholder: bool = False # To identify floors created from GAs before CPTs exist

    slab_data: 'SlabMeshData | None' = None
    walls_over_data: 'WallsData | None' = None
    walls_under_data: 'WallsData | None' = None
    columns_over_data: 'ColumnsData | None' = None
    columns_under_data: 'ColumnsData | None' = None

    toc: float | None = None
    default_toc: float | None = None
    priority: int | None = None
    typical_count: int = 1
    is_included: bool = True
    to_be_updated: bool = True

    structure_model: 'StructureModel | None' = field(default=None, repr=False)
    floors_data_parent: 'FloorsData | None' = field(default=None, repr=False)

    def __post_init__(self):
        if self.typical_count < 1:
            self.typical_count = 1
        if self.ram_model_name and not self.filepath:
            print(f"Warning: FloorData '{self.floor_name}' has ram_model_name but no filepath.")
        if not hasattr(self, 'linked_pdf_page_identifier'):
            self.linked_pdf_page_identifier = None
        if self.ga_page_fitz is not None and self._ga_page_index is None:
            try:
                self._ga_page_index = self.ga_page_fitz.number # type: ignore
            except Exception as e:
                print(f"Warning: Could not get page number for ga_page_fitz in FloorData '{self.floor_name}': {e}")
        if not hasattr(self, '_ga_page_index'): # Ensure field exists for older pickles
            self._ga_page_index = None
        # --- NEW POST_INIT LOGIC ---
        if not hasattr(self, 'is_placeholder'):
            self.is_placeholder = False


    def update_paths(self, new_absolute_cpt_path: str, project_root_dir: str):
        import os
        self.filepath = new_absolute_cpt_path
        if project_root_dir and new_absolute_cpt_path:
            try:
                self.listpath = os.path.relpath(new_absolute_cpt_path, project_root_dir).replace("\\", "/")
            except ValueError:
                self.listpath = new_absolute_cpt_path
        else:
            self.listpath = new_absolute_cpt_path

    def __getstate__(self):
        state = self.__dict__.copy()
        if self.ga_page_fitz is not None and state.get('_ga_page_index') is None:
            try:
                state['_ga_page_index'] = self.ga_page_fitz.number # type: ignore
            except Exception as e:
                print(f"Warning (getstate): Could not get page number for ga_page_fitz in FloorData '{self.floor_name}': {e}")
                state['_ga_page_index'] = None # Ensure it's None if error
        state['ga_page_fitz'] = None  # Don't pickle the fitz.Page object
        state['structure_model'] = None # Avoid pickling parent, re-linked by FloorsData/StructureModel
        state['floors_data_parent'] = None # Avoid pickling parent
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # ga_page_fitz will be None here. It needs to be restored by StructureModel.__setstate__
        # after the main FitzDocument is reloaded, using self._ga_page_index.
        # structure_model and floors_data_parent also need to be re-linked by the parent.
        if not hasattr(self, '_ga_page_index'): # Ensure field exists for older pickles
            self._ga_page_index = None
        # --- NEW SETSTATE LOGIC ---
        if not hasattr(self, 'is_placeholder'):
            self.is_placeholder = False

# The rest of the file (FloorsData class) remains unchanged.

@dataclass
class FloorsData:
    model: 'StructureModel | None' = field(default=None, repr=False)
    floors: Dict[str, FloorData] = field(default_factory=dict) 

    def add_floor(self, floor_data_instance: FloorData):
        if floor_data_instance.floor_name in self.floors:
            print(f"Warning: Floor with name '{floor_data_instance.floor_name}' already exists. Overwriting.")
        floor_data_instance.floors_data_parent = self
        floor_data_instance.structure_model = self.model
        self.floors[floor_data_instance.floor_name] = floor_data_instance

    def get_floor_by_name(self, name: str) -> FloorData | None:
        return self.floors.get(name)

    def get_ordered_floors(self) -> list[FloorData]:
        if not self.floors:
            return []
        
        def sort_key(fd: FloorData):
            index_val = getattr(fd, 'floor_index', float('inf'))
            if not isinstance(index_val, (int, float)):
                try:
                    index_val = int(index_val)
                except (ValueError, TypeError):
                    index_val = float('inf') 
            
            name_val = getattr(fd, 'floor_name', '')
            return (index_val, name_val)

        return sorted(list(self.floors.values()), key=sort_key)

    def remove_floor(self, floor_name: str):
        if floor_name in self.floors:
            del self.floors[floor_name]
        else:
            print(f"Warning: Floor with name '{floor_name}' not found for removal.")

    def clear_floors(self):
        self.floors.clear()

    def re_index_floors(self):
        ordered_floors = self.get_ordered_floors()
        for i, fd_obj in enumerate(ordered_floors):
            fd_obj.floor_index = i + 1
    
    # No __getstate__/__setstate__ needed for FloorsData itself if FloorData handles its components,
    # and StructureModel handles FloorsData.
