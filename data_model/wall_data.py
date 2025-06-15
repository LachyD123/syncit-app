from dataclasses import dataclass, field
from shapely.geometry import MultiPolygon, Polygon, Point
from typing import TypedDict, List, Tuple
from ram_concept.model import Model
from ram_concept.point_2D import Point2D
from ram_concept.line_segment_2D import LineSegment2D
from ram_concept.slab_area import SlabArea
from ram_concept.column import Column
from ram_concept.wall import Wall
from ram_concept.polygon_2D import Polygon2D
import typing
from fitz import Annot, Page, Rect
from shapely import LineString
from ..core_logic.pdf_processor import PdfPageProperties, GaPage

if typing.TYPE_CHECKING:
    from .floor_data import FloorData

def RAM_poly_to_shapely_poly(ram_poly):
    return MultiPolygon(Polygon([(ram_point.x,ram_point.y) for ram_point in ram_poly]))

@dataclass(kw_only=True)
class WallAnnot(Rect):
    annot: Annot = None
    ga_page: GaPage = None
    annot_over: Annot = None
    annot_under: Annot = None
    pdf_layer: str = None

    def export_to_pdf(self):
        self.annot.rect.x0 = self.annot.rect.x0 - 1000
        self.annot.rect.x1 = self.annot.rect.x1 + 1000
        self.annot.rect.y0 = self.annot.rect.y0 - 1000
        self.annot.rect.y1 = self.annot.rect.y1 + 1000  
        self.annot.update()

    def update_width(self, width: int):
        self.annot.rect.width = width/self.page.page_properties.scale_1_to

@dataclass(kw_only=True)
class WallMesh:
    name: str = None
    tag : str = None
    number: int = None
    thickness: float = None
    location: LineSegment2D = None
    height: float = None
    toc: float = None
    below_slab: bool = True
    compressable: bool = False
    concrete: str = None
    level_over: 'FloorData' = None
    level_under: 'FloorData' = None
    polygon : MultiPolygon = None
    compressable: bool = False
    shear_wall: bool = False
    fixed_near: bool = True
    fixed_far: bool = False
    below_slab: bool = True
    wall_annot: WallAnnot = None
        
    def export_to_pdf(self):
        self.wall_annot.export_to_pdf()

    @classmethod
    def from_ram_model(cls, ram_wall: Wall):
        return cls(
            name = None,
            tag = None,
            number=ram_wall.number,
            thickness= ram_wall.thickness,
            location= ram_wall.location,
            height= ram_wall.height,
            toc= 0,
            below_slab=ram_wall.below_slab,
            compressable=ram_wall.compressible,
            concrete=ram_wall.concrete,
            fixed_far=ram_wall.fixed_far,
            fixed_near=ram_wall.fixed_near,
            # llr_max_reduction=ram_wall.llr_max_reduction,
            shear_wall = ram_wall.shear_wall
        )

    @staticmethod
    def is_wall_annot(annot: Annot):
        if annot.type == 'Line':
             return True
        return False
    
    @classmethod
    def from_pdf_annot(cls, wall_annot: WallAnnot):
        scale_adjusted_points = [Point(vertice[0]*wall_annot.ga_page.page_properties.annot_x_to_mm_factor,vertice[0]*wall_annot.ga_page.page_properties.annot_y_to_mm_factor) for vertice in wall_annot.annot.vertices]
        location = LineString(scale_adjusted_points)
        tag = "P180-1"
        return WallMesh(name = None,
                        tag = tag,
                        number = None,
                        thickness = None,
                        location = location,
                        wall_annot= wall_annot
                        )
    
    def to_pdf(sell):
        pass
    
@dataclass(kw_only=True)
class WallMeshOver(WallMesh):
    pass

@dataclass(kw_only=True)
class WallMeshUnder(WallMesh):
    pass

@dataclass(kw_only=True)
class WallsData:
    ga_page: 'GaPage' = None
    walls: list[WallMesh] = field(default_factory=list)

    @classmethod
    def from_ga_page(cls,ga_page: GaPage):
        ga_page = ga_page
        return cls(ga_page = ga_page)

    @classmethod
    def from_ram_model(cls, model: Model, over_T_under_F: bool):    
            if over_T_under_F:
                walls = model.cad_manager.structure_layer.walls_above
            else:
                walls = model.cad_manager.structure_layer.walls_below
            
            return [WallMesh.from_ram_model(wall) for wall in walls]
    
    def to_pdf(self,page:Page, page_properties: PdfPageProperties):
        pass
    
        # for wall in self.pdf_input:
        #     wall.annot.

    def export_to_pdf(self):
        for wall in self.walls:
            wall.export_to_pdf()

@dataclass(kw_only=True)
class WallsOverData(WallsData):
    pass

@dataclass(kw_only=True)
class WallsUnderData(WallsData):
    pass

