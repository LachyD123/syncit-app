from tkinter import messagebox
from logging import Logger
from .default_settings import SettingsDict
from .error_handling import debug_exit

def get_template_has_llur(settings: SettingsDict) -> bool:
    return  bool(settings['TRANSFER_LL_UNREDUCIBLE'] and settings['LLUR_PLANS'])

def validate_number(value, min_value, max_value, is_int, show_message,var_name, logger: Logger = None):
    """
    Validates if the input value is a number and falls between the specified range.
    
    :param value: The value to be validated.
    :param min_value: The minimum valid value.
    :param max_value: The maximum valid value.
    :param is_int: If True, the value should be an integer.
    :return: A boolean indicating whether the value is valid or not.
    """
    try:
        if is_int:
            number = int(value)
        else:
            number = float(value)

        if min_value is not None and number < min_value:
            raise ValueError
        if max_value is not None and number > max_value:
            raise ValueError

        return True
    except ValueError:
        if not show_message:
            return  False
        
        if is_int and min_value is not None and max_value is not None:
            logger.error(f"{var_name} needs to be a valid interger between {min_value} and {max_value}.")
        elif is_int and min_value is not None:
            logger.error(f"{var_name} needs to be a valid interger greater than {min_value}.")
        elif is_int and max_value is not None:
            logger.error(f"{var_name} needs to be a valid interger less than {max_value}.")
        elif min_value is not None and max_value is not None:
            logger.error(f"{var_name} needs to be a valid number between {min_value} and {max_value}.")
        elif min_value is not None:
            logger.error(f"{var_name} needs to be a valid number greater than {min_value}.")
        elif max_value is not None:
            logger.error(f"{var_name} needs to be a valid number less than {max_value}.")        
        return False


def vaidate_max_min_column_stiffness(settings, logger: Logger = None):
    if settings["MAX_COLUMN_STIFFNESS_RATIO"] < settings["MIN_COLUMN_STIFFNESS_RATIO"]:
        logger.error(f'Max Column Stiffness Ratio: {settings["MAX_COLUMN_STIFFNESS_RATIO"]} is less than Min Column Stiffness Ratio: {settings["MIN_COLUMN_STIFFNESS_RATIO"]}')

    if settings["MAX_COLUMN_STIFFNESS_RATIO"] > 1:
        logger.error(f'Max Column Stiffness Ratio: {settings["MAX_COLUMN_STIFFNESS_RATIO"]} is greater than 1')
    
    if settings["MIN_COLUMN_STIFFNESS_RATIO"] < 0:
        logger.error(f'Min Column Stiffness Ratio: {settings["MIN_COLUMN_STIFFNESS_RATIO"]} is less than 0')

def validate_inputs(settings: SettingsDict, logger: Logger = None):

    is_error = False
    def check_is_error(value):
        if not value:
            is_error = True

    do_centroid = settings['DO_CENTROID_CALCS']
    do_transfer = settings['DO_LOAD_RUNDOWN']
    do_update_column_stiffness = settings['UPDATE_COLUMN_STIFNESS_CALCS']
    template_has_llur = get_template_has_llur(settings)

    if do_centroid or do_transfer:

        validate_number(settings['REINFORCED_CONCRETE_DENSITY'], 0, None, False, True,"Reinforced Concrete Density",logger=logger)
    
    if do_update_column_stiffness:
        check_is_error(validate_number(settings['MAX_COLUMN_STIFFNESS_RATIO'], 0, 1, False, True,"Max Column Stiffness Ratio",logger=logger))
        check_is_error(validate_number(settings['MIN_COLUMN_STIFFNESS_RATIO'], 0, 1, False, True,"Min Column Stiffness Ratio",logger=logger))
        check_is_error(vaidate_max_min_column_stiffness(settings, logger = logger))
        
    
    if do_centroid:
        check_is_error(validate_number(settings['DRAWING_SCALE_1_TO'], 0, None, True, True,"Drawing Scale",logger=logger))
        check_is_error(validate_number(settings['EQ_FACTORS_DL'], 0, None, False, True,"EQ LOAD COMBINATOIN FACTORS Dead Load",logger=logger))
        check_is_error(validate_number(settings['EQ_FACTORS_LLR'], 0, None, False, True,"EQ LOAD COMBINATOIN FACTORS Live Load Reducible",logger=logger))
        if template_has_llur:
            check_is_error(validate_number(settings['EQ_FACTORS_LLUR'], 0, None, False, True,"EQ LOAD COMBINATOIN FACTORS Live Load Unreducible",logger=logger))
        
    check_is_error(validate_number(settings['EXIT_CODE_AFTER_X_SECONDS'], 0, None, True, True,"EXIT_CODE_AFTER_X_SECONDS",logger=logger))
    check_is_error(validate_number(settings['MAX_ATTEMPTS_IF_ERRORS_RAISED'], 0, None, True, True,"MAX_ATTEMPTS_IF_ERRORS_RAISED",logger=logger))

    

    if is_error:
        debug_exit(settings, is_error=True, logger=logger)
