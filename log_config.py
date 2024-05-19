import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO):
    """Set up a logger with specified name and log file.

    Args:
        name (str): Name of the logger.
        log_file (str): File path for the log file.
        level (optional): Logging level. Defaults to logging.INFO.
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024*5, backupCount=5)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)

    return logger

def set_library_log_level(library_name, level):
    """Set the logging level for a specified library.

    Args:
        library_name (str): The name of the library.
        level: The logging level to be set for the library.
    """
    logging.getLogger(library_name).setLevel(level)
    
# Configure logging
logger = setup_logger(__name__, 'prospectari_bot.log')
set_library_log_level('httpx', logging.WARNING)
