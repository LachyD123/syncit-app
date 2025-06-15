from typing import List, TypedDict
from ram_concept.model import Model
from ram_concept.point_2D import Point2D
from ram_concept.result_layers import ReactionContext
from scripts.default_settings import SettingsDict
import math
from ram_concept.force_loading_layer import ForceLoadingLayer
from ram_concept.load_combo_layer import LoadComboLayer

class ColumnReactions(TypedDict):
    location: Point2D
    all_dead_reaction_at_base: float
    all_live_load_reaction: float

class ColumnReactions(TypedDict):
    location: Point2D
    name: str
    Fr: float
    Fs: float
    Fz: float
    Mr: float
    Ms: float

def get_column_reactions(model: Model, loading_layer: ForceLoadingLayer|LoadComboLayer ,self_weight_concrete_density = 0) -> List[ColumnReactions]:
    
    """
    Fetches the reactions for each column in the model.
    
    Args:
    - model (Model): The RAM Concept model.
    - settings (dict): The dictionary containing all the settings.

    Returns:
    - List[ColumnReactions]: A list of reactions for each column.
    """
  
    reactions = {}

    for column_element in model.cad_manager.element_layer.column_elements_below:

        if self_weight_concrete_density == 0:
            column_self_weight = 0

        else:
            height = column_element.height
            width = column_element.b/1000
            depth = column_element.d/1000
        
            if width == 0:
                column_self_weight = self_weight_concrete_density * height * (math.pi * depth**2) / 4

            else:
                
                column_self_weight =  self_weight_concrete_density * height * width * depth
        
        column_reaction = loading_layer.column_reaction(
                column_element, ReactionContext.STANDARD
        )
        
        location = column_element.location
        reactions[(location.x,location.y)] = dict(
                location = Point2D(location.x, location.y),
                name = column_element.name,
                Fr = column_reaction.x,
                Fs = column_reaction.y,
                Fz = column_reaction.z + column_self_weight,
                Mr = column_reaction.rot_x,
                Ms = column_reaction.rot_y,
            )
        
    return reactions

    # if over_multi:

    #     for column_element in element_layer.column_elements_above:

    #         if not under_multi:
    #             column_self_weight = 0

    #         else:
    #             height = column_element.height
    #             width = column_element.b/1000
    #             depth = column_element.d/1000
            
    #             if width == 0:
    #                 column_self_weight = over_multi * height * REINFORCED_CONCRETE_DENSITY * (math.pi * depth**2) / 4

    #             else:
                    
    #                 column_self_weight =  over_multi * REINFORCED_CONCRETE_DENSITY * height * width * depth
    #         column_reaction = load_combination.column_reaction(
    #                 column_element, ReactionContext.STANDARD
    #             ).z

    #         location = column_element.location
    #         reactions.append(
    #             dict(
    #                 location = Point2D(location.x, location.y),
    #                 load = column_self_weight,
    #             )
    #         )
    # return reactions




def update_column_reactons(model: Model, loading_layer: ForceLoadingLayer|LoadComboLayer ,self_weight_concrete_density = 0) -> List[ColumnReactions]:
    

    """
    Fetches the reactions for each column in the model.
    
    Args:
    - model (Model): The RAM Concept model.
    - settings (dict): The dictionary containing all the settings.

    Returns:
    - List[ColumnReactions]: A list of reactions for each column.
    """
  
    reactions = {}

    for column_element in model.cad_manager.element_layer.column_elements_below:

        if self_weight_concrete_density == 0:
            column_self_weight = 0

        else:
            height = column_element.height
            width = column_element.b/1000
            depth = column_element.d/1000
        
            if width == 0:
                column_self_weight = self_weight_concrete_density * height * (math.pi * depth**2) / 4

            else:
                
                column_self_weight =  self_weight_concrete_density * height * width * depth
        
        column_reaction = loading_layer.column_reaction(
                column_element, ReactionContext.STANDARD
            ).z
        
        location = column_element.location
        
        reactions[(location.x,location.y)] = dict(
                location = Point2D(location.x, location.y),
                Fz = column_reaction + column_self_weight,
            )
        
    return reactions

