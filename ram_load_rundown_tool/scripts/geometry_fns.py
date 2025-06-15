import math
from ram_concept.line_segment_2D import LineSegment2D
from ram_concept.point_2D  import Point2D

def d2_line_to_length(line: LineSegment2D) -> float:
    return math.sqrt(
        (line.end_point.x - line.start_point.x) ** 2
        + (line.end_point.y - line.start_point.y) ** 2
    )

def centroid(line: LineSegment2D): 
    return Point2D((line.start_point.x + line.end_point.x),(line.start_point.x + line.end_point.x))

