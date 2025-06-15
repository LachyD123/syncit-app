from dataclasses import dataclass, field, fields, MISSING
import dataclasses # Ensure dataclasses is imported for dataclasses.replace
import os
from fitz import Document as FitzDocument, Page as FitzPage, Annot as FitzAnnot # type: ignore

from typing import List, Optional, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ram_concept.concept import Concept # type: ignore
    from ram_concept.model import Model as RAMModel # type: ignore
else:
    class Concept: pass
    class RAMModel: pass


from .pdf_properties import PdfPageProperties
from .floor_data import FloorData, FloorsData
# Import GUIData and SETTINGS_DEFAULT from the correct location
from gui.gui_data import GUIData, SETTINGS_DEFAULT


class NoPageAbove: pass
class NoPageBelow: pass
from dataclasses import dataclass, field, fields, MISSING
import dataclasses # Ensure dataclasses is imported for dataclasses.replace
import os
from fitz import Document as FitzDocument, Page as FitzPage, Annot as FitzAnnot # type: ignore
from typing import TYPE_CHECKING, List, Dict, Any, Optional

# Assuming PdfPageProperties is imported or defined in the same file or accessible scope
# from .pdf_properties import PdfPageProperties 

if TYPE_CHECKING:
    # from ram_concept.concept import Concept # type: ignore # Not directly used in ModelPage
    # from ram_concept.model import Model as RAMModel # type: ignore # Not directly used in ModelPage
    from .pdf_properties import PdfPageProperties # Forward declaration for type hint
    # Define StructureModel for type hinting if it's in the same file, otherwise import
    # class StructureModel: pass 


# In class ModelPage in structure_model.py:
@dataclass(kw_only=True)
class ModelPage:
    page_fitz: FitzPage | None = field(default=None, repr=False)
    page_properties: Optional['PdfPageProperties'] = None
    structure_model: Optional['StructureModel'] = field(default=None, repr=False)

    is_selected_ga: bool = False
    # is_included_for_linking attribute is completely removed
    linked_cpt_floor_name: Optional[str] = None
    ga_number_display: Optional[str] = None
    
    # ... remove is_included_for_linking from __post_init__ etc. if it exists there.

    @property
    def page_name(self) -> str | None:
        return self.page_properties.page_name if self.page_properties else None

    # ... you will also need to remove 'is_included_for_linking' from
    # __post_init__ and _parse_pdf_pages within the ModelPage class.

    def __post_init__(self):
        if not hasattr(self, 'is_selected_ga'):
            self.is_selected_ga = False
        # if not hasattr(self, 'is_included_for_linking'):
        #     self.is_included_for_linking = False
        if not hasattr(self, 'linked_cpt_floor_name'):
            self.linked_cpt_floor_name = None

    def __getstate__(self):
        state = self.__dict__.copy()
        
        # Ensure PdfPageProperties handles its own Fitz page during its pickling
        if 'page_properties' in state and state['page_properties'] is not None:
            # If PdfPageProperties has its own __getstate__, pickle will call it.
            # If not, and it contains unpicklable types, it would also need handling.
            # Assuming PdfPageProperties.__getstate__ correctly nulls its 'page'.
            # No explicit call to state['page_properties'].__getstate__() needed here,
            # pickle handles it for attributes of types that define __getstate__.
            pass

        state['page_fitz'] = None # Crucial: Do not pickle the live Fitz Page object
        state['structure_model'] = None # Avoid pickling parent, re-linked by StructureModel on load
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # page_fitz is None here, will be restored by StructureModel.__setstate__ by reloading the document
        # and then iterating through all_pdf_pages to re-assign page_fitz based on page_index.
        # structure_model is also None here, will be re-linked by StructureModel.__setstate__
        # after the StructureModel instance itself is created.
        
        # If PdfPageProperties was pickled as a dict (from its own __getstate__),
        # and needs manual re-instantiation, it would be handled here.
        # However, typically, if PdfPageProperties has __setstate__, pickle handles this.
        # For robustness, ensure PdfPageProperties can be restored if it becomes a dict:
        if 'page_properties' in state and isinstance(state['page_properties'], dict):
            # This assumes PdfPageProperties has a suitable __init__ or __setstate__
            # that can reconstruct from this dictionary.
            # For simplicity, if PdfPageProperties has its own __setstate__, this might not be needed.
            # Or, it might be reconstructed directly by pickle if its definition is available.
            # from .pdf_properties import PdfPageProperties # Ensure import is available
            # temp_props = PdfPageProperties.__new__(PdfPageProperties) # Or however it should be re-instantiated
            # temp_props.__setstate__(state['page_properties'])
            # self.page_properties = temp_props
            pass # Assuming PdfPageProperties handles its own __setstate__ properly


