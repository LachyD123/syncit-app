from .error_handling import debug_exit
import configparser
import time
from .default_settings import SettingsDict
import os
from .validate_files import check_ram_files_are_present, validate_at_filenmae_or_index, validate_length_of_files,validate_start_at_and_end_at
# Configure logging
import threading   
from .validate_inputs import validate_inputs 

SETTINGS_FILENAME = 'settings.txt'

import re
def extract_numbers_after_text(s, text):
    pattern = f"(?<={text})\d+"
    return [int(match) for match in re.findall(pattern, s)][-1]

SETTINGS_TEMPLATE = """
[INPUTS]
FILES = 
START_FROM_LEVEL_OR_INDEX = None
END_AT_LEVEL_OR_INDEX = None

[SETTINGS]
REINFORCED_CONCRETE_DENSITY = 25
WALL_GROUP = True
ATEMPT_RESTART_IF_ERROR = True
MAX_ATTEMPTS_IF_ERRORS_RAISED = 20
EXIT_CODE_AFTER_X_SECONDS = 10
GENERATE_MESH = True
DEBUG = False

[LOADINGS NAMES]
TRANSFER_DEAD = Transfer - Dead
TRANSFER_LL_REDUCIBLE = Transfer - LL reducible

TRANSFER_LL_NOT_REDUCIBLE = Transfer - LL unreducible

[LOAD COMBINATION NAMES]
ALL_DEAD_LC = All Dead LC
ALL_LIVE_LOADS = All live loads          
"""

import tkinter.messagebox as messagebox
from .error_handling import debug_exit
import configparser
import time
from .default_settings import SettingsDict
import os
from logging import Logger

# Configure logging

SETTINGS_FILENAME = 'settings.txt'

# import typing
# if typing.TYPE_CHECKING:
#     import logging

from scripts.log_window_wrapper import log_window_wrapper

