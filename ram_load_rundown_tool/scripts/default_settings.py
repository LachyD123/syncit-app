
from typing import TypedDict

class SettingsDict(TypedDict):
    REINFORCED_CONCRETE_DENSITY: float
    DRAWING_SCALE_1_TO: float
    # WALL_GROUP: bool
    FILES: list[dict[str,str]]
    START_FROM_LEVEL_OR_INDEX: int
    END_AT_LEVEL_OR_INDEX: int
    MAX_ATTEMPTS_IF_ERRORS_RAISED: int
    EXIT_CODE_AFTER_X_SECONDS: int
    ATEMPT_RESTART_IF_ERROR: bool
    ALL_DEAD_LC: str
    ALL_LIVE_LOADS_LC: str
    TRANSFER_DEAD: str
    TRANSFER_LL_REDUCIBLE: str
    TEMPLATE_HAS_LLUR: bool
    LL_UNREDUCIBLE: str
    TRANSFER_LL_UNREDUCIBLE: str
    LLR_PLANS: list[str]
    LLUR_PLANS: list[str]
    GENERATE_MESH: bool
    DEBUG: bool
    ROOT_DIRECTORY: str
    DO_LOAD_RUNDOWN : bool
    DO_CENTROID_CALCS: bool
    UPDATE_COLUMN_STIFNESS_CALCS: bool
    MAX_COLUMN_STIFFNESS_RATIO: bool
    EQ_FACTORS_DL: bool
    EQ_FACTORS_LLR: bool
    EQ_FACTORS_LLUR: bool
    CREATE_BACKUP_FILES: bool

SETTINGS_DEFAULT: SettingsDict = {
    "REINFORCED_CONCRETE_DENSITY": 24.0,
    "FILES": ["LOR", "Roof", "L12", "L11", "L10", "L9", "L8", "L7", "L6", "L5", "L4", "L3", "L2", "L1", "Mezzanine", "GF"],
    "DRAWING_SCALE_1_TO": 100.0,
    "START_FROM_LEVEL_OR_INDEX": 0,
    "END_AT_LEVEL_OR_INDEX": -1,
    "MAX_ATTEMPTS_IF_ERRORS_RAISED": 5,
    "EXIT_CODE_AFTER_X_SECONDS": 10,
    "WALL_GROUP": True,
    "ATEMPT_RESTART_IF_ERROR": True,
    "ALL_DEAD_LC" : "All Dead LC",
    "ALL_LIVE_LOADS_LC": "All live loads",
    "TRANSFER_DEAD": "Transfer - Dead",
    "TRANSFER_LL_REDUCIBLE": "Transfer - LL reducible",
    "LLR_PLANS": ['Live (Reducible) Loading','Live (Parking) Loading','Live (Roof) Loading'],
    "LLUR_PLANS": ['Live (Unreducible) Loading','Live (Storage) Loading'],
    "TEMPLATE_HAS_LLUR": True,
    "LL_UNREDUCIBLE": "Live (Unreducible) Loading",
    "TRANSFER_LL_UNREDUCIBLE": "Transfer - LL unreducible",
    "GENERATE_MESH": True,
    "DEBUG": False,
    'ROOT_DIRECTORY': "",
    'DO_LOAD_RUNDOWN': True,
    'DO_CENTROID_CALCS': False,
    'UPDATE_COLUMN_STIFNESS_CALCS': False,
    'MAX_COLUMN_STIFFNESS_RATIO': 0.8,
    'MIN_COLUMN_STIFFNESS_RATIO': 0,
    'EQ_FACTORS_DL': 1.0,
    'EQ_FACTORS_LLR': 0.3,
    'EQ_FACTORS_LLUR': 0.6,
    'CREATE_BACKUP_FILES': False,
}
