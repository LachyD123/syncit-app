from dataclasses import dataclass, field
from shapely.geometry import MultiPolygon, Polygon, Point

from ram_concept.point_2D import Point2D as RAMPoint2D

from ram_concept.column import Column as Ram
import typing
from fitz import Annot, Rect
from ..core_logic.pdf_processor import GaPage
from ram_concept.column import Column as RamColumn
from ram_concept.structure_layer import StructureLayer
import fitz

from ..core_logic.pdf_processor import PdfPageProperties
from .structure_model import GaAnnot
if typing.TYPE_CHECKING:
    from .structure_model import StructureModel
    from .floor_data import FloorData
    from .structure_model import StructureModel
    from .column_data import ColumnMesh

from ram_concept.model import Model as RAMModel
from ..utils.data_type_conversions import RamToShapely, ShapelyToRam

def Ram_poly_to_shapely_poly(ram_poly):
    return MultiPolygon(Polygon([(ram_point.x,ram_point.y) for ram_point in ram_poly]))

import fitz  # PyMuPDF
from shapely.geometry import box as sp_box
from shapely.affinity import rotate as shapely_rotate
from shapely.affinity import scale as shapely_scale
import fitz  # PyMuPDF
from shapely.affinity import translate as shapely_translate

def convert_points_to_mm(points):
    """Convert points to millimeters."""
    return points * 705.9654

def get_annotation_content_width_in_mm(annot, scale=100):
    """Get the content width of an annotation in millimeters, adjusted for scale."""
    # Get the bounding box of the annotation
    bbox = annot.rect

    # Get the border width of the annotation
    border_width = annot.border.get("width", 0)
    print(f"==>> border_width: {border_width}")

    # Calculate the content width by excluding the border
    content_width_points = bbox.width - (2 * border_width)  # Width in points

    # Convert the content width to millimeters
    content_width_mm = convert_points_to_mm(content_width_points)

    # Since the PDF is at 1:100 scale, multiply by the scale factor
    real_world_width_mm = content_width_mm / scale

    print(f"==>> real_world_width_mm: {real_world_width_mm}")
    return round(real_world_width_mm)

def get_annotation_content_width_in_mm(annot, scale=100):
    """Get the content width of an annotation in millimeters, adjusted for scale."""
    # Get the bounding box of the annotation
    bbox = annot.rect

    # Get the border width of the annotation
    border_width = annot.border.get("width", 0)
    print(f"==>> border_width: {border_width}")

    # Calculate the content width by excluding the border
    content_width_points = bbox.width - (2 * border_width)  # Width in points
    print(f"==>> content_width_points: {content_width_points}")

    # Convert the content width to millimeters
    content_width_mm = convert_points_to_mm(content_width_points)

    # Since the PDF is at 1:100 scale, multiply by the scale factor
    real_world_width_mm = content_width_mm / scale

    print(f"==>> real_world_width_mm: {real_world_width_mm}")
    return round(real_world_width_mm)

def get_annotation_content_height_in_mm(annot, scale=100):
    """Get the content height of an annotation in millimeters, adjusted for scale."""
    # Get the bounding box of the annotation
    bbox = annot.rect

    # Get the border width of the annotation
    border_width = annot.border.get("width", 0)

    # Calculate the content height by excluding the border
    content_height_points = bbox.height - (2 * border_width)  # Height in points

    # Convert the content height to millimeters
    content_height_mm = convert_points_to_mm(content_height_points)

    # Adjust for the 1:100 scale
    real_world_height_mm = content_height_mm / scale

    return round(real_world_height_mm)

def get_annotation_center(annot):
    """Get the center of the annotation's rectangle in points."""
    rect = annot.rect
    center_x = (rect.x0 + rect.x1) / 2
    center_y = (rect.y0 + rect.y1) / 2
    return center_x, center_y

def get_annotation_center_in_mm_point(annot, page_height, scale=100):
    """Get the center of the annotation's rectangle in millimeters, adjusted for a 1:100 scale.
    Coordinates are given with respect to a coordinate system where the origin is at the top-left of the page.
    """
    center_x, center_y = get_annotation_center(annot)
    
    # Convert points to millimeters
    center_x_mm = convert_points_to_mm(center_x) * scale
    center_y_mm = convert_points_to_mm(center_y) * scale
    
    # Adjust the y-coordinate to have the origin at the top-left
    adjusted_center_y_mm = convert_points_to_mm(page_height) * scale - center_y_mm
    
    return Point(center_x_mm, adjusted_center_y_mm)

