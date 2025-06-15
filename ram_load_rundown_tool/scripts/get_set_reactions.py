from typing import Union
from ram_concept.model import Model
from ram_concept.point_2D import Point2D
from ram_concept.line_segment_2D import LineSegment2D
from ram_concept.result_layers import ReactionContext
from .error_handling import debug_exit
from .column_reactions import ColumnReactions, get_column_reactions
from .wall_reactions import WallReactions, get_wall_group_reactions
from logging import Logger
import math
from .default_settings import SettingsDict


def set_reactions(model:Model,level_loads: dict[str, dict[str, dict[str, dict[str, float]]]],filename,lc_name: str,support_type_name: str,settings: SettingsDict,self_weight_concrete_density = 0, logger: Logger = None):
    _lc_name = settings.get(lc_name)

    if _lc_name:
        layer_name = _lc_name
        key = lc_name
    else:
        layer_name = lc_name
        key = lc_name
    load_layer = model.cad_manager.force_loading_layer(layer_name)
    if not load_layer:
        load_layer = model.cad_manager.load_combo_layer(layer_name)
    if not load_layer:
        logger.error(f"Load layer {layer_name} not found in Loading Layers or Load Combinations Layers")
        debug_exit(settings, is_error=True, logger=logger) 
    if support_type_name == 'COLUMNS':
        level_loads[filename]['COLUMNS'][key] = get_column_reactions(model, load_layer,self_weight_concrete_density = self_weight_concrete_density)
    elif support_type_name == 'WALLS':
        level_loads[filename]['WALLS'][key] = get_wall_group_reactions(model, load_layer, self_weight_concrete_density=self_weight_concrete_density)


# def set_reactions(model:Model,level_loads: dict[str, dict[str, dict[str, dict[str, float]]]],filename,: str,support_type_name: str,settings,self_weight_concrete_density = 0, logger: Logger = None):
#     load_layer = model.cad_manager.force_loading_layer(settings[lc_name])
#     if not load_layer:
#         load_layer = model.cad_manager.load_combo_layer(settings[lc_name])
#     if not load_layer:
#         logger.error(f"Load layer {settings[lc_name]} not found in Loading Layers or Load Combinations Layers")
#         debug_exit(settings, is_error=True, logger=logger) 
#     if support_type_name == 'COLUMNS':
#         level_loads[filename]['COLUMNS'][lc_name] = get_column_reactions(model, load_layer,self_weight_concrete_density = self_weight_concrete_density)
#     elif support_type_name == 'WALLS':

#         level_loads[filename]['WALLS'][lc_name] = get_wall_group_reactions(model, load_layer, self_weight_concrete_density=self_weight_concrete_density)


def get_ultimate_column_reactions(level_loads: dict[str, dict[str, dict[str, dict[str, float]]]],filename, logger: Logger = None):
    ultimate_columns = {}
    for dead_location, dead_value in level_loads[filename]['COLUMNS']['ALL_DEAD_LC'].items():

        all_live_value = level_loads[filename]['COLUMNS']['ALL_LIVE_LOADS'].get(dead_location)
        if not all_live_value:
            raise Exception(f"Location {dead_location} not found in ALL LIVE LOADS")

        ultimate_columns[dead_location] = {'location': dead_location, 'Fz':max((1.2*dead_value['Fz'] + 1.5*all_live_value['Fz'],1.35*dead_value["Fz"]))}

    return ultimate_columns

def update_column_stiffness(model: Model, ultimate_columns: dict[str, dict], settings: SettingsDict ) -> list[ColumnReactions]:

    max_column_stiffness_ratio = settings['MAX_COLUMN_STIFFNESS_RATIO']
    min_column_stiffness_ratio = settings['MIN_COLUMN_STIFFNESS_RATIO']
    
    for column_element in model.cad_manager.structure_layer.columns_below:
        location = column_element.location

        width = column_element.b
        depth = column_element.d
    
        if width == 0:
            Ag = (math.pi * depth**2) / 4

        else:
            
            Ag =  width * depth

        N_star =  ultimate_columns[(location.x,location.y)]['Fz']*1000 #kN to N

        f_c = column_element.concrete.fc_final
        
        check = N_star/(Ag*f_c)

        new_i_factor = 0.3
        
        if check >= 0.5:
            new_i_factor = 0.8
            
        elif check >= 0.2:
            new_i_factor = 0.5 + (check-0.2)
        
        elif check >= 0:
            new_i_factor = 0.3 + check*(0.2/0.3)

        else:
            new_i_factor = 0.3
            # raise Exception(f"Column {column_element.name} has negative axial load, logic should prevent this")
                
        new_i_factor = math.floor(new_i_factor*1000)/1000
        if new_i_factor > max_column_stiffness_ratio or new_i_factor > 1:
            new_i_factor = min(max_column_stiffness_ratio,1)
        if new_i_factor < min_column_stiffness_ratio or new_i_factor < 0:
            new_i_factor = max(min_column_stiffness_ratio,0)

        column_element.i_factor = new_i_factor



