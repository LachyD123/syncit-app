
from .error_handling import debug_exit
from .default_settings import SettingsDict
import os
import re
from logging import Logger

import typing
if typing.TYPE_CHECKING:
    import logging

def extract_numbers_after_text(s, text):
    pattern = f"(?<={text})\d+"
    return [int(match) for match in re.findall(pattern, s)][-1]

def check_ram_files_are_present(settings: SettingsDict, logger: Logger = None):
    """Check if all files are present in the current directory."""
    filenames = [file_dict['filename'].split(".cpt")[0] for file_dict in settings['FILES']]
    filepaths = [file_dict['filepath'] for file_dict in settings['FILES']]
    # files = settings["FILES"]
    if not isinstance(filepaths, list):
        if isinstance(filepaths, str):
            filepaths = [filepaths]
        else:
            logger.error('Variable files is not of type list')
            debug_exit(settings, is_error=True)

    missing_files = []
    for file in filepaths:
        if not os.path.isfile(file):
            missing_files.append(file)

    if missing_files:
        logger.warning("The following files are missing:")
        for missing in missing_files:
            logger.warning(missing)
        logger.warning(f"Please open the update the !!!!!!!!!!!!!!!!! TODO file and update the list 'FILES' to include your files for the load rundown; Ensure the list is ordered from top RL to bottom RL.")
        debug_exit(settings, is_error=True)
    else:
        logger.info("All files are present.")

def validate_length_of_files(settings, logger: Logger = None):
    if not settings["FILES"]:
        logger.error(f'FILES: {settings["FILES"]} is empty. Please add files to the list of "Level Files"')
        debug_exit(settings, is_error=True, logger = logger)

    if len(settings["FILES"]) == 1 and settings["DO_LOAD_RUNDOWN"]:
        logger.warning(f'Only one file in Level Files: {settings["FILES"]}, 2 is needed for Load Rundown')
        # debug_exit(settings, is_error=True, logger = logger)

def validate_at_filenmae_or_index(settings,name = "'From Selected'", logger: Logger = None):
    if name == "'From Selected'":
        at_level_or_index = settings["START_FROM_LEVEL_OR_INDEX"]
    elif name == "'To Selected":
        at_level_or_index = settings["END_AT_LEVEL_OR_INDEX"]
    else:
        raise ValueError(f'Name: {name} is not valid. Must be "From Selected" or "To Selected"')
    filenames = [file_dict['filename'].split(".cpt")[0] for file_dict in settings['FILES']]

    if not at_level_or_index in filenames:
        if at_level_or_index.lower() == 'none':
            at_level_or_index = len(filenames)
        elif isinstance(at_level_or_index, str):
            if at_level_or_index.isdigit():
                at_level_or_index = int(at_level_or_index)
                if at_level_or_index > len(filenames):
                    logger.warning(f'{name} : {at_level_or_index} is greater than the length of FILES.')         
                    debug_exit(settings, is_error=True, logger = logger)
                elif int(at_level_or_index) < 0:
                    logger.warning(f'{name} : {at_level_or_index} is less than 0.')
                    debug_exit(settings, is_error=True, logger = logger)    
            else:
                logger.error(f'{name} : {at_level_or_index} is not in the list of files.')
                debug_exit(settings, is_error=True, logger=logger)
    else:
        at_level_or_index = filenames.index(at_level_or_index)
    return at_level_or_index
    # return end_at_level_or_index

def validate_start_at_and_end_at(settings, logger: Logger = None):
    logger.info('Validating Start and End')
    start_from_level_or_index = validate_at_filenmae_or_index(settings,name = "'From Selected'", logger = logger)
    end_at_level_or_index = validate_at_filenmae_or_index(settings,name = "'To Selected", logger = logger)
    if start_from_level_or_index > end_at_level_or_index:
        logger.warning(f'"From Selected": {start_from_level_or_index} is greater than "To Selected": {end_at_level_or_index}')
    settings["START_FROM_LEVEL_OR_INDEX"] = start_from_level_or_index
    settings["END_AT_LEVEL_OR_INDEX"] = end_at_level_or_index

    