def extract_rotation_from_source(annot: Annot, doc: fitz.Document):
    """Extract the rotation of an annotation by inspecting the raw PDF object."""
    
    # Get the raw PDF object string for the annotation
    annot_xref = annot.xref
    annot_source = doc.xref_object(annot_xref, compressed=False)
    print(f"==>> annot_source: {annot_source}")
    
    # Search for the /Rotation entry in the source
    rotation = 0  # Default rotation
    if "/Rotation" in annot_source:
        # Extract the rotation value
        rotation_str = annot_source.split("/Rotation")[1].split()[0]
        print(f"==>> rotation_str: {rotation_str}")
        rotation = int(rotation_str)
    print(f"==>> rotationwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww: {rotation}")
    return rotation

def extract_and_update_rotation(annot: fitz.Annot, doc: fitz.Document, new_rotation: int):
    """Extract the rotation of an annotation and update it to a new angle."""
    
    # Get the raw PDF object string for the annotation
    annot_xref = annot.xref
    annot_source = doc.xref_object(annot_xref, compressed=False)
    print(f"==>> Original annot_source: {annot_source}")

    # Search for the /Rotation entry in the source
    if "/Rotation" in annot_source:
        # Extract the existing rotation value
        rotation_str = annot_source.split("/Rotation")[1].split()[0]
        print(f"==>> Existing rotation_str: {rotation_str}")
        
        # Replace the old rotation value with the new one
        annot_source = annot_source.replace(f"/Rotation {rotation_str}", f"/Rotation {new_rotation}")
        print(f"==>> Updated annot_source: {annot_source}")
    else:
        # If /Rotation is not found, add it with the new rotation value
        insert_position = annot_source.find(">>")
        annot_source = annot_source[:insert_position] + f"/Rotation {new_rotation} " + annot_source[insert_position:]
        print(f"==>> Annot source with added rotation: {annot_source}")
    
    # Update the annotation in the PDF with the modified source
    # doc.update_object(annot_xref, annot_source)



# def extract_and_update_poly_to_rect(annot: fitz.Annot, doc: fitz.Document, new_rotation: int):
#     """Extract the rotation of an annotation and update it to a new angle."""
    
#     # Get the raw PDF object string for the annotation
#     annot_xref = annot.xref
#     annot_source = doc.xref_object(annot_xref, compressed=False)
#     print(f"==>> Original annot_source: {annot_source}")

#     # Search for the /Rotation entry in the source
#     if "/Rotation" in annot_source:
#         # Extract the existing rotation value
#         rotation_str = annot_source.split("/Rotation")[1].split()[0]
#         print(f"==>> Existing rotation_str: {rotation_str}")
        
#         # Replace the old rotation value with the new one
#         annot_source = annot_source.replace(f"/Rotation {rotation_str}", f"/Rotation {new_rotation}")
#         print(f"==>> Updated annot_source: {annot_source}")
#     else:
#         # If /Rotation is not found, add it with the new rotation value
#         insert_position = annot_source.find(">>")
#         annot_source = annot_source[:insert_position] + f"/Rotation {new_rotation} " + annot_source[insert_position:]
#         print(f"==>> Annot source with added rotation: {annot_source}")
    
#     # annot.rotation = new_rotation

#     # Update the annotation in the PDF with the modified source
#     doc.update_object(annot_xref, annot_source)


def get_rotated_width(annot):
    # Get the rotation angle in degrees
    rotation = annot.rotation  # This gives the rotation angle (if any)
    
    # Get the bounding box of the rotated square
    bbox = annot.rect
    
    # Calculate width and height using the bounding box coordinates
    width = bbox.width
    height = bbox.height
    
    # If rotation is zero, no need to adjust
    if rotation == 0:
        return width, height
    
    # Convert rotation angle to radians
    angle_rad = rotation * (fitz.pi / 180)
    
    # Calculate cosine and sine of the rotation angle
    cos_theta = fitz.cos(angle_rad)
    sin_theta = fitz.sin(angle_rad)
    
    # Apply inverse rotation matrix to get original width and height
    original_width = abs(cos_theta * width + sin_theta * height)
    original_height = abs(-sin_theta * width + cos_theta * height)

    return original_width, original_height


