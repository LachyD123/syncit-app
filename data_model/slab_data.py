from dataclasses import dataclass, field
from shapely.geometry import MultiPolygon, Polygon
from typing import TypedDict, List, Tuple
from ram_concept.model import Model
from ram_concept.point_2D import Point2D
from ram_concept.slab_area import SlabArea
from ram_concept.polygon_2D import Polygon2D

def Ram_poly_to_shapely_poly(ram_poly: Polygon2D):
    return Polygon([(ram_point.x,ram_point.y) for ram_point in ram_poly.points])

from shapely import LineString, Point
from ..core_logic.pdf_processor import PdfPageProperties
from fitz import Annot, Rect
import fitz
import typing
if typing.TYPE_CHECKING:
    from .structure_model import StructureModel
    from .structure_model import GaPage

@dataclass(kw_only=True)
class SlabAnnot(Annot):
    annot: Annot = None
    ga_page: 'GaPage' = None
    annot_over: Annot = None
    annot_under: Annot = None
    pdf_layer: str = None

    def export_to_pdf(self):
        print(f"==>> self.annot: 2wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        # https://pymupdf.readthedocs.io/en/latest/page.html#Page.add_freetext_annot
        print(f"==>> self.annot.flags: {self.annot.flags}")
        print(f"==>> self.annot.rect: {self.annot.info}")
        # print(f'==>> self.annot.rect: {self.annot.info={"Rotation" : 15})')
        print(f"==>> self.annot.xref: {self.annot.rotation}")
        vertices = [(100, 100), (200, 100), (200, 200), (100, 200)]
        annot = self.ga_page.page.add_polygon_annot(vertices)
        annot.set_vertices(vertices)
        self.ga_page.structure_model.doc.xref_set_key(self.annot.xref, 'Rotation', '45')
        # self.annot.set_colors(stroke=(1,1, 0), fill=(0, 0, 0))
        # self.ga_page.page.add_rect_annot(self.annot.rect)
        self.annot.set_rotation(45)
        # new_annot.set_border(dashes=True)
        print(f"==>> self.annot.xref: {self.annot.rotation}")

    def update_width(self, width: int):
        self.annot.rect.width = 900

@dataclass(kw_only=True)
class SlabMeshArea:
    model: 'StructureModel' = None
    ga_page: 'GaPage' = None
    thickness: float = None
    toc: float = None
    priority: int = None
    polygon : Polygon = None
    slab_annot: SlabAnnot = None

    @classmethod
    def from_ram_slab_area(cls, ram_slab_area: SlabArea):
        ram_slab_area: SlabArea

        return cls(
        polygon = Ram_poly_to_shapely_poly(ram_slab_area.location),
        thickness = ram_slab_area.thickness,
        toc = ram_slab_area.toc,
        priority = ram_slab_area.priority,
        )

    def cut_from_other(self,other_mesh_area: 'SlabMeshArea'):
        if self.priority == other_mesh_area.priority and self.polygon.intersection(other_mesh_area):
            raise Exception('Priorities of the same overlap')

        elif self.priority > other_mesh_area:
            self.polygon = self.polygon.difference(other_mesh_area)

    @classmethod
    def from_pdf_annot(cls,ga_page: 'GaPage', annot: Annot):
        if not annot.type[1] == 'Polygon':
            raise NotImplementedError
        print(f"==>> ga_page.page_properties.annot_x_to_mm_factor: {ga_page.page_properties.annot_x_to_mm_factor}")
        this_inst = cls()
        scale_adjusted_points = [Point(vertice[0]*ga_page.page_properties.annot_x_to_mm_factor,vertice[1]*ga_page.page_properties.annot_x_to_mm_factor) for vertice in annot.vertices]
        this_inst.polygon = Polygon(scale_adjusted_points)
        wtk: Polygon = this_inst.polygon
        print(f"==>> wtk.wkb: {wtk.wkt}")
        print(f"==>> this_inst.polygon: {this_inst.polygon}")
        this_inst.thickness = 200 # 'TODO'
        this_inst.priority = 1 # 'TODO'
        this_inst.slab_annot = SlabAnnot(annot = annot, ga_page = ga_page)
        this_inst.update_annot_to_polly()
        return this_inst

    def update_annot_to_polly(self):
        print(f"==>> self.slab_annot.type: {self.slab_annot.annot.type}")
        # self.slab_annot.type= [point for point in self.polygon.exterior.coords]        

    def export_to_pdf(self):
        self.slab_annot.export_to_pdf()

@dataclass(kw_only=True)
class SlabMeshData:
    ga_page: 'GaPage' = None
    structure_model: 'StructureModel' = None
    pdf_input : list[SlabMeshArea] = field(default_factory=list)
    slab_meshed_areas: list[SlabMeshArea] = field(default_factory=list)
    all_slab_polygon: list[MultiPolygon] = field(default_factory=list)
    pdf_export_areas: list[SlabMeshArea] = field(default_factory=list)
    
    @classmethod
    def from_ga_page(cls,ga_page: 'GaPage'):
        ga_page = ga_page
        model = ga_page.structure_model
        return cls(ga_page = ga_page, structure_model = model)

    @property
    def slab_input_areas(self):
        return self._slab_input_areas[:]

    @classmethod
    def from_ram_model(cls,model: Model):
        ram_slab_areas = model.cad_manager.structure_layer.slab_areas
        this_inst = cls()
        this_inst.slab_meshed_areas  = [SlabMeshArea.from_ram_slab_area(ram_slab_area) for ram_slab_area in ram_slab_areas] 
        this_inst._slab_input_areas = [SlabMeshArea.from_ram_slab_area(ram_slab_area) for ram_slab_area in ram_slab_areas]
        return this_inst

    @staticmethod
    def sort_priorities(slab_mesh_area:SlabMeshArea):
        return slab_mesh_area.priority

    @property
    def get_by_priorities(self):
        return sorted(self.slab_mesh_areas,key = self.sort_priorities)
    
    def export_to_pdf(self):
        for slab_mesh_area in self.pdf_input:
            slab_mesh_area.export_to_pdf()
        pass

    # @dataclass(kw_only=True)
    # def get_slab_mesh_areas(model: Model ) -> dict[int, SlabMesh]:
    #     return SlabMeshAreas.from_ram_model(model)


