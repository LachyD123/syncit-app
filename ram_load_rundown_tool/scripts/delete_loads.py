

from ram_concept.model import Model
from .default_settings import SettingsDict
from ram_concept.force_loading_layer import ForceLoadingLayer


def delete_loadings(loading_layer:ForceLoadingLayer, area_loads:bool = True, line_loads: bool = True, point_loads: bool = True) -> None:

    if area_loads:
        for load in loading_layer.area_loads:
            load.delete()
    if line_loads:
        for load in loading_layer.line_loads:
            load.delete()
    if point_loads:
        for load in loading_layer.point_loads:
            load.delete()

def delete_transfer_loads(model: Model, settings: SettingsDict) -> None:
    """
    Deletes transfer loads from the model in the TRANSFER_DEAD and TRANSFER_LL_REDUCIBLE layers.
    
    Args:
    - model (Model): The RAM Concept model.
    - settings (dict): The dictionary containing all the settings.

    Returns:
    - None
    """
    delete_loadings(settings["TRANSFER_DEAD"])
    delete_loadings(settings["TRANSFER_LL_REDUCIBLE"])

