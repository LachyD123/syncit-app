# core_logic/pdf_processor.py
import os
import shutil
from typing import List, Dict, Any, Tuple
from fitz import Document as FitzDocument, Page as FitzPage # type: ignore

from data_model.pdf_properties import PdfPageProperties
from data_model.floor_data import FloorData
from data_model.structure_model import StructureModel, GaPage # For type hinting if needed

class PDFProcessor:
    def __init__(self, structure_model: StructureModel):
        self.structure_model = structure_model

    def process_pdf_binder_to_floor_data(self, pdf_binder_path: str) -> List[FloorData]:
        """
        Processes a PDF binder, identifies GA pages, and prepares FloorData objects.
        This method assumes each page in the binder is a GA.
        It does NOT create CPT files here; that's handled by CPTManager.
        """
        created_floor_data_list: List[FloorData] = []
        if not os.path.exists(pdf_binder_path):
            print(f"Error: PDF Binder not found at '{pdf_binder_path}'")
            return created_floor_data_list

        try:
            doc: FitzDocument = FitzDocument(pdf_binder_path)
        except Exception as e:
            print(f"Error opening PDF binder '{pdf_binder_path}': {e}")
            return created_floor_data_list

        for i, fitz_page in enumerate(doc):
            page_num = i + 1
            # Create PdfPageProperties for this page
            # Scale and paper size might come from GUI settings or be defaults
            pdf_props = PdfPageProperties(
                page=fitz_page, 
                page_index=i,
                page_name=f"BinderPage_{page_num}", # Default name
                drawing_scale=self.structure_model.gui_data.drawing_scale_1_to,
                paper_size_key='A1' # Or from GUI settings
            )

            # Create a GaPage object (optional, if you need to store GaPage instances separately)
            # ga_page_obj = GaPage(
            #     page_fitz=fitz_page,
            #     page_properties=pdf_props,
            #     structure_model=self.structure_model
            # )
            # self.structure_model.ga_pages_list.append(ga_page_obj) # If managing a list of GaPage

            # Create FloorData based on this PDF page
            # CPT related fields (ram_model_name, filepath, listpath) will be populated
            # when the template CPT is actually created by CPTManager.
            floor_name_key = f"Floor_From_PDF_Page_{page_num}" # Unique key for the dictionary
            
            fd = FloorData(
                floor_name=floor_name_key,
                floor_index=page_num, # Initial index based on PDF page order
                ga_page_fitz=fitz_page, # Store the fitz page
                pdf_page_ref_text=f"{os.path.basename(pdf_binder_path)}, Page {page_num}",
                is_included=True, # Default to include new floors from PDF
                typical_count=1,
                structure_model=self.structure_model,
                # ram_model_name, filepath, listpath will be set later
            )
            created_floor_data_list.append(fd)
            
        doc.close()
        print(f"Processed {len(created_floor_data_list)} pages from PDF binder '{pdf_binder_path}'.")
        return created_floor_data_list

