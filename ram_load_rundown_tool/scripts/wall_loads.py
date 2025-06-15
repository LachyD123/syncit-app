
from typing import TypedDict
from ram_concept.model import Model
from ram_concept.point_2D import Point2D
from ram_concept.result_layers import ReactionContext
from .default_settings import SettingsDict
import math
from .wall_reactions import get_wall_group_reactions, get_wall_reactions, WallReactions
from ram_concept.force_loading_layer import ForceLoadingLayer

# def add_wall_loads(model: Model, wall_over_data: list[WallReactions], loading_layer: ForceLoadingLayer) -> tuple[float, float]:
#     """
#     Adds loads to the walls in the model based on the provided data.
    
#     Args:
#     - model (Model): The RAM Concept model.
#     - wall_over_data (list[WallReactions]): Data for the wall loads.
#     - settings (dict): The dictionary containing all the settings.

#     Returns:
#     - tuple: Total dead load and total live load.
    
# """
#     total_dead_load = 0
    
#     total_live_load = 0


#     default_line_load = model.cad_manager.default_line_load
#     default_line_load.elevation = 0

#     for wall_over in wall_over_data:


#         default_line_load.set_load_values(
#             0, 0, wall_over["Fz"], 0, 0
#         )  

#         dead_transfer.add_line_load(wall_over["location"])
#         total_dead_load += wall_over["all_dead_reaction_at_base_kN"]

#         default_line_load.set_load_values(
#             0, 0, wall_over["all_live_load_reaction_kN_per_m"], 0, 0
#         )  

#         live_transfer.add_line_load(wall_over["location"])

#         total_live_load += wall_over["all_live_load_reaction_kN"]

#     return total_dead_load, total_live_load


def add_wall_loads(model: Model, wall_over_data: list[WallReactions], loading_layer: ForceLoadingLayer) -> tuple[float, float]:
   
    """
    Adds loads to the walls in the model based on the provided data.
    
    Args:
    - model (Model): The RAM Concept model.
    - wall_over_data (list[WallReactions]): Data for the wall loads.
    - settings (dict): The dictionary containing all the settings.

    Returns:
    - tuple: Total dead load and total live load.
    
"""
    total_load = 0
    default_line_load = model.cad_manager.default_line_load
    default_line_load.elevation = 0

    for wall_over in wall_over_data:
        default_line_load.set_load_values(
            0, 0, wall_over["Fz_per_m"], 0, 0
        )  

        loading_layer.add_line_load(wall_over["location"])
        total_load += wall_over["Fz"]
 
    return total_load
