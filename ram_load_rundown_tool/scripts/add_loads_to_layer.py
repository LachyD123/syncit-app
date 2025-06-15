from typing import TypedDict
from ram_concept.model import Model
from ram_concept.point_2D import Point2D
from ram_concept.result_layers import ReactionContext
from scripts.default_settings import SettingsDict
import math
from .column_reactions import get_column_reactions, ColumnReactions

from ram_concept.force_loading_layer import ForceLoadingLayer
import math 


# def add_column_loads(model: Model, column_data: list[ColumnReactions], loading_layer: ForceLoadingLayer) -> tuple[float, float]:
#     """
#     Adds loads to the columns in the model based on the provided data.
    
#     Args:
#     - model (Model): The RAM Concept model.
#     - column_data (list[ColumnReactions]): Data for the column loads.
#     - settings (dict): The dictionary containing all the settings.

#     Returns:
#     - tuple: Total dead load and total live load.
#     """
    
#     total_dead_load = 0
#     total_live_load = 0

#     dead_transfer = model.cad_manager.force_loading_layer(settings["TRANSFER_DEAD"])
#     live_transfer = model.cad_manager.force_loading_layer(
#         settings["TRANSFER_LL_REDUCIBLE"]
#     )

#     default_point_load = model.cad_manager.default_point_load
#     default_point_load.elevation = 0

#     for column_over in column_data:
#         dead_transfer_point_load = dead_transfer.add_point_load(column_over["location"])
#         dead_transfer_point_load.zero_load_values()
#         dead_transfer_point_load.elevation = 0
#         dead_transfer_point_load.Fz = column_over["all_dead_reaction_at_base"]

#         total_dead_load += column_over["all_dead_reaction_at_base"]

#         live_transfer_point_load = live_transfer.add_point_load(column_over["location"])
#         live_transfer_point_load.zero_load_values()
#         live_transfer_point_load.elevation = 0
#         live_transfer_point_load.Fz = column_over["all_live_load_reaction"]
#         total_live_load += column_over["all_live_load_reaction"]

#     return total_dead_load, total_live_load

def _add_column_loads(model: Model, column_data: dict[tuple,ColumnReactions], loading_layer: ForceLoadingLayer, load_types = None) -> tuple[float, float]:

    """
    Adds loads to the columns in the model based on the provided data.
    
    Args:
    - model (Model): The RAM Concept model.
    - column_data (list[ColumnReactions]): Data for the column loads.
    - settings (dict): The dictionary containing all the settings.

    Returns:
    - tuple: Total dead load and total live load.
    """

    if not load_types:
        load_types = [('Fz','Fz')]

    # load_types = [('Fz','Fz'),('Fr','Mx'),('Ms','My')]
    default_point_load = model.cad_manager.default_point_load
    default_point_load.elevation = 0
    load_types_add = [x[1] for x in load_types]
    for column_over in column_data.values():
        transfer_point_load = loading_layer.add_point_load(column_over["location"])
        transfer_point_load.zero_load_values()
        transfer_point_load.elevation = 0
        
        for value in load_types:
            load = column_over[value[0]]
            if value[0] not in ['Ms','Mr'] or load > 0:
                
                if load < 0:
                    load = 0
                
                elif load >= 10:
                    load = math.ceil(load)

                else:
                    load = math.ceil(load*10)/10
            else:
                if load <= 10:
                    load = math.floor(load)

                else:
                    load = math.floor(load*10)/10

            if value[1] == 'Fz' and load != 0:
                transfer_point_load.Fz = load
                continue
            if value[1] == 'Fx' and load != 0:
                transfer_point_load.Fx = float(load)
            if value[1] == 'Fy' and load != 0:
                transfer_point_load.Fy = float(load)
            if value[1] == 'Mx' and load != 0:
                transfer_point_load.Mx = float(load)
            if value[1] == 'My' and load != 0:
                transfer_point_load.My = float(load)

        # load = column_over["Fz"]
        # if load < 0:
        #     load = 0
        
        # elif load >= 10:
        #     load = math.ceil(load)

        # else:
        #     load = math.ceil(load*10)/10

        # transfer_point_load.Fz = load


def add_column_loads(model: Model, level_loads: dict[str, dict[str, dict[str, dict[str, float]]]],filename: str, lc_name: str, loading_layer: ForceLoadingLayer,load_types = None) -> tuple[float, float]:
    # try:
    _add_column_loads(model,level_loads[filename]['COLUMNS'][lc_name],loading_layer,load_types = load_types)
    # except KeyError:
    #     return
        # if not level_loads.get(filename):
        # if not level_loads[filename].get('COLUMNS'):
        #     level_loads[filename]['COLUMNS'] = dict()
        # _add_column_loads(model, level_loads, loading_layer)
        # raise Exception('Should not get here')




from .wall_reactions import get_wall_group_reactions, get_wall_reactions, WallReactions

def _add_wall_loads(model: Model, wall_over_data: dict[tuple,WallReactions], loading_layer: ForceLoadingLayer) -> tuple[float, float]:
   
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
    # length = mathwall_over['locatoin'].x - wall_over['locatoin'].y
    for location, wall_over in wall_over_data.items():
        length = math.sqrt((location[1][0] - location[0][0])**2 + (location[1][1] - location[0][1])**2) 
        load_per_length = wall_over["Fz"]/length
        if load_per_length < 0:
            load_per_length = 0
        
        elif load_per_length >= 10:
            load_per_length = math.ceil(load_per_length)

        else:
            load_per_length = math.ceil(load_per_length*10)/10

        default_line_load.set_load_values(
            0, 0, load_per_length, 0, 0
        )  

        loading_layer.add_line_load(wall_over["location"])


def add_wall_loads(model: Model, level_loads: dict[str, dict[str, dict[str, dict[str, float]]]],filename: str, lc_name: str, loading_layer: ForceLoadingLayer) -> tuple[float, float]:
    try:
        _add_wall_loads(model,level_loads[filename]['WALLS'][lc_name],loading_layer)
    except KeyError:
        if not level_loads.get(filename):
            level_loads[filename] = dict()
        if not level_loads[filename].get('WALLS'):
            level_loads[filename]['WALLS'] = dict()
        _add_wall_loads(model, level_loads[filename]['WALLS'][lc_name], loading_layer)
        return
    

def add_loads(model: Model, level_loads: dict[str, dict[str, dict[str, dict[str, float]]]],filename, lc_name: str,support_type: str, loading_layer: ForceLoadingLayer,load_types = None) -> tuple[float, float]:
    if support_type == 'COLUMNS':
        return add_column_loads(model,level_loads,filename,lc_name,loading_layer,load_types = load_types)
    elif support_type == 'WALLS':
        return add_wall_loads(model,level_loads,filename,lc_name,loading_layer)
    else:
        raise Exception('load_type must be COLUMNS or WALLS')
    

