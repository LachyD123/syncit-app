
import os
import configparser
from ram_concept.concept import Concept
from scripts.default_settings import SettingsDict
import math
from scripts.wall_loads import add_wall_loads
from scripts.wall_reactions import get_wall_group_reactions, get_wall_reactions, WallReactions
from scripts.delete_loads import delete_transfer_loads, delete_loadings
from scripts.default_settings import SETTINGS_DEFAULT
from scripts.txt_settings import read_settings
from scripts.column_loads import add_column_loads, _add_column_loads, ColumnReactions
from scripts.column_reactions import get_column_reactions, ColumnReactions
from scripts.error_handling import debug_exit
from scripts.validate_files import check_ram_files_are_present
from scripts.txt_settings import SETTINGS_FILENAME
from ram_concept.point_2D import Point2D
from ram_concept.line_segment_2D import LineSegment2D
import time
import logging
import tkinter as tk
import threading
import copy

DO_NEW = False

from scripts.validate_template import validate_loading_types, validate_load_comboinations_types
from scripts.add_loads_to_layer import add_loads 
# from ram_templae_file_data import level_column_data, level_wall_data
from typing import TypedDict
from ram_concept.model import Model
from logging import Logger
from .tolal_load_centroids import get_centroids, log_centroid_calcs
from .get_set_reactions import set_reactions, get_ultimate_column_reactions, update_column_stiffness

import pandas as pd
import os
from datetime import datetime
import shutil
from .validate_inputs import get_template_has_llur

def create_excel_from_centroid_data(centroid_data: dict, directory_path: str, darwing_scale: float):
    # Set the filepath for the template and the new file
    current_time = datetime.now().strftime('%Y_%m_%d@%H_%M_%S')

    new_filepath = os.path.join(directory_path, f'excel/{current_time}.xlsx')
    if not os.path.isdir(directory_path + '/excel'):
        os.mkdir(directory_path + '/excel')
    # Copy the template to the new file
    sheets_pandas: dict[str, pd.DataFrame] = dict()
    # For each inner key (sheet name) in centroid_data, edit the corresponding sheet in the new Excel file
    len_centroid_data = len(centroid_data)
    floor_height = 3    
    e = -1
    drawing_scale_multi = 100/darwing_scale # m to cm

    for sheet_name, data_dict in next(iter(centroid_data.values())).items():
        
        data = []
        for node_minus_1,(filename, inner_dict) in enumerate(centroid_data.items()):
            node = node_minus_1 + 1
            if inner_dict.get(sheet_name):
                
                row = {
                    'filename': filename,
                    'Node': node,
                    'SG X': round(inner_dict[sheet_name]['location'].x,3),
                    'SG Y': (len_centroid_data - node)*floor_height,
                    'SG Z': round(-inner_dict[sheet_name]['location'].y,3),
                    'Fz (kN)': round(inner_dict[sheet_name]['Fz']),
                    'PDF': f'{-round(drawing_scale_multi*inner_dict[sheet_name]["location"].x,3)},{-round(drawing_scale_multi*inner_dict[sheet_name]["location"].y,3)}',
                    'RAM': f'{round(inner_dict[sheet_name]["location"].x,3)},{round(inner_dict[sheet_name]["location"].y,3)}',
                }

                data.append(row)

        # Create a DataFrame from the data
        if data:

            sheets_pandas[sheet_name] = pd.DataFrame(data)

        if sheets_pandas:
            # Open the new Excel file and edit the specific sheet

            with pd.ExcelWriter(new_filepath, engine='xlsxwriter', mode='w') as writer:
                for sheet_name, df in sheets_pandas.items():
                    df: pd.DataFrame
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
    return new_filepath

def add_sub_reactions(all_reactions, loading_reactions, addT_subF = True):
    for location, reaction in loading_reactions.items():
        if location in all_reactions:
            if not addT_subF:
                all_reactions[location]['Fz'] -= reaction['Fz']
                all_reactions[location]['Fx'] -= reaction['Fx']
                all_reactions[location]['Fy'] -= reaction['Fy']
                all_reactions[location]['Mr'] -= reaction['Mr']
                all_reactions[location]['Ms'] -= reaction['Ms']

                if all_reactions[location].get('Fz_per_m') is not None:

                    all_reactions[location]['Fz_per_m'] -= reaction['Fz_per_m']   

            else:
                all_reactions[location]['Fz'] += reaction['Fz']
                if all_reactions[location].get('Fz_per_m') is not None:
                    all_reactions[location]['Fz_per_m'] += reaction['Fz_per_m']   

