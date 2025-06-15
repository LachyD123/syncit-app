
from ram_concept.point_2D import Point2D
from .column_reactions import ColumnReactions
from .wall_reactions import WallReactions
from .default_settings import SettingsDict 
from logging import Logger

class LoadCentroid(ColumnReactions):
    pass

from typing import TypedDict
import copy

def calculate_weighted_centroid(column_reactions: dict[tuple,ColumnReactions], wall_reactions: dict[tuple,WallReactions]) -> LoadCentroid:
    total_load = 0
    weighted_sum_x = 0
    weighted_sum_y = 0
        
    for reaction in column_reactions.values():
        load = reaction['Fz']

        x = reaction['location']._x
        y = reaction['location']._y
        
        total_load += load
        weighted_sum_x += load * x
        weighted_sum_y += load * y
    
    for reaction in wall_reactions.values():
        load = reaction['Fz']
        x = reaction['centroid']._x
        y = reaction['centroid']._y
        
        total_load += load
        weighted_sum_x += load * x
        weighted_sum_y += load * y

    if total_load == 0:
        print("Total load is zero, cannot calculate centroid")
        return None

    centroid_x = weighted_sum_x / total_load
    centroid_y = weighted_sum_y / total_load

    return LoadCentroid(Fz=total_load, location = Point2D(centroid_x,centroid_y))

def weighted_centroid_of_multiple(load_centroids: list[LoadCentroid], multipliers: list[float] = None) -> LoadCentroid:
    if not multipliers:
        multipliers = [1] * len(load_centroids)
    if len(load_centroids) != len(multipliers):
        raise ValueError("The number of load centroids must match the number of multipliers")

    total_combined_load = 0
    weighted_sum_x = 0
    weighted_sum_y = 0
    
    for lc, multiplier in zip(load_centroids, multipliers):
        if not lc:
            continue
        adjusted_load = lc['Fz'] * multiplier
        total_combined_load += adjusted_load
        weighted_sum_x += adjusted_load * lc['location'].x
        weighted_sum_y += adjusted_load * lc['location'].y

    if total_combined_load == 0:
        raise ValueError("Total combined load is zero, cannot calculate centroid")

    centroid_x = weighted_sum_x / total_combined_load
    centroid_y = weighted_sum_y / total_combined_load

    return LoadCentroid(
        location =  Point2D(centroid_x, centroid_y),
        Fz = total_combined_load
    )

def reduce_all_reactions_by_loading_reactions(all_reactions, loading_reactions):
    copy_of_all_reactions = copy.deepcopy(all_reactions)

    for location, reaction in loading_reactions.items():
        if location in copy_of_all_reactions:
            copy_of_all_reactions[location]['Fz'] -= reaction['Fz']
    return copy_of_all_reactions


class CentoidCacls(TypedDict):
    Accumulative_ALL_DL: LoadCentroid
    Accumulative_ALL_LLR: LoadCentroid
    Accumulative_ALL_LLUNR: LoadCentroid
    Floor_ALL_DL: LoadCentroid
    Floor_ALL_LLR: LoadCentroid
    Floor_ALL_LLUNR: LoadCentroid
    Accumulative_1DL_03LLR_06LLUR: LoadCentroid
    Floor_1DL_03LLR_06LLUR: LoadCentroid

def log_centroid_calcs(centroid_data: dict[str,LoadCentroid],filename = "", logger: Logger = None):
    for key, value in centroid_data.items():
        if value:
            logger.info(f"{filename} {key.upper().replace('_', ' ')} = {round(value['Fz'])}kN @ {round(value['location'].x,3)},{round(value['location'].y,3)}")

