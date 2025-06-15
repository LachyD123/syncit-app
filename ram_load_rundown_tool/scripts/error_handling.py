from logging import Logger
from .default_settings import SettingsDict
import time
import threading

# # Create a new log file with a unique name for each run
# log_file = f"{'app'}_{int(time.time())}"
# logging.basicConfig(filename=f'{log_file}.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def debug_exit(settings: SettingsDict, is_error=False, logger: Logger = None):
    """
    Exits the script after waiting for a specified duration if DEBUG = False as assuming file is ran through CMD.
    Not sleeping the command prompt window will exit and not show the error message.
    """
    DEBUG = settings["DEBUG"]
    EXIT_CODE_AFTER_X_SECONDS = settings["EXIT_CODE_AFTER_X_SECONDS"]
    current_thread = threading.current_thread()

    if DEBUG:
        if is_error:
            logger.error(f'^ The error above has occurred; Script will close in {EXIT_CODE_AFTER_X_SECONDS} seconds')
            time.sleep(EXIT_CODE_AFTER_X_SECONDS)
        else:
            time.sleep(3)
        


            logger.info("Exiting script.")
            logger.info("[EXIT]")
            exit()
    else:
        logger.info("Exiting script.")
        logger.info("[EXIT]") # kills the thread
        exit()