def rotate_annot(annot: Annot, ang):
    """
    Rotates the annotation by the specified angle by deleting it and creating a new one
    with the rotation transformation matrix applied.

    Parameters
    ----------
    annot : fitz.Annot
        The annotation to be rotated
    ang : int/float
        The angle the annotation is to be rotated by in degrees

    Returns
    -------
    None
    """
    # Get the original annotation properties
    rect = annot.rect
  
    # Rotate the rectangle
    bbox = sp_box(rect.x0, rect.y0, rect.x1, rect.y1)
    bbox = shapely_rotate(bbox, ang, origin='center')
    rotated_rect = fitz.Rect(bbox.bounds)

    # Apply a transformation matrix to rotate the appearance stream
    rotation_matrix = fitz.Matrix(1, 0, 0, 1, -rotated_rect.width / 2, -rotated_rect.height / 2)
    rotation_matrix = rotation_matrix * fitz.Matrix(-ang)
    rotation_matrix = rotation_matrix * fitz.Matrix(1, 0, 0, 1, rotated_rect.width / 2, rotated_rect.height / 2)

    # Apply the transformation to the annotation's appearance stream
    annot.set_rect(rotated_rect)
    annot.set_apn_matrix(rotation_matrix)
    
    annot.parent.parent
    current_angle = extract_rotation_from_source(annot, annot.parent.parent)
    annot.parent.parent.xref_set_key(annot.xref, 'Rotation', str(ang))



import math


def get_rotated_width(annot):
    """
    Calculate the original width and height of a rotated annotation.

    Parameters
    ----------
    annot : fitz.Annot
        The annotation whose dimensions need to be calculated.

    Returns
    -------
    original_width : float
        The original width of the annotation before rotation.
    original_height : float
        The original height of the annotation before rotation.
    """
    # Get the rotation angle in degrees
    rotation = annot.rotation  # This gives the rotation angle (if any)
    
    # Get the bounding box of the rotated annotation
    bbox = annot.rect
    
    # Calculate width and height using the bounding box coordinates
    width = bbox.width
    height = bbox.height
    
    # If rotation is zero, return the width and height as is
    if rotation == 0:
        return width, height
    
    # Convert rotation angle to radians
    angle_rad = math.radians(rotation)
    
    # Calculate cosine and sine of the rotation angle
    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)
    
    # Apply inverse rotation matrix to get the original width and height
    original_width = abs(width * cos_theta + height * sin_theta)
    original_height = abs(height * cos_theta + width * sin_theta)
    
    return original_width, original_height

# Constants for unit conversion
MM_TO_POINTS = 72 / 25.4  # 1 inch = 25.4 mm and 1 inch = 72 points

def mm_to_points(mm):
    """Convert millimeters to points."""
    return mm * MM_TO_POINTS

def create_shapely_polygon_from_rect(width_mm, height_mm, center_mm, rotation_deg, scale=100):

    """
    Create a Shapely polygon from rectangle dimensions in millimeters.
    
    Parameters:
    - width_mm: The width of the rectangle in millimeters.
    - height_mm: The height of the rectangle in millimeters.
    - center_mm: The center point of the rectangle in millimeters (Shapely Point).
    - rotation_deg: The rotation angle of the rectangle in degrees.
    - scale: The scale of the drawing (default is 1:100).
    
    Returns:
    - A Shapely Polygon representing the rotated rectangle.
    """
    # Convert dimensions to real-world size based on scale
    width_mm_scaled = width_mm / scale
    height_mm_scaled = height_mm / scale
    x_offset = center_mm.x/scale
    y_offset = center_mm.y/scale

    # Define the rectangle corners (centered at (0,0) before translation)
    half_width = width_mm_scaled / 2
    half_height = height_mm_scaled / 2
    rect_corners = [
        (-half_width, -half_height),
        (half_width, -half_height),
        (half_width, half_height),
        (-half_width, half_height)
    ]
    
    # Create the rectangle as a Shapely Polygon
    rect = Polygon(rect_corners)
    # Rotate and translate the rectangle to the desired center
    rect_rotated = shapely_rotate(rect, rotation_deg, origin=(0, 0))
    rect_translated = shapely_translate(rect_rotated, xoff=x_offset, yoff=y_offset)
    return rect_translated