def read_settings_from_txt(settings_filename: str, defaults: SettingsDict, logger: Logger = None) -> SettingsDict:

    # logger.info('READING SETTINGS')
    settings = defaults.copy()

    # logger.info('READING SETTINGS') 
    _root_directory = os.path.dirname(settings_filename) + '/'
    settings["ROOT_DIRECTORY"] = _root_directory
    if not os.path.isfile(settings_filename):
        logger.error('NO INPUTS.txt FILE')
        if False or settings["DEBUG"]:
            logger.info('using default as DEBUG = True')
            time.sleep(3)
        else:
            logger.error(f"""
Please create a {settings_filename} file in the same directory as this script with example template below:
{SETTINGS_TEMPLATE}""")
            debug_exit(settings, is_error=True, logger=logger)
        return tuple(settings.values())

    config = configparser.ConfigParser()
    config.read(settings_filename)
    settings["DEBUG"] = config.getboolean('SETTINGS', 'DEBUG', fallback=settings["DEBUG"])
    start_from_level_or_index = str(config.get('PROJECT_INPUTS', 'START_FROM_LEVEL_OR_INDEX', fallback=settings["START_FROM_LEVEL_OR_INDEX"]))
    end_at_level_or_index = str(config.get('PROJECT_INPUTS', 'END_AT_LEVEL_OR_INDEX', fallback=settings["END_AT_LEVEL_OR_INDEX"]))
    settings["START_FROM_LEVEL_OR_INDEX"] = start_from_level_or_index
    settings["END_AT_LEVEL_OR_INDEX"] = end_at_level_or_index
    settings["REINFORCED_CONCRETE_DENSITY"] = config.getfloat('SETTINGS', 'REINFORCED_CONCRETE_DENSITY', fallback=settings["REINFORCED_CONCRETE_DENSITY"])
    settings["MAX_ATTEMPTS_IF_ERRORS_RAISED"] = config.getint('SETTINGS', 'MAX_ATTEMPTS_IF_ERRORS_RAISED', fallback=settings["MAX_ATTEMPTS_IF_ERRORS_RAISED"])
    settings["EXIT_CODE_AFTER_X_SECONDS"] = config.getint('SETTINGS', 'EXIT_CODE_AFTER_X_SECONDS', fallback=settings["EXIT_CODE_AFTER_X_SECONDS"])
    # settings["WALL_GROUP"] = config.getboolean('SETTINGS', 'WALL_GROUP', fallback=settings['WALL_GROUP'])
    settings["DRAWING_SCALE_1_TO"] = config.getfloat('SETTINGS', 'DRAWING_SCALE_1_TO', fallback=settings["DRAWING_SCALE_1_TO"])
    settings["GENERATE_MESH"] = config.getboolean('SETTINGS', 'GENERATE_MESH', fallback=settings["GENERATE_MESH"])
    
    settings["MAX_COLUMN_STIFFNESS_RATIO"] = config.getfloat('SETTINGS', 'MAX_COLUMN_STIFFNESS_RATIO', fallback=settings["MAX_COLUMN_STIFFNESS_RATIO"])
    settings["MIN_COLUMN_STIFFNESS_RATIO"] = config.getfloat('SETTINGS', 'MIN_COLUMN_STIFFNESS_RATIO', fallback=settings["MIN_COLUMN_STIFFNESS_RATIO"])
    settings["ATEMPT_RESTART_IF_ERROR"] = config.getboolean('SETTINGS', 'ATEMPT_RESTART_IF_ERROR', fallback=settings["ATEMPT_RESTART_IF_ERROR"])
    settings["ALL_DEAD_LC"] = config.get('LOAD COMBINATION NAMES', 'ALL_DEAD_LC', fallback=settings["ALL_DEAD_LC"])
    settings["ALL_LIVE_LOADS_LC"] = config.get('LOAD COMBINATION NAMES', 'ALL_LIVE_LOADS_LC', fallback=settings["ALL_LIVE_LOADS_LC"])
    # settings["ALL_LIVE_LOADS"] = config.get('LOAD COMBINATION NAMES', 'ALL_LIVE_LOADS', fallback=settings["ALL_LIVE_LOADS"])
    settings["TRANSFER_DEAD"] = config.get('LOADINGS NAMES', 'TRANSFER_DEAD', fallback=settings["TRANSFER_DEAD"])
    settings["TRANSFER_LL_REDUCIBLE"] = config.get('LOADINGS NAMES', 'TRANSFER_LL_REDUCIBLE', fallback=settings["TRANSFER_LL_REDUCIBLE"])
    settings["TRANSFER_LL_UNREDUCIBLE"] = config.get('LOADINGS NAMES', 'TRANSFER_LL_UNREDUCIBLE', fallback=settings["TRANSFER_LL_REDUCIBLE"])
    # settings["LL_UNREDUCIBLE"] = config.get('LOADINGS NAMES', 'LL_UNREDUCIBLE', fallback=settings["LL_UNREDUCIBLE"])
    settings['LLR_PLANS'] = [item.strip() for item in config.get('LOADINGS NAMES', 'LLR_PLANS', fallback="").split(',')]
    settings['LLUR_PLANS'] = [item.strip() for item in config.get('LOADINGS NAMES', 'LLUR_PLANS', fallback="").split(',')]

    settings["TEMPLATE_HAS_LLUR"] = config.get('LOADINGS NAMES', 'TEMPLATE_HAS_LLUR', fallback=settings["TEMPLATE_HAS_LLUR"])
    settings["UPDATE_COLUMN_STIFNESS_CALCS"] = config.getboolean('RUN CALCS', 'UPDATE_COLUMN_STIFNESS_CALCS', fallback=settings["UPDATE_COLUMN_STIFNESS_CALCS"])
    settings["DO_LOAD_RUNDOWN"] = config.getboolean('RUN CALCS', 'DO_LOAD_RUNDOWN', fallback=settings["DO_LOAD_RUNDOWN"])

    settings["DO_CENTROID_CALCS"] = config.getboolean('RUN CALCS', 'DO_CENTROID_CALCS', fallback=settings["DO_CENTROID_CALCS"])
    settings["EQ_FACTORS_DL"] = config.getfloat('EQ COMBO FACTORS', 'EQ_FACTORS_DL', fallback=settings["EQ_FACTORS_DL"])
    settings["EQ_FACTORS_LLR"] = config.getfloat('EQ COMBO FACTORS', 'EQ_FACTORS_LLR', fallback=settings["EQ_FACTORS_LLR"])
    settings["EQ_FACTORS_LLUR"] = config.getfloat('EQ COMBO FACTORS', 'EQ_FACTORS_LLUR', fallback=settings["EQ_FACTORS_LLUR"])
    settings['CREATE_BACKUP_FILES'] = config.getboolean('SETTINGS', 'CREATE_BACKUP_FILES', fallback=settings["CREATE_BACKUP_FILES"])

    _files_in = config.get('PROJECT_INPUTS', 'FILES', fallback="")
    _typicals_in = config.get('PROJECT_INPUTS', 'TYPICAL', fallback="")
    # _filepaths_in = config.get('PROJECT_INPUTS', 'FILEPATHS', fallback="")

    _files: list[str] = [] if _files_in == "" else [item.strip() for item in _files_in.split(',')]
    _typicals: list[str] = [] if _typicals_in == "" else [item.strip() for item in _typicals_in.split(',')]
    # _filepaths: list[str] = [] if _filepaths_in == "" else [item.strip() for item in _filepaths_in.split(',')]

    FILES = {filename:{'filename': filename, 'typical': 1, 'filepath': _root_directory + '/' + filename} for filename in _files}
    

    # for _filepath in _filepaths:
    #     key, value = _filepath.split(':')
    #     FILES[key]['filepath'] = value

    for _typical in _typicals:
        key, value = _typical.split(':')
        FILES[key]['typical'] = value

    settings["FILES"] = list(FILES.values())


    if len(settings['LLUR_PLANS']) == 0:
        settings['TEMPLATE_HAS_LLUR'] = False

    return settings

@log_window_wrapper
def read_settings(settings_filename: str, defaults: SettingsDict, action = "LOAD FILE",  logger: Logger = None) -> SettingsDict:
    settings = read_settings_from_txt(settings_filename, defaults, logger = logger)
    # validate_length_of_files(settings, logger = logger)
    # validate_start_at_level_or_index(settings, logger = logger)
    # validate_end_at_level_or_index(settings, logger = logger)
    # validate_at_filenmae_or_index(settings, logger = logger)
    return settings

def validate_settings(settings, logger: Logger = None):
    validate_length_of_files(settings, logger = logger)
    validate_start_at_and_end_at(settings, logger = logger)

def validate_settings_wrapped(settings: SettingsDict):
    threading.Thread(target=main_validate_settings(settings, log_folder_src = settings['ROOT_DIRECTORY']) + "/logs").start()

@log_window_wrapper
def main_validate_settings(settings: SettingsDict,**kwargs):

    logger: Logger = kwargs.get('logger', None)

    
    validate_inputs(settings, logger = logger)

    validate_settings(settings, logger=logger)

def load_settings(settings_filename: str, defaults: SettingsDict,action = "LOAD FILE",  logger: Logger = None) -> SettingsDict:
    settings = read_settings_from_txt(settings_filename, defaults, logger = logger)
    # validate_length_of_files(settings, logger = logger)
    # validate_start_at_level_or_index(settings, logger = logger)
    # validate_end_at_level_or_index(settings, logger = logger)
    # validate_at_filenmae_or_index(settings, logger = logger)
    return settings
