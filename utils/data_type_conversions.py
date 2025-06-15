


from ..core_logic.pdf_processor import PdfPageProperties

from dataclasses import dataclass, field
from shapely.geometry import MultiPolygon, Polygon, Point, LineString

from ram_concept.point_2D import Point2D
from ram_concept.column import Column as Ram
import typing
from fitz import Annot, Rect
from ..core_logic.pdf_processor import GaPage

from ram_concept.model import Model as RamModel
from ram_concept.structure_layer import StructureLayer as RamStructureLayer
from ram_concept.point_2D import Point2D as RamPoint2D
from ram_concept.line_segment_2D import LineSegment2D as RamLineSegment2D
from ram_concept.polygon_2D import Polygon2D as RamPolygon2D
from ram_concept.slab_area import SlabAreaBehavior as RamSlabAreaBehavior
from ram_concept.beam import BeamBehavior as RamBeamBehavior
from ram_concept.column import Column as RamColumn

if typing.TYPE_CHECKING:
    from ..data_model.floor_data import FloorData
    from ..data_model.structure_model import StructureModel
    from ..data_model.column_data import ColumnMesh



class AnnottoShapely:
    @staticmethod
    def to_polygon(annot: Annot, page_properties: PdfPageProperties):

        return Polygon([Point(annot.vertices[0]*page_properties.annot_x_to_mm_factor,annot.vertices[1]*page_properties.annot_y_to_mm_factor) for vertices in annot.vertices])


class RamToShapely:
    @staticmethod
    def to_polygon(ram_polygon):
        return MultiPolygon(Polygon([(ram_point.x,ram_point.y) for ram_point in ram_polygon]))

class ShapelyToRam:
    @staticmethod
    def polygon(shapely_polygon: Polygon) -> RamPolygon2D:
        return RamPolygon2D([RamPoint2D(x=point[0], y=point[1]) for point in shapely_polygon.exterior.coords])
    
    @staticmethod
    def point(shapely_point: Point) -> RamPoint2D:
        return RamPoint2D(x=shapely_point.x, y=shapely_point.y)
    
    @staticmethod
    def line_segment(shapely_line: LineString) -> RamLineSegment2D:
        return RamLineSegment2D(start_point=ShapelyToRam.point(shapely_line.coords[0]), end_point=ShapelyToRam.point(shapely_line.coords[1]))
    