def add_polygon_as_annotation(ga_page : GaPage, polygon: Polygon, update = True):

    """
    Convert a Shapely polygon to a PDF annotation and add it to a PDF page.
    
    Parameters:
    - doc: The PDF document object (fitz.Document).
    - page: The PDF page object (fitz.Page) where the annotation will be added.
    - polygon: The Shapely polygon object (shapely.geometry.Polygon).
    """

    # Get the page height in points directly from the page object
    page_height = ga_page.page.rect.height

    
    # Convert the Shapely polygon's coordinates to PDF points
    pdf_coords = []

    for x_mm, y_mm in polygon.exterior.coords:
        x_pts = mm_to_points(x_mm)
        print(f"==>> x_pts: {x_pts}")
        y_pts = page_height - mm_to_points(y_mm)  # Adjust for PDF coordinate system
        print(f"==>> y_pts: {y_pts}")
        pdf_coords.append((x_pts, y_pts))
    
    print(f"==>> pdf_coords: {pdf_coords}")

    # Add the polygon as a PDF annotation
    annot: Annot = ga_page.page.add_polygon_annot(pdf_coords)
    # Optionally, set properties of the annotation (like color, border width, etc.)

    annot.set_colors(stroke=(1, 0, 0))  # Red border color
    annot.set_border(width=1)  # Border width of 1 point

    annot.parent

    


    # if update:
    #     annot.update()


def get_positive_rotation(rotation):
    """
    Get the positive rotation angle from a negative or positive rotation angle.
    
    Parameters:
    - rotation: The rotation angle in degrees.
    
    Returns:
    - The positive rotation angle in degrees.
    """
    return (rotation + 360) % 360

def add_rect_as_annotation(ga_page: GaPage, width_mm, height_mm, center_mm, rotation_deg):
    """
    Add a rectangle as an annotation to a PDF page.

    Parameters:
    - ga_page: The PDF page object (GaPage) where the annotation will be added.
    - width_mm: The width of the rectangle in millimeters.
    - height_mm: The height of the rectangle in millimeters.
    - center_mm: The center point of the rectangle in millimeters (Shapely Point).
    - rotation_deg: The rotation angle of the rectangle in degrees.
    - scale: The scale of the drawing (default is 1:100).
    """
    scale = ga_page.page_properties.drawing_scale
    # Create a Shapely polygon from the rectangle dimensions
    x0 = center_mm.x - width_mm / 2
    y0 = center_mm.y - height_mm / 2
    x1 = center_mm.x + width_mm / 2
    y1 = center_mm.y + height_mm / 2
    rect = fitz.Rect(x0*MM_TO_POINTS/scale, y0*MM_TO_POINTS/scale, x1*MM_TO_POINTS/scale, y1*MM_TO_POINTS/scale)

    pos_rotation_deg = get_positive_rotation(rotation_deg)
    print(f"==>> rotation_deg: {rotation_deg}")
    
    annot: Annot = ga_page.page.add_rect_annot(rect)
    rotate_annot(annot, pos_rotation_deg)
    
    # annot.set_rotation(rotate = int(pos_rotation_deg))
    # extract_and_update_rotation(annot, ga_page.structure_model.doc, rotation_deg)

    # annot.set_colors(stroke=(1, 0, 0))  # Red border color
    # annot.set_border(width=1)  # Border width of 1 point
        
    
    
    
    
    # # Add the polygon as an annotation to the PDF page
    # annot.set_rect(annot.rect) # (location changes)

    # annot.set_flags() # (annotation behaviour)

    # annot.set_info() # (meta information, except changes to content)

    # annot.set_popup() # (create popup or change its rect)

    # annot.set_oc() # (add / remove reference to optional content information)

    # annot.set_open()

    # annot.update_file() #(file attachment changes)



