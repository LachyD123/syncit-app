
from .default_settings import SettingsDict
from ram_concept.model import Model
from ram_concept.line_segment_2D import LineSegment2D, Point2D
from typing import TypedDict, List
from ram_concept.result_layers import ReactionContext
from .RAM_geometry import wall_coordinates
import math
from .geometry_fns import d2_line_to_length, centroid
from ram_concept.force_loading_layer import ForceLoadingLayer
from ram_concept.load_combo_layer import LoadComboLayer


class WallReactions(TypedDict):
    location: LineSegment2D
    centroid: Point2D
    Fz: float
    Fz_per_m: float



def get_wall_group_reactions(model: Model, settings: SettingsDict) -> List[WallReactions]:
    """
    Fetches the reactions for each wall group in the model.
    
    Args:
    - model (Model): The RAM Concept model.
    - settings (dict): The dictionary containing all the settings.

    Returns:
    - List[WallReactions]: A list of reactions for each wall group.
    """

    REINFORCED_CONCRETE_DENSITY = settings["REINFORCED_CONCRETE_DENSITY"]
    ALL_DEAD_LC = settings["ALL_DEAD_LC"]
    ALL_LIVE_LOADS = settings["ALL_LIVE_LOADS"]

    cad_manager = model.cad_manager
    element_layer = cad_manager.element_layer
    all_dead_load_combo = cad_manager.load_combo_layer(ALL_DEAD_LC)
    all_live_load_combo = cad_manager.load_combo_layer(ALL_LIVE_LOADS)
    wall_reactions: list[WallReactions] = []

    for wall_element in element_layer.wall_element_groups_below:
        
        all_dead_reaction = all_dead_load_combo.wall_group_reaction(
            wall_element, ReactionContext.STANDARD
        ).z
        
        all_live_reaction = all_live_load_combo.wall_group_reaction(
            wall_element, ReactionContext.STANDARD
        ).z
        
        height = 3
        total_area = wall_element.total_area*10**-6
        total_length = wall_element.total_length
        centroid = wall_element.centroid
        reaction_anlge = wall_element.reaction_angle
        location = wall_coordinates(centroid, reaction_anlge, total_length)

        wall_self_weight = REINFORCED_CONCRETE_DENSITY * height * total_area
        all_dead_reaction_at_base_kN = max(all_dead_reaction,0) + wall_self_weight

        wall_reactions.append(
            dict(
                location=location,
                Fz=all_dead_reaction_at_base_kN,
                Fz_per_m=all_dead_reaction_at_base_kN
                / total_length,
            )
        )

    return wall_reactions

def get_wall_reactions(model: Model, settings: SettingsDict) -> List[WallReactions]:
    """
    Fetches the reactions for each wall in the model.
    
    Args:
    - model (Model): The RAM Concept model.
    - settings (dict): The dictionary containing all the settings.

    Returns:
    - List[WallReactions]: A list of reactions for each wall.
    """

    REINFORCED_CONCRETE_DENSITY = settings["REINFORCED_CONCRETE_DENSITY"]
    ALL_DEAD_LC = settings["ALL_DEAD_LC"]
    ALL_LIVE_LOADS = settings["ALL_LIVE_LOADS"]

    cad_manager = model.cad_manager
    element_layer = cad_manager.element_layer
    all_dead_load_combo = cad_manager.load_combo_layer(ALL_DEAD_LC)
    all_live_load_combo = cad_manager.load_combo_layer(ALL_LIVE_LOADS)
    wall_reactions: list[WallReactions] = []

    for wall_element in element_layer.wall_elements_below:
        all_dead_reaction = all_dead_load_combo.wall_group_reaction(
            wall_element, ReactionContext.STANDARD
        ).z
        all_live_reaction = all_live_load_combo.wall_group_reaction(
            wall_element, ReactionContext.STANDARD
        ).z
        height = wall_element.height
        thickness = wall_element.thickness/1000

        length = d2_line_to_length(wall_element.location)
        wall_self_weight = REINFORCED_CONCRETE_DENSITY * height * length * thickness
        all_dead_reaction_at_base_kN = max(all_dead_reaction,0) + wall_self_weight
        all_live_load_reaction_kN = math.ceil(all_live_reaction)

        wall_reactions.append(
            dict(
                location=wall_element.location,
                all_dead_reaction_at_base_kN=all_dead_reaction_at_base_kN,
                all_live_load_reaction_kN=all_live_reaction,
                all_dead_reaction_at_base_kN_per_m=all_dead_reaction_at_base_kN
                / length,
                all_live_load_reaction_kN_per_m=all_live_load_reaction_kN / length,
            )
        )

    return wall_reactions

# def get_load_combo_reaction(model: Model, load_combo_name: str, under_multi = 0, over_multi = 0, concrete_density = 25) -> List[ColumnReactions]:



#     REINFORCED_CONCRETE_DENSITY = concrete_density
  
#     cad_manager = model.cad_manager
#     element_layer = cad_manager.element_layer
#     load_combination = cad_manager.load_combo_layer(load_combo_name)
#     wall_reactions: list[WallReactions] = []

#     for wall_element in element_layer.wall_elements_below:

#         reaction = load_combination.wall_group_reaction(
#             wall_element, ReactionContext.STANDARD
#         ).z

#         height = wall_element.height
#         thickness = wall_element.thickness/1000

#         length = d2_line_to_length(wall_element.location)

#         wall_self_weight = REINFORCED_CONCRETE_DENSITY * height * length * thickness
#         all_dead_reaction_at_base_kN = reaction + wall_self_weight
#         all_live_load_reaction_kN = math.ceil(all_live_reaction)


#         wall_reactions.append(
#             dict(
#                 location=centroid(wall_element.location),
#                 load = reaction + (wall_self_weight * under_multi) + (over_multi * ),
#                 all_live_load_reaction_kN=all_live_reaction,
#                 all_dead_reaction_at_base_kN_per_m=all_dead_reaction_at_base_kN
#                 / length,
#                 all_live_load_reaction_kN_per_m=all_live_load_reaction_kN / length,
#             )
#         )

#     return wall_reactions

#     return wall_reactions

def get_wall_group_reactions(model: Model,loading_layer: ForceLoadingLayer|LoadComboLayer,self_weight_concrete_density = 0) -> List[WallReactions]:
    """
    Fetches the reactions for each wall group in the model.
    
    Args:
    - model (Model): The RAM Concept model.
    - settings (dict): The dictionary containing all the settings.

    Returns:
    - List[WallReactions]: A list of reactions for each wall group.
    """

    cad_manager = model.cad_manager
    element_layer = cad_manager.element_layer

    wall_reactions: dict[tuple,WallReactions] = dict()

    for wall_element in element_layer.wall_element_groups_below:
        
        Fz = loading_layer.wall_group_reaction(
            wall_element, ReactionContext.STANDARD
        ).z
        
        total_length = wall_element.total_length
        height = 3
        total_area = wall_element.total_area*10**-6
        centroid = wall_element.centroid
        reaction_anlge = wall_element.reaction_angle
        location = wall_coordinates(centroid, reaction_anlge, total_length)
        wall_self_weight = self_weight_concrete_density * height * total_area

        Fz += wall_self_weight

        wall_reactions[((location._start_point.x,location._start_point.y),(location._end_point.x,location._end_point.y))] = dict(
                location=location,
                centroid=centroid,
                Fz  = Fz,
            )
        
    
    return wall_reactions