
from scripts.default_settings import SettingsDict
from scripts.default_settings import SETTINGS_DEFAULT
from scripts.txt_settings import read_settings, validate_settings
from scripts.error_handling import debug_exit
from scripts.validate_files import check_ram_files_are_present
from scripts.txt_settings import SETTINGS_FILENAME
from logging import Logger
import tkinter as tk
import threading

from scripts.validate_inputs import validate_inputs

from scripts.run_down_process import _run
from scripts.log_window_wrapper import log_window_wrapper

def run_click(settings: SettingsDict):
    threading.Thread(target = run(settings,log_folder_src = settings['ROOT_DIRECTORY'])).start()

def main_centroid_rundown_wrapped(settings: SettingsDict):
    threading.Thread(target = run(settings,log_folder_src = settings['ROOT_DIRECTORY'])).start()

@log_window_wrapper
def run(settings: SettingsDict,**kwargs):


    logger: Logger = kwargs.get('logger', None)
    
    validate_inputs(settings, logger = logger)
    validate_settings(settings, logger=logger)

    logger.info("Validating settings")

    check_ram_files_are_present(settings, logger = logger)

    progress = 0
    attempts = 0
    finish = False
    progress = _run(settings,progress=0, level_loads=None,centroid_data = None, attempts = None,logger = logger)


# @log_window_wrapper
# def main_centroid_rundown(settings: SettingsDict,**kwargs):

#     logger: Logger = kwargs.get('logger', None)

#     validate_settings(settings, logger=logger)

#     logger.info("Reading settings")
#     # settings = read_settings(SETTINGS_FILENAME, SETTINGS_DEFAULT, logger = logger)

#     logger.info("Validating settings")

#     check_ram_files_are_present(settings, logger = logger)

#     update_files_for_typical(settings, logger = logger)

#     progress = 0
#     attempts = 0
#     finish = False

#     progress = do_rundown_process(settings,progress=0, level_loads=None,centroid_data = None, attempts = None, do_transfer = False, do_centroid = True, logger = logger)
