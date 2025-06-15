from dataclasses import dataclass, field
from typing import Optional
from fitz import Page, Rect # type: ignore

A1_SIZE = dict(
    width=594,  # mm
    height=841, # mm
)

PAPER_SIZES = dict(
    A1=A1_SIZE
)

@dataclass(kw_only=True)
class PdfPageProperties:
    page: Page | None = field(default=None, repr=False) # To be handled for pickling
    paper_size_key: str = 'A1'
    drawing_scale: float = 100.0
    page_index: int | None = None # This is crucial for restoring the 'page'
    page_name: str | None = None 

    drawing_width_mm: float | None = None
    drawing_height_mm: float | None = None 
    
    page_bound_width: float | None = None 
    page_bound_height: float | None = None 
    
    annot_x_to_mm_factor: float | None = None
    annot_y_to_mm_factor: float | None = None
    mm_x_to_annot_factor: float | None = None
    mm_y_to_annot_factor: float | None = None

    def __post_init__(self):
        # Calculate dimensions and factors if 'page' is present
        self._calculate_derived_properties()
        # Ensure page_index is set if page is available (important for pickling)
        if self.page is not None and self.page_index is None:
            self.page_index = self.page.number # type: ignore

    def _calculate_derived_properties(self):
        """Calculates dimensions and conversion factors if self.page is set."""
        if self.paper_size_key in PAPER_SIZES:
            self.drawing_width_mm = float(PAPER_SIZES[self.paper_size_key]['width'])
            self.drawing_height_mm = float(PAPER_SIZES[self.paper_size_key]['height'])
        else:
            print(f"Warning: Unknown paper size key '{self.paper_size_key}'. Using A1 defaults for calculation.")
            self.drawing_width_mm = float(PAPER_SIZES['A1']['width'])
            self.drawing_height_mm = float(PAPER_SIZES['A1']['height'])

        if self.page: # Check if the fitz.Page object is available
            page_bound: Rect = self.page.bound()
            self.page_bound_width = float(page_bound.width)
            self.page_bound_height = float(page_bound.height)

            if self.page_bound_width > 0 and self.page_bound_height > 0 and \
               self.drawing_width_mm is not None and self.drawing_height_mm is not None:
                self.annot_x_to_mm_factor = self.drawing_scale * (self.drawing_width_mm / self.page_bound_width)
                self.annot_y_to_mm_factor = self.drawing_scale * (self.drawing_height_mm / self.page_bound_height)
                
                if self.annot_x_to_mm_factor != 0:
                    self.mm_x_to_annot_factor = 1.0 / self.annot_x_to_mm_factor
                if self.annot_y_to_mm_factor != 0:
                    self.mm_y_to_annot_factor = 1.0 / self.annot_y_to_mm_factor
            else:
                print("Warning (PdfPageProperties): Could not calculate factors due to missing page dimensions or drawing dimensions.")
        # else:
            # If self.page is None, factors cannot be calculated. They will remain None.
            # print("Warning (PdfPageProperties): Initialized without a Page object or page dimensions. Factors will not be calculated.")


    def __getstate__(self):
        """Prepare the object for pickling."""
        state = self.__dict__.copy()
        # Ensure page_index is stored if 'page' exists (should be handled by __post_init__)
        if self.page is not None and state.get('page_index') is None:
             state['page_index'] = self.page.number # type: ignore
        state['page'] = None  # Don't pickle the fitz.Page object itself
        return state

    def __setstate__(self, state):
        """Restore the object after unpickling."""
        self.__dict__.update(state)
        # The 'page' attribute (fitz.Page) is None at this point.
        # It needs to be restored by the parent object (ModelPage or StructureModel)
        # after the main FitzDocument is reloaded, using self.page_index.
        # We can, however, recalculate other properties if page_index is present
        # but this is better done once the 'page' object is restored.
        # For now, _calculate_derived_properties will only run if self.page is not None.
        # If self.page is restored later, _calculate_derived_properties should be called again.

    def restore_fitz_page_and_recalculate(self, fitz_page_object: Page):
        """Restores the fitz.Page object and recalculates derived properties."""
        self.page = fitz_page_object
        if self.page is not None and self.page_index is None: # Ensure index consistency
            self.page_index = self.page.number # type: ignore
        elif self.page is not None and self.page_index != self.page.number: # type: ignore
             print(f"Warning: Restored page index {self.page.number} differs from stored {self.page_index}") # type: ignore
             self.page_index = self.page.number # type: ignore
        self._calculate_derived_properties()