def get_centroids(level_loads, current_level_filename, is_unreducible_live_load, settings : SettingsDict, logger=None):
    
    centroid_data  = dict(
        Floor_1DL_03LLR_06LLUR = {},
        Floor_ALL_DL = {},
        Floor_ALL_LLR = {},
        Floor_ALL_LLUNR = {},
        Accumulative_1DL_03LLR_06LLUR = {},
        Accumulative_ALL_DL = {},
        Accumulative_ALL_LLR = {},
        Accumulative_ALL_LLUNR = {},
    )
    def round_if_int(number):
        if int(number) - float(number) == 0:
            number = int(number)
        else:
            number = round(number,1)
        return number

    EQ_DL_factor = round_if_int(settings['EQ_FACTORS_DL'])
    EQ_LLR_factor = round_if_int(settings['EQ_FACTORS_LLR'])
    EQ_LLUR_factor = round_if_int(settings['EQ_FACTORS_LLUR'])

    centroid_data['Accumulative_ALL_DL'] = calculate_weighted_centroid(level_loads[current_level_filename]['COLUMNS']['ALL_DEAD_LC'], level_loads[current_level_filename]['WALLS']['ALL_DEAD_LC'])

    this_all_dead_load_columns = reduce_all_reactions_by_loading_reactions(
        level_loads[current_level_filename]['COLUMNS']['ALL_DEAD_LC'],
        level_loads[current_level_filename]['COLUMNS']['TRANSFER_DEAD']
    )
    
    this_all_dead_load_walls = reduce_all_reactions_by_loading_reactions(
        level_loads[current_level_filename]['WALLS']['ALL_DEAD_LC'],
        level_loads[current_level_filename]['WALLS']['TRANSFER_DEAD']
    )

    centroid_data['Floor_ALL_DL'] = calculate_weighted_centroid(this_all_dead_load_columns, this_all_dead_load_walls)
    centroid_data['Floor_ALL_LL'] = calculate_weighted_centroid(level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS_FLOOR'], level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS_FLOOR'])
    centroid_data['Accumulative_ALL_LL'] = calculate_weighted_centroid(level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS'], level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS'])
    
    if is_unreducible_live_load:
        centroid_data['Accumulative_ALL_LLR'] = calculate_weighted_centroid(level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS_REDUCIBLE'], level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS_REDUCIBLE'])
        centroid_data['Accumulative_ALL_LLUR'] = calculate_weighted_centroid(level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS_UNREDUCIBLE'], level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS_UNREDUCIBLE'])
        centroid_data['Floor_ALL_LLR'] = calculate_weighted_centroid(level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'], level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'])
        centroid_data['Floor_ALL_LLUR'] = calculate_weighted_centroid(level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'], level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'])


        # this_all_llr_columns = reduce_all_reactions_by_loading_reactions(
        #     level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS_REDUCIBLE'],
        #     level_loads[current_level_filename]['COLUMNS']['TRANSFER_LL_REDUCIBLE']
        # )
    
        # this_all_llur_columns = reduce_all_reactions_by_loading_reactions(
        #     level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS_UNREDUCIBLE'],
        #     level_loads[current_level_filename]['COLUMNS']['TRANSFER_LL_UNREDUCIBLE']
        # )


        # this_all_llr_walls = reduce_all_reactions_by_loading_reactions(
        #     level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS_REDUCIBLE'],
        #     level_loads[current_level_filename]['WALLS']['TRANSFER_LL_REDUCIBLE']
        # )
    
        # this_all_llur_walls = reduce_all_reactions_by_loading_reactions(
        #     level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS_UNREDUCIBLE'],
        #     level_loads[current_level_filename]['WALLS']['TRANSFER_LL_UNREDUCIBLE']
        # )

        # centroid_data['Floor_ALL_LLR'] = calculate_weighted_centroid(this_all_llr_columns,this_all_llr_walls)
        # centroid_data['Floor_ALL_LLUR'] = calculate_weighted_centroid(this_all_llur_columns,this_all_llur_walls)
        
        _factors = f"{EQ_DL_factor}DL_{EQ_LLR_factor}LLR_{EQ_LLUR_factor}LLUR"
        _factors_list = [settings['EQ_FACTORS_DL'], settings['EQ_FACTORS_LLR'], settings['EQ_FACTORS_LLUR']]

        centroid_data[f'Acc_{_factors}'] = weighted_centroid_of_multiple([centroid_data['Accumulative_ALL_DL'], centroid_data['Accumulative_ALL_LLR'], centroid_data['Accumulative_ALL_LLUR']],_factors_list)
        centroid_data[f'Floor_{_factors}'] = weighted_centroid_of_multiple([centroid_data['Floor_ALL_DL'], centroid_data['Floor_ALL_LLR'], centroid_data['Floor_ALL_LLUNR']], _factors_list)
        
    else:

        centroid_data['Accumulative_ALL_LLR'] = calculate_weighted_centroid(level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS'], level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS'])
        centroid_data['Floor_ALL_LLR'] = calculate_weighted_centroid(level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'], level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'])

    #   # Using the new function for walls
    #     this_all_llr_columns= reduce_all_reactions_by_loading_reactions(
    #         level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS'],
    #         level_loads[current_level_filename]['COLUMNS']['TRANSFER_LL_REDUCIBLE']
    #     )

    #     # Using the new function for columns
    #     this_all_llr_walls = reduce_all_reactions_by_loading_reactions(
    #         level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS'],
    #         level_loads[current_level_filename]['WALLS']['TRANSFER_LL_REDUCIBLE']
    #     )

    #     centroid_data['Floor_ALL_LLR'] = calculate_weighted_centroid(this_all_llr_columns,this_all_llr_walls)

        _factors = f"{EQ_DL_factor}DL_{EQ_LLR_factor}LLR"
        _factors_list = [settings['EQ_FACTORS_DL'], settings['EQ_FACTORS_LLR']]
        centroid_data[f'Accumulative_{_factors}'] = weighted_centroid_of_multiple([centroid_data['Accumulative_ALL_DL'], centroid_data['Accumulative_ALL_LLR']], _factors_list)
        centroid_data[f'Floor_{_factors}'] = weighted_centroid_of_multiple([centroid_data['Floor_ALL_DL'], centroid_data['Floor_ALL_LLR']], _factors_list)

    return centroid_data