@dataclass(kw_only=True)
class ColumnAnnot(GaAnnot):
    # annot: Annot = None
    # ga_page: GaPage = None
    annot_over: Annot = None
    annot_under: Annot = None
    # pdf_layer: str = None
    column_mesh: 'ColumnMesh' = None
    
    @property
    def width_annot(self):
        return abs(self.annot.rect.bl - self.annot.x0)
    
    def rect_from_column(self):
        center_x = self.column_mesh.location

    # @property
    # def length_annot(self):
    #     """Return the height (length) of the annotation in millimeters."""
    #     return get_annotation_content_height_in_mm(self.annot)

    @property
    def width_mm_from_annot(self):
        """Return the width of the annotation in millimeters."""
        return get_annotation_content_width_in_mm(self.annot)
    
    @property
    def length_mm_from_annot(self):
        return get_annotation_content_height_in_mm(self.annot)
    
    @property
    def location_mm_from_annot(self) -> Point:
        return get_annotation_center_in_mm_point(self.annot, self.ga_page.page.rect.height, scale=100)
    
    @property
    def rotation_from_annot(self):
        return extract_rotation_from_source(self.annot,self.ga_page.structure_model.doc)
    
    @property
    def width_mm(self):
        return self.column_mesh.width
        
    @property
    def length_mm(self):
        return self.column_mesh.length
    
    @classmethod
    def from_pdf_annot(cls, annot: Annot, ga_page: GaPage):
        this_inst = cls(annot = annot, ga_page = ga_page)
        return this_inst

    def export_to_pdf(self):
        pass
        # self.annot = rotate_and_recreate_annot_as_polygon(self.annot, 45)
        # rotate_annot(self.annot, 45) # for test
        # self.annot.update(rotate = -32) 
        # # new_annot.set_border(dashes=True)

    def update_width(self, width: int):
        self.annot.rect.width = 900

    def update_location(self, new_location: Point):
        self.annot.rect.x0 = new_location.x
        self.annot.rect.x1 = new_location.x + self.width_mm
        self.annot.rect.y0 = new_location.y
        self.annot.rect.y1 = new_location.y + self.length_mm
        # self.annot.update()

@dataclass(kw_only=True)
class ColumnMesh:
    model: 'StructureModel' = None
    floor_name: str = None
    name: str = None
    location: Point = None    
    toc: float = 0
    width: float = None
    length: float = None
    height: float = None
    angle: float = None
    below_slab: bool = True
    fixed_near: bool = True
    fixed_far: bool = False
    i_factor: float = None
    compressible: bool = False
    concrete: str = None
    polygon : MultiPolygon = None
    number: int = None
    floor_data: 'FloorData' = None
    level_over: 'FloorData' = None
    level_under: 'FloorData' = None
    column_annot: ColumnAnnot  = None

    @classmethod
    def from_ram_model(cls, ram_column: RamColumn):    
            print(f"==>> ram_column.location.x: {ram_column.location.x}")
            print(f"==>> ram_column.location.y: {ram_column.location.y}")
            print(f"==>> ram_column.b: {ram_column.b}")
            print(f"==>> ram_column.d: {ram_column.d}")
            this_inst = cls(
            name=ram_column.name,
            location = Point(ram_column.location.x*1000, ram_column.location.y*1000),
            toc=0,
            width = ram_column.b,
            length = ram_column.d,
            height=ram_column.height,
            angle = ram_column.angle,
            below_slab = ram_column.below_slab,
            compressible = ram_column.compressible,
            fixed_far=ram_column.fixed_far,
            fixed_near=ram_column.fixed_near,
            i_factor=ram_column.i_factor,
            concrete=ram_column.concrete,
            number=ram_column.number,
        )
            return this_inst

    def set_column_annot(self, ga_page: GaPage):
        self.polygon = create_shapely_polygon_from_rect(self.width, self.length, self.location, self.angle)
        print(f"==>> self.angle: {self.angle}")
        print(f"==>> self.location: {self.location}")
        print(f"==>> self.length: {self.length}")
        print(f"==>> self.width: {self.width}")

        # print(f"==>> self.polygon: {self.polygon}")
        # print(10000000000000000000000000000000000000000000000000000000000000000000000000001)
        # print('ga')
        # print(f"==>> ga_page: {ga_page}")
        # print(f"==>> self.ga_page: {self.ga_page}")


        self.column_annot = ColumnAnnot(annot = add_rect_as_annotation(ga_page, self.width, self.length, self.location, self.angle), ga_page = ga_page, column_mesh = self)
        # self.column_annot = ColumnAnnot(annot = add_polygon_as_annotation(ga_page,self.polygon), ga_page = ga_page, column_mesh = self)

        # self.column_annot = ColumnAnnot.from_pdf_annot(annot, ga_page)

    def column_annot_from_self(self):
        self.column_annot = ColumnAnnot.from_pdf_annot(self.column_annot.annot, self.ga_page)
    
    @classmethod
    def from_pdf_annot(cls, annot: Annot, ga_page: GaPage):
        _column_annot = ColumnAnnot.from_pdf_annot(annot,ga_page)
        _name = None
        _location = _column_annot.location_mm_from_annot
        _toc = 0
        _width = _column_annot.width_mm_from_annot
        _length = _column_annot.length_mm_from_annot
        _angle = _column_annot.rotation_from_annot
        _below_slab = True
        _compressible = False
        _concrete = None
        _fixed_near = True
        _fixed_far = False
        _i_factor = None
        _polygon = create_shapely_polygon_from_rect(_width, _length, _location, _angle)
        _number = None
        _floor_data = None
        _level_over = None
        _level_under = None
        _column_annot = _column_annot

        this_inst = cls(
            model = None,
            name = _name,
            location = _location,
            toc = _toc,
            width = _width,
            length = _length,
            angle = _angle,
            below_slab = _below_slab,
            compressible = _compressible,
            concrete = _concrete,
            fixed_near = _fixed_near,
            fixed_far = _fixed_far,
            i_factor = _i_factor,
            polygon = _polygon,
            number = _number,
            floor_data = _floor_data,
            level_over = _level_over,
            level_under = _level_under,
            column_annot = _column_annot
        )

        return this_inst
    
    @property
    def ram_column_name(self):
        return self.name

    @property
    def ram_location(self):
        return RAMPoint2D(self.location.x,self.location.y)
    
    def add_column_to_ram_model(self,model: RAMModel):
        
        structure_layer: StructureLayer = model.cad_manager.structure_layer

        ram_column_instance = structure_layer.add_column(self.ram_location)
        
        if self.name is not None:
            ram_column_instance.name = self.name

        if self.name is not None:
            ram_column_instance.name = self.name

        if self.width is not None:
            ram_column_instance.b = self.width

        if self.length is not None:
            ram_column_instance.d = self.length

        if self.height is not None:
            ram_column_instance.height = self.height

        if self.angle is not None:
            ram_column_instance.angle = self.angle

        if self.below_slab is not None:
            ram_column_instance.below_slab = self.below_slab

        if self.compressible is not None:
            ram_column_instance.compressible = self.compressible

        if self.fixed_far is not None:
            ram_column_instance.fixed_far = self.fixed_far

        if self.fixed_near is not None:
            ram_column_instance.fixed_near = self.fixed_near

        if self.i_factor is not None:
            ram_column_instance.i_factor = self.i_factor

        if self.concrete is not None:
            ram_column_instance.concrete = self.concrete

        if self.number is not None:
            ram_column_instance.number = self.number

        if self.length is not None:
            ram_column_instance.d = self.length

        if self.width is not None:
            ram_column_instance.b = self.width

