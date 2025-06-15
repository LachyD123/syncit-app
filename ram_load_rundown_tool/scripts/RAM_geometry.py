from ram_concept.line_segment_2D import LineSegment2D
from ram_concept.point_2D import Point2D
import math


def wall_coordinates(centroid, angle, total_length) -> LineSegment2D:
    """Returns the start and end coordinates of a wall group."""
    
    # Calculate the delta x and delta y for half of the wall length along the angle.
    dx = (total_length / 2) * math.cos(math.radians(angle))
    dy = (total_length / 2) * math.sin(math.radians(angle))
    
    # Calculate the start and end coordinates.
    start = Point2D(centroid.x - dx, centroid.y - dy)
    end = Point2D(centroid.x + dx, centroid.y + dy)
    
    return LineSegment2D(start, end)