@dataclass(kw_only=True)
class GaPage(ModelPage):
    pass

@dataclass(kw_only=True)
class PagesCollection: # Not actively used but kept for structure
    model: 'StructureModel' = field(repr=False)
    pages: List[ModelPage] = field(default_factory=list)

    def append_page(self, page: ModelPage):
        self.pages.append(page)

@dataclass(kw_only=True)
class GaPagesCollection(PagesCollection): # Not actively used but kept for structure
    pages: List[GaPage] = field(default_factory=list) # type: ignore

    def append_ga_page(self, ga_page: GaPage):
        super().append_page(ga_page)


@dataclass(kw_only=True)
class GaAnnot: # Not actively used but kept for structure
    annot_fitz: FitzAnnot | None = None
    ga_page_ref: GaPage | None = field(default=None, repr=False)
    pdf_layer: str | None = None

@dataclass(kw_only=True)
class AnnotProperties: # Used by LegendProperties
    subject: str
    abbreviation: str
    template_annot_xref: int | None = None

    @property
    def template_subject_name(self) -> str:
        return f'{self.subject}_TEMPLATE[{self.abbreviation}]'

@dataclass(kw_only=True)
class LegendProperties:
    legend_page_fitz: FitzPage | None = field(default=None, repr=False)
    _legend_page_index: Optional[int] = field(default=None, repr=False)

    column_under: AnnotProperties = field(default_factory=lambda: AnnotProperties(subject='column_under', abbreviation='CU'))
    column_over: AnnotProperties = field(default_factory=lambda: AnnotProperties(subject='column_over', abbreviation='CO'))
    slab: AnnotProperties = field(default_factory=lambda: AnnotProperties(subject='slab', abbreviation='SL'))    
    wall_over: AnnotProperties = field(default_factory=lambda: AnnotProperties(subject='wall_over', abbreviation='WO'))
    wall_under: AnnotProperties = field(default_factory=lambda: AnnotProperties(subject='wall_under', abbreviation='WU'))

    def __post_init__(self):
        for f_field in fields(self):
            if isinstance(getattr(self, f_field.name), AnnotProperties):
                annot_prop_instance = getattr(self, f_field.name)
                if f_field.name != annot_prop_instance.subject:
                    print(f"Warning/Error: Legend attribute '{f_field.name}' != AnnotProperties subject '{annot_prop_instance.subject}'")
        if self.legend_page_fitz is not None and self._legend_page_index is None:
            try:
                self._legend_page_index = self.legend_page_fitz.number # type: ignore
            except Exception as e:
                print(f"Warning (LegendProperties __post_init__): Could not get page number: {e}")
        if not hasattr(self, '_legend_page_index'): # Ensure field exists for older pickles
            self._legend_page_index = None


    def load_template_annots_from_legend_page(self):
        if not self.legend_page_fitz:
            print("No legend page set to load template annotations from.")
            return

        for f_field in fields(self):
            if isinstance(getattr(self, f_field.name), AnnotProperties):
                annot_prop_instance: AnnotProperties = getattr(self, f_field.name)
                template_found = False
                try:
                    for annot in self.legend_page_fitz.annots(): # type: ignore
                        if annot.info.get('subject') == annot_prop_instance.template_subject_name: # type: ignore    
                            if template_found:
                                print(f"Warning: Multiple template annots found for subject: {annot_prop_instance.subject}. Using first one.")
                            else:
                                annot_prop_instance.template_annot_xref = annot.xref # type: ignore
                                template_found = True
                except Exception as e:
                    print(f"Error accessing annots for legend page: {e}")

                if not template_found:
                    print(f"Warning: Template annotation for '{annot_prop_instance.subject}' (expected: '{annot_prop_instance.template_subject_name}') not found on legend page.")
    
    def __getstate__(self):
        """Prepare LegendProperties for pickling by removing live fitz.Page object."""
        state = self.__dict__.copy()
        if self.legend_page_fitz is not None and state.get('_legend_page_index') is None:
            try:
                state['_legend_page_index'] = self.legend_page_fitz.number # type: ignore
            except Exception: # NOSONAR
                pass # Error already printed if it occurs
        state['legend_page_fitz'] = None
        return state

    def __setstate__(self, state):
        """Restore LegendProperties after unpickling."""
        self.__dict__.update(state)
        # legend_page_fitz is restored by StructureModel.__setstate__