'''
    reduce_all_reactions_by_loading_reactions(
        level_loads[current_level_filename]['WALLS']['ALL_DEAD_LC'],
        level_loads[current_level_filename]['WALLS']['TRANSFER_DEAD']
    )
    
    reduce_all_reactions_by_loading_reactions(
        level_loads[current_level_filename]['COLUMNS']['ALL_DEAD_LC'],
        level_loads[current_level_filename]['COLUMNS']['TRANSFER_DEAD']
    )

    reduce_all_reactions_by_loading_reactions(
        level_loads[current_level_filename]['WALLS']['ALL_LIVE_LOADS'],
        level_loads[current_level_filename]['WALLS']['TRANSFER_LL_REDUCIBLE']
    )
    
    reduce_all_reactions_by_loading_reactions(
        level_loads[current_level_filename]['COLUMNS']['ALL_LIVE_LOADS'],
        level_loads[current_level_filename]['COLUMNS']['TRANSFER_LL_REDUCIBLE']
    )

# '''


#       # set_reactions(model,level_loads, current_level_filename, 'ALL_LIVE_LOADS',support_type, settings, logger=logger)

#         level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type][settings['LLR_PLANS'][0]])
#         for live_load_name in settings['LLR_PLANS'][1:]:
#             add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'], level_loads[current_level_filename][support_type][live_load_name], addT_subF = True)

#         level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'])
#         add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'],level_loads[current_level_filename][support_type]['TRANSFER_LL_REDUCIBLE'], addT_subF = True)

#         if template_has_llur:
#             set_reactions(model,level_loads, current_level_filename, 'TRANSFER_LL_UNREDUCIBLE',support_type, settings, logger=logger)

#             for live_load_name in settings['LLUR_PLANS']:
#                 set_reactions(model,level_loads, current_level_filename, live_load_name,support_type, settings, logger=logger)
#             # set_reactions(model,level_loads, current_level_filename, 'ALL_LIVE_LOADS',support_type, settings, logger=logger)

#             level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type][settings['LLUR_PLANS'][0]])
#             for live_load_name in settings['LLR_PLANS'][1:]:
#                 add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'], level_loads[current_level_filename][support_type][live_load_name], addT_subF = True)

#             level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'])
#             add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE'],level_loads[current_level_filename][support_type]['TRANSFER_LL_UNREDUCIBLE'], addT_subF = True)

#             level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'])
#             add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_FLOOR'],level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'], addT_subF = True)

#             level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'])
#             add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS'],level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE'], addT_subF = True)

#         else:
#             level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'])
#             level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'])
