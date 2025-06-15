
from typing import TypedDict
from ram_concept.model import Model
from ram_concept.point_2D import Point2D
from ram_concept.result_layers import ReactionContext
from scripts.default_settings import SettingsDict
import math
from .column_reactions import get_column_reactions, ColumnReactions

from ram_concept.force_loading_layer import ForceLoadingLayer



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

def _add_column_loads(model: Model, column_data: list[ColumnReactions], loading_layer: ForceLoadingLayer) -> tuple[float, float]:

    """
    Adds loads to the columns in the model based on the provided data.
    
    Args:
    - model (Model): The RAM Concept model.
    - column_data (list[ColumnReactions]): Data for the column loads.
    - settings (dict): The dictionary containing all the settings.

    Returns:
    - tuple: Total dead load and total live load.
    """

    total_load = 0
    default_point_load = model.cad_manager.default_point_load
    default_point_load.elevation = 0

    for column_over in column_data:
        transfer_point_load = loading_layer.add_point_load(column_over["location"])
        transfer_point_load.zero_load_values()
        transfer_point_load.elevation = 0
        transfer_point_load.Fz = column_over["Fz"]
        total_load += column_over["Fz"]

    return total_load


def add_column_loads(model: Model, level_loads: dict[str, dict[str, dict[str, dict[str, float]]]],filename: str, lc_name: str, loading_layer: ForceLoadingLayer) -> tuple[float, float]:
    try:
        _add_column_loads(model,level_loads[filename]['COLUMNS'][lc_name],loading_layer)
    except KeyError:
        if not level_loads.get(filename):
            level_loads[filename] = dict()
        if not level_loads[filename].get('COLUMNS'):
            level_loads[filename]['COLUMNS'] = dict()
        _add_column_loads(model, level_loads, lc_name, loading_layer)
        raise Exception('Should not get here')