@dataclass(kw_only=True)
class StructureModel:
    gui_data: GUIData = field(default_factory=GUIData) # Now defaults to an empty GUIData object
    floors_data: FloorsData = field(default_factory=lambda: FloorsData())

    pdf_document: FitzDocument | None = field(default=None, repr=False)
    all_pdf_pages: List[ModelPage] = field(default_factory=list) # Stores ModelPage instances

    legend_properties: LegendProperties | None = None
    etabs_model_path: str | None = None # Example, not currently used in logic

    def __post_init__(self):
        if self.floors_data.model is None:
            self.floors_data.model = self
        
        # Ensure gui_data is an instance of GUIData. If loaded from an older pickle, it might be a dict.
        # This is more robustly handled in ProjectManager.load_project_data, but a check here is good.
        if not isinstance(self.gui_data, GUIData):
            print("Warning: self.gui_data was not a GUIData instance in __post_init__. Re-initializing from dict.")
            current_data_dict = self.gui_data if isinstance(self.gui_data, dict) else {}
            # Merge with defaults to ensure all fields are present
            merged_data = SETTINGS_DEFAULT.copy()
            merged_data.update(current_data_dict)
            self.gui_data = GUIData.from_dict(merged_data)


        # Load PDF if path is available and document not already loaded (e.g., by __setstate__)
        if not self.pdf_document:
            pdf_to_load = self.gui_data.current_pdf_binder_full_path # Uses the property
            if pdf_to_load and os.path.exists(pdf_to_load):
                self.load_pdf_document(pdf_to_load)
            # No fallback to self.gui_data.pdf_binder_path here, as current_pdf_binder_full_path handles it.


    def __getstate__(self):
        state = self.__dict__.copy()
        state['pdf_document'] = None # Don't pickle FitzDocument

        # ModelPage objects in all_pdf_pages already handle their page_fitz for pickling (it's transient)
        # LegendProperties also handles its legend_page_fitz via its own __getstate__
        if state.get('legend_properties') and isinstance(state['legend_properties'], LegendProperties):
             state['legend_properties'] = state['legend_properties'].__getstate__()

        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

        # Ensure gui_data is properly initialized (ProjectManager.load_project_data is primary handler)
        if not isinstance(self.gui_data, GUIData):
            print("Warning: self.gui_data was not a GUIData instance in __setstate__. Re-initializing.")
            current_data_dict = self.gui_data if isinstance(self.gui_data, dict) else {}
            merged_data = SETTINGS_DEFAULT.copy()
            merged_data.update(current_data_dict)
            self.gui_data = GUIData.from_dict(merged_data)


        self.pdf_document = None # Ensure it's None before attempting to load
        pdf_path_to_load_on_restore = self.gui_data.current_pdf_binder_full_path # Uses property

        if pdf_path_to_load_on_restore and os.path.exists(pdf_path_to_load_on_restore):
            try:
                # print(f"StructureModel __setstate__: Restoring PDF document from: {pdf_path_to_load_on_restore}")
                self.pdf_document = FitzDocument(pdf_path_to_load_on_restore)

                # Restore page_fitz for each ModelPage
                restored_all_pdf_pages = []
                for mp_shell in self.all_pdf_pages: # These are ModelPage shells
                    if mp_shell.page_properties and mp_shell.page_properties.page_index is not None and \
                       0 <= mp_shell.page_properties.page_index < self.pdf_document.page_count:
                        
                        fitz_page_obj = self.pdf_document[mp_shell.page_properties.page_index]
                        # Re-link the fitz_page_obj to the PdfPageProperties inside ModelPage
                        if mp_shell.page_properties:
                             mp_shell.page_properties.restore_fitz_page_and_recalculate(fitz_page_obj)

                        # Update the ModelPage shell with the live fitz_page and self reference
                        # Using dataclasses.replace is safer for immutable dataclasses or complex __init__
                        new_mp = dataclasses.replace(mp_shell, 
                                                     page_fitz=fitz_page_obj, 
                                                     structure_model=self)
                        restored_all_pdf_pages.append(new_mp)
                    else:
                        # print(f"Warning (StructureModel __setstate__): Could not restore page_fitz for ModelPage, index issue: {mp_shell.page_properties}")
                        restored_all_pdf_pages.append(dataclasses.replace(mp_shell, page_fitz=None, structure_model=self))
                self.all_pdf_pages = restored_all_pdf_pages
                
                # Restore legend_page_fitz if legend_properties exists
                if self.legend_properties and isinstance(self.legend_properties, dict): # If it was stored as dict from older pickle
                    temp_legend_page_index = self.legend_properties.get('_legend_page_index')
                    self.legend_properties = LegendProperties(**self.legend_properties) # Recreate instance
                    self.legend_properties._legend_page_index = temp_legend_page_index


                if self.legend_properties and self.legend_properties._legend_page_index is not None:
                    if 0 <= self.legend_properties._legend_page_index < self.pdf_document.page_count:
                        self.legend_properties.legend_page_fitz = self.pdf_document[self.legend_properties._legend_page_index]
                        self.legend_properties.load_template_annots_from_legend_page()
                    else:
                        # print(f"Warning (StructureModel __setstate__): Legend page index {self.legend_properties._legend_page_index} out of bounds.")
                        self.legend_properties.legend_page_fitz = None
            except Exception as e:
                print(f"Error re-loading PDF document during StructureModel unpickling from '{pdf_path_to_load_on_restore}': {e}")
                self.pdf_document = None
                for mp in self.all_pdf_pages: mp.page_fitz = None
                if self.legend_properties: self.legend_properties.legend_page_fitz = None
        else:
            # print("No valid PDF path in gui_data during StructureModel unpickle, PDF objects not restored.")
            for mp in self.all_pdf_pages: mp.page_fitz = None # Ensure all are None
            if self.legend_properties: self.legend_properties.legend_page_fitz = None


        # Re-link parent models
        if self.floors_data:
            self.floors_data.model = self
            for floor_key in list(self.floors_data.floors.keys()): # Iterate over keys for safe modification
                floor = self.floors_data.floors[floor_key]
                floor.structure_model = self
                floor.floors_data_parent = self.floors_data
                # Restore ga_page_fitz in FloorData
                if floor._ga_page_index is not None and self.pdf_document and \
                   0 <= floor._ga_page_index < self.pdf_document.page_count:
                    try:
                        floor.ga_page_fitz = self.pdf_document[floor._ga_page_index]
                    except Exception as e_fd_pdf:
                        print(f"Error restoring ga_page_fitz for FloorData '{floor.floor_name}': {e_fd_pdf}")
                        floor.ga_page_fitz = None
                elif floor._ga_page_index is not None: # PDF not loaded or index out of bounds
                     floor.ga_page_fitz = None


    def load_pdf_document(self, pdf_path: str):
        if not pdf_path or not os.path.exists(pdf_path):
            print(f"Error: PDF document not found or path is invalid: '{pdf_path}'")
            if self.pdf_document and hasattr(self.pdf_document, 'name') and self.pdf_document.name == os.path.abspath(pdf_path):
                self.pdf_document.close() # Close if it's the same one being invalidated
                self.pdf_document = None
                self.all_pdf_pages.clear()
            return

        try:
            existing_links = {}
            if self.pdf_document and hasattr(self.pdf_document, 'name') and self.pdf_document.name == os.path.abspath(pdf_path):
                for mp in self.all_pdf_pages:
                    if mp.page_name:
                        existing_links[mp.page_name] = {
                            "is_selected_ga": mp.is_selected_ga,
                            "is_included_for_linking": mp.is_included_for_linking,
                            "linked_cpt_floor_name": mp.linked_cpt_floor_name
                        }
                self.pdf_document.close() # Close existing before reopening

            self.pdf_document = FitzDocument(pdf_path)
            self._parse_pdf_pages(existing_links_to_restore=existing_links)

            if self.pdf_document and self.pdf_document.page_count > 0:
                if self.legend_properties and self.legend_properties._legend_page_index is not None:
                    if 0 <= self.legend_properties._legend_page_index < self.pdf_document.page_count:
                        self.legend_properties.legend_page_fitz = self.pdf_document[self.legend_properties._legend_page_index]
                        self.legend_properties.load_template_annots_from_legend_page()
                    else: # Index out of bounds for new PDF
                        self.set_legend_properties_from_pdf_page() # Default to first page
                elif not self.legend_properties :
                    self.set_legend_properties_from_pdf_page()
                elif self.legend_properties and self.legend_properties._legend_page_index is None:
                     self.set_legend_properties_from_pdf_page()
            # print(f"PDF document '{pdf_path}' loaded with {self.pdf_document.page_count if self.pdf_document else 'N/A'} pages.")
        except Exception as e:
            print(f"Error loading PDF document '{pdf_path}': {e}")
            if self.pdf_document: self.pdf_document.close()
            self.pdf_document = None
            self.all_pdf_pages.clear()