@dataclass(kw_only=True)
class ColumnsData:
    ga_page: 'GaPage' = None
    columns: list[ColumnMesh] = field(default_factory=list)
    
    @classmethod
    def from_ga_page(cls,ga_page: GaPage):
        ga_page = ga_page
        return cls(ga_page = ga_page)

    @classmethod
    def from_ram_model(cls, model: RAMModel, over_T_under_F: bool):    

        # if over_T_under_F:
        #     ram_columns: list[RamColumn] = model.cad_manager.structure_layer.columns_above
        # else:
        ram_columns: list[RamColumn] = model.cad_manager.structure_layer.columns_below
        this_inst = cls()
        this_inst.columns = [ColumnMesh.from_ram_model(ram_column) for ram_column in ram_columns]
        # for coulmn in this_inst.columns:
        #     coulmn.floor_data = model.floor_data
        return this_inst
    
    def set_column_annot(self):
        for column in self.columns:
            column.set_column_annot(self.ga_page)

    def set_pdf_data(self, ga_page: GaPage):
        self.ga_page = ga_page
        for column in self.columns:
            column.column_annot_from_self()

    def export_to_pdf(self):
        for column in self.columns:
            column.column_annot.export_to_pdf()

    def columns_to_ram_model(self, model, replaceT_update_F = True):
        for column in self.columns:
            column.add_column_to_ram_model(model)


    # @classmethod
    # def from_annotation(self, annotation: Annot):
    #     location = Point(0.5*annotation.vertices[0][0] + 0.5*annotation.vertices[0][1],0.5*annotation.vertices[0][1] + 0.5*annotation.vertices[1][1])
    #     tag = "P180-1"
    #     return WallMesh(name = None,
    #                     tag = tag,
    #                     number = None,
    #                     thickness = None)

@dataclass(kw_only=True)
class ColumnsOverData(ColumnsData):
    pass

@dataclass(kw_only=True)
class ColumnsUnderData(ColumnsData):
    pass