def open_excel(filepath: str):
    os.system(f'start excel "{filepath}"')

import typing
if typing.TYPE_CHECKING:
    import logging

def _run(settings: SettingsDict, progress=0, level_loads: dict[str, dict[str, dict[str, dict[str, ColumnReactions]]]]=None,centroid_data = None, attempts = None,logger: Logger = None):

    do_centroid = settings['DO_CENTROID_CALCS']
    do_transfer = settings['DO_LOAD_RUNDOWN']
    do_update_column_stiffness = settings['UPDATE_COLUMN_STIFNESS_CALCS']
    template_has_llur = get_template_has_llur(settings)

    genererate_mesh = settings['GENERATE_MESH']
    create_backup_files = settings['CREATE_BACKUP_FILES']

    if not do_centroid and not do_transfer and not do_update_column_stiffness:
        logger.error(f'Nothing to do please select instructions and try again, exiting script')

    def set_support_type_reactions(support_type):


        set_reactions(model,level_loads, current_level_filename, 'TRANSFER_DEAD',support_type, settings, logger=logger)

        set_reactions(model,level_loads, current_level_filename, 'TRANSFER_LL_REDUCIBLE',support_type, settings, logger=logger)
        
        set_reactions(model,level_loads, current_level_filename, 'ALL_DEAD_LC',support_type,settings,self_weight_concrete_density = settings['REINFORCED_CONCRETE_DENSITY'], logger=logger)

        if settings['ALL_LIVE_LOADS_LC']:
            set_reactions(model,level_loads, current_level_filename, 'ALL_LIVE_LOADS_LC',support_type,settings, logger=logger)

        for live_load_name in settings['LLR_PLANS']:
            set_reactions(model,level_loads, current_level_filename, live_load_name,support_type, settings, logger=logger)
        # set_reactions(model,level_loads, current_level_filename, 'ALL_LIVE_LOADS',support_type, settings, logger=logger)

        level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type][settings['LLR_PLANS'][0]])
        for live_load_name in settings['LLR_PLANS'][1:]:
            add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'], level_loads[current_level_filename][support_type][live_load_name], addT_subF = True)

        level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'])
        add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'],level_loads[current_level_filename][support_type]['TRANSFER_LL_REDUCIBLE'], addT_subF = True)

        if template_has_llur:
            set_reactions(model,level_loads, current_level_filename, 'TRANSFER_LL_UNREDUCIBLE',support_type, settings, logger=logger)

            for live_load_name in settings['LLUR_PLANS']:
                set_reactions(model,level_loads, current_level_filename, live_load_name,support_type, settings, logger=logger)
            # set_reactions(model,level_loads, current_level_filename, 'ALL_LIVE_LOADS',support_type, settings, logger=logger)

            level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type][settings['LLUR_PLANS'][0]])
            for live_load_name in settings['LLR_PLANS'][1:]:
                add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'], level_loads[current_level_filename][support_type][live_load_name], addT_subF = True)

            level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'])
            add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE'],level_loads[current_level_filename][support_type]['TRANSFER_LL_UNREDUCIBLE'], addT_subF = True)

            level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'])


            add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_FLOOR'],level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE_FLOOR'], addT_subF = True)
            level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'])

            level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'])
            add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS'],level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE'], addT_subF = True)

        else:
            level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_FLOOR'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE_FLOOR'])
            level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'])

        if support_type == 'COLUMNS' and DO_NEW:

            level_loads[current_level_filename][support_type]['SUMMARY'] = {}
            for location in level_loads[current_level_filename][support_type]['TRANSFER_DEAD'].keys():
                all_dead: ColumnReactions = level_loads[current_level_filename][support_type]['TRANSFER_DEAD'][location]
                all_live = level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS'][location]
                live_load_lc = level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_LC'][location]
                max_mr = max(1.2*all_dead['Mr'] + 1.5*live_load_lc['Mr'],1.35*all_dead['Mr'])
                max_ms = max(1.2*all_dead['Ms'] + 1.5*live_load_lc['Ms'],1.35*all_dead['Ms'])
                min_mr = min(1.2*all_dead['Mr'] + 1.5*live_load_lc['Mr'],1.35*all_dead['Mr'])
                min_ms = min(1.2*all_dead['Ms'] + 1.5*live_load_lc['Ms'],1.35*all_dead['Ms'])

                if abs(max_mr) > abs(min_mr):
                    mr = max_mr
                else:
                    mr = min_mr
                
                if abs(max_ms) > abs(min_ms):
                    ms = max_ms
                else:
                    ms = min_ms

                summary_reaction: ColumnReactions = {'name':'C?','location':all_dead['location'],'Fz':all_live['Fz'], 'Fr':live_load_lc['Fz'], 'Fs':all_dead['Fz'], 'Mr':mr, 'Ms':ms}

                level_loads[current_level_filename][support_type]['SUMMARY'][location] = summary_reaction

                # if all_dead.
                #     all_dead = 0

                # max_mr = 
            # set_reactions(model,level_loads, current_level_filename, 'TRANSFER_LL_UNREDUCIBLE',support_type, settings, logger=logger)
            # set_reactions(model,level_loads, current_level_filename, 'LL_UNREDUCIBLE',support_type, settings, logger=logger)

            # level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE'] = copy.deepcopy(level_loads[current_level_filename][support_type]['LL_UNREDUCIBLE'])
            # add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE'], level_loads[current_level_filename][support_type]['TRANSFER_LL_UNREDUCIBLE'], addT_subF = True)

            # level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'] = copy.deepcopy(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS'])
            # add_sub_reactions(level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_REDUCIBLE'], level_loads[current_level_filename][support_type]['ALL_LIVE_LOADS_UNREDUCIBLE'], addT_subF = False)
    
    def add_support_type_loads(support_type):
        add_loads(model, level_loads, previous_level_filename, 'ALL_DEAD_LC', support_type, model.cad_manager.force_loading_layer(settings["TRANSFER_DEAD"]))

        if template_has_llur:
            add_loads(model, level_loads, previous_level_filename, 'ALL_LIVE_LOADS_REDUCIBLE', support_type, model.cad_manager.force_loading_layer(settings["TRANSFER_LL_REDUCIBLE"]))
            add_loads(model, level_loads, previous_level_filename, 'ALL_LIVE_LOADS_UNREDUCIBLE', support_type, model.cad_manager.force_loading_layer(settings["TRANSFER_LL_UNREDUCIBLE"]))

        else:
            add_loads(model, level_loads, previous_level_filename, 'ALL_LIVE_LOADS', support_type, model.cad_manager.force_loading_layer(settings["TRANSFER_LL_REDUCIBLE"]))

        if support_type == 'COLUMNS' and DO_NEW:
            add_loads(model, level_loads, previous_level_filename, 'SUMMARY', support_type, model.cad_manager.force_loading_layer('_SUMMARY_TRANSFER_LOADS'),load_types = [('Fr','Fx'),('Fs','Fy'),('Fz','Fz'),('Fr','Mx'),('Ms','My')])

    # try:
    # The above code is a Python function that performs a series of tasks. Here is a breakdown of
    # what it does:
    if level_loads is None:
        level_loads = dict()

    if centroid_data is None:
        centroid_data = dict()
    
    if attempts is None:
        attempts = 1
    
    
    updataed_files = []
    for e,file_dict in enumerate(settings['FILES'][settings["START_FROM_LEVEL_OR_INDEX"]:settings["END_AT_LEVEL_OR_INDEX"]+1]):
        for _ in range(int(file_dict['typical'])):
            updataed_files.append(file_dict)
    settings['FILES'] = updataed_files


    FILES = settings['FILES']

    for e, file in enumerate(FILES[progress:]):
        concept = Concept.start_concept(headless=True)
        logger.info('')
        filename = file['filename']
        filepath = file['filepath']
        logger.info(f"Opening file {filename}")

        model = concept.open_file(filepath)

        if create_backup_files:
            path = os.path.dirname(filepath)
            if not os.path.isdir(path + '/backups'):
                os.mkdir(path + '/backups')    
            backup_name = f"/backups/{filename}.bak_{datetime.now().strftime('%Y_%m_%d@%H_%M_%S')}"
            logger.info(f"Creating backup file {backup_name}")
            model.save_file(f"{filepath}.bak_{datetime.now().strftime('%Y_%m_%d@%H_%M_%S')}")
        # model.calc_options.supports_above_in_self_dead = False

        if e == 0:
            previous_level_filename = file['filename']
        else:
            previous_level_filename = current_level_filename

        current_level_filename = file['filename']

        logger.info(f"Validating loading and load combinations types for {current_level_filename}")
        validate_loading_types(model, settings, filename, logger=logger)
        validate_load_comboinations_types(model, settings, filename, logger=logger)

        if e > 0 and do_transfer:
            logger.info(f"Deleting transfer loads from previous rundown if any for {current_level_filename}")
            delete_loadings(model.cad_manager.force_loading_layer(settings["TRANSFER_DEAD"]))
            delete_loadings(model.cad_manager.force_loading_layer(settings["TRANSFER_LL_REDUCIBLE"]))      
            if DO_NEW:
                delete_loadings(model.cad_manager.force_loading_layer("_SUMMARY_TRANSFER_LOADS")) 
            if template_has_llur:
                delete_loadings(model.cad_manager.force_loading_layer(settings["TRANSFER_LL_UNREDUCIBLE"]))

            logger.info(f"Adding column loads for {current_level_filename}")
            add_support_type_loads('COLUMNS')
            logger.info(f"Adding column loads for {current_level_filename}")
            add_support_type_loads('WALLS')
            
        if genererate_mesh:
            logger.info(f"Generating mesh for {current_level_filename}")
            model.generate_mesh()
        
        logger.info(f"Calculating model for {current_level_filename}")
        model.calc_all()
        level_loads[current_level_filename] = dict(COLUMNS=dict(),WALLS=dict())
        logger.info(f"Getting column reactions for {current_level_filename}")

        set_support_type_reactions('COLUMNS')

        if do_update_column_stiffness:

            ultimate_column_loads = get_ultimate_column_reactions(level_loads, current_level_filename,logger=logger)
            update_column_stiffness(model, ultimate_column_loads, settings)
            logger.info(f"Regenerating mesh for updated column stiffnesses")
            
            model.generate_mesh()
            logger.info(f"Getting revised column reactions for {current_level_filename}")

            set_support_type_reactions('COLUMNS')


        logger.info(f"Getting wall reactions for {current_level_filename}")
        set_support_type_reactions('WALLS')

        if do_centroid:
            centroid_loads = copy.deepcopy(level_loads)
            # Process loads using the new function
            centroid_data[filename] = get_centroids(centroid_loads, current_level_filename, template_has_llur, settings,  logger=logger)
            log_centroid_calcs(centroid_data[filename],logger = logger)

        logger.info(f"Getting wall reactions for {current_level_filename}")
        logger.info(f"Saving file {current_level_filename}")
        model.save_file(filepath)
        progress += 1
        logger.info(f"Closing File {current_level_filename}")
        model.close_model()
        logger.info(f"File {current_level_filename} closed")

    if do_centroid:
        logger.info(f"Creating Excel file for centroid data")
        excel_filepath = create_excel_from_centroid_data(centroid_data, settings['ROOT_DIRECTORY'], settings['DRAWING_SCALE_1_TO'])
        logger.info(f"Opening Excel file for centroid data")
        open_excel(excel_filepath)

    logger.info(f"SCRIPT COMPLETED SUCCESSFULLY")
    return 


    # except Exception as exc:

    #     if attempts >= settings['MAX_ATTEMPTS_IF_ERRORS_RAISED']:
    #         logger.error(f"RAM Concept spamming error: {exc}, max attempts reached of {settings['MAX_ATTEMPTS_IF_ERRORS_RAISED']}, exiting script")
    #         debug_exit(settings, is_error=True, logger = logger)

    #     logger.info(f"RAM Concept spamming error: {exc}, waiting 60 seconds and trying again")
    #     for t in range(int(60/5)):
    #         logger.info(f"Restarting in {int(60-t*5)} seconds")
    #         time.sleep(5)
    #     attempts += 1
    #     _run(settings, progress=progress, level_loads=level_loads,centroid_data = centroid_data, attempts=attempts, logger=logger)
    #     # debug_exit(settings, is_error=True, logger = logger)