# In class StructureModel in structure_model.py:
    def _parse_pdf_pages(self, existing_links_to_restore: Optional[Dict[str, Dict]] = None):
        if not self.pdf_document:
            return
        self.all_pdf_pages.clear()

        for i, fitz_page_obj in enumerate(self.pdf_document):
            page_name_identifier = f"Page_{i+1}"

            page_props = PdfPageProperties(
                page=fitz_page_obj,
                page_index=i,
                page_name=page_name_identifier,
                drawing_scale=self.gui_data.drawing_scale_1_to,
                paper_size_key='A1'
            )
            
            restored_info = existing_links_to_restore.get(page_name_identifier) if existing_links_to_restore else None
            
            is_ga = restored_info["is_selected_ga"] if restored_info else False
            linked_cpt = restored_info["linked_cpt_floor_name"] if restored_info else None

            model_page = ModelPage(
                page_fitz=fitz_page_obj,
                page_properties=page_props,
                structure_model=self,
                is_selected_ga=is_ga,
                linked_cpt_floor_name=linked_cpt
            )
            self.all_pdf_pages.append(model_page)

    def set_legend_properties_from_pdf_page(self, page_index: int = 0):
        if self.pdf_document and 0 <= page_index < self.pdf_document.page_count:
            legend_fitz_page = self.pdf_document[page_index]
            self.legend_properties = LegendProperties(legend_page_fitz=legend_fitz_page, _legend_page_index=page_index)
            self.legend_properties.load_template_annots_from_legend_page()
            # print(f"Legend properties set from PDF page {page_index}.")
        else:
            # print(f"Cannot set legend: PDF document not loaded or page index {page_index} out of bounds.")    
            if self.legend_properties: # If it exists but cannot be set from PDF
                self.legend_properties.legend_page_fitz = None
                self.legend_properties._legend_page_index = None
            else: # If it doesn't exist at all
                self.legend_properties = LegendProperties(_legend_page_index=None)


    def get_floor_by_name(self, name: str) -> FloorData | None:
        return self.floors_data.get_floor_by_name(name)

    def get_model_page_by_identifier(self, page_identifier: str) -> Optional[ModelPage]:
        for mp in self.all_pdf_pages:
            if mp.page_name == page_identifier:
                return mp
        return None

    def add_floor(self, floor_data_instance: FloorData):
        self.floors_data.add_floor(floor_data_instance)

    def clear_all_floor_data(self):
        self.floors_data.clear_floors()
        if self.gui_data: # Ensure gui_data exists
            self.gui_data.included_files.clear()

    def get_ordered_floors(self) -> List[FloorData]:
        return self.floors_data.get_ordered_floors()

    def update_gui_included_files_from_floors(self):
        """
        Updates the list of included CPT ram_model_names in GUIData
        based on the is_included status of FloorData objects.
        """
        if self.gui_data: # Ensure gui_data exists
            ordered_floors = self.get_ordered_floors()
            self.gui_data.included_files = [
                f.ram_model_name for f in ordered_floors if f.is_included and f.ram_model_name
            ]
