from .txt_settings import SETTINGS_FILENAME
from ram_concept.model import Model
from .default_settings import SettingsDict
from .error_handling import debug_exit
import logging
from logging import Logger
from .validate_inputs import get_template_has_llur

def validate_loading_types(model: Model, settings: SettingsDict,filename, logger:Logger = None) -> None:
    """
    Validates if the loading types in the model match the expected types.
    """
    
    if get_template_has_llur(settings):
        loading_names = [settings["TRANSFER_DEAD"], settings["TRANSFER_LL_REDUCIBLE"], settings["TRANSFER_LL_UNREDUCIBLE"]]
        loading_names.extend(settings["LLR_PLANS"])
        loading_names.extend(settings["LLUR_PLANS"])
    else:
        loading_names = [settings["TRANSFER_DEAD"], settings["TRANSFER_LL_REDUCIBLE"]]
        loading_names.extend(settings["LLR_PLANS"])
        loading_names.extend(settings["LLUR_PLANS"])

    template = [
        loading_layer.name.strip()
        for loading_layer in model.cad_manager.force_loading_layers
    ]



    loading_names = [x.strip() for x in loading_names]
    missing = [x for x in loading_names if x not in template]
    
    if missing:
        logger.error(f'For file {filename}; Loadings names {missing} are not found. Update the "LOADING NAMES" inputs to match the RAM C template loadings names.')
        debug_exit(settings, logger=logger)

def validate_load_comboinations_types(model: Model, settings: SettingsDict,filename, logger:Logger = None) -> None:
    """
    Validates if the load combination types in the model match the expected types.
    """

    load_combinations_names = [settings["ALL_DEAD_LC"]]
    
    template = [
        load_combination.name.strip()
        for load_combination in model.cad_manager.load_combo_layers
    ]

    missing = [x for x in load_combinations_names if x not in template]
    if missing:
        logger.error(f'For file {filename};  Load combination names {missing} are not found. Update the "LOAD COMBINATION NAMES" inputs to match the RAM C template loadings names.')
        debug_exit(settings, is_error=True, logger = logger)

