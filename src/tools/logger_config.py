import logging
import datetime
import os

if not os.path.isdir(os.path.join(os.getcwd(), "log")):
    # 'log' directory is not existed
    os.mkdir("log")
    print("log directory is created.")

# Set the default name of log file as 'year-month-day' format
log_file = datetime.datetime.now().strftime("%Y-%m-%d")

def setup_logger(log_file: str = f"{os.getcwd()}/log/{log_file}.log", debug_mode: bool = False):
    """
    Configures the logger to write logs to a file and optionally to the console.

    This function sets up a global logger with INFO level logging. It adds a file handler 
    to save logs to the specified log file and a console handler to display logs on the terminal.
    It prevents multiple handlers from being added if the logger is initialized multiple times.

    Args:
        log_file (str): The name of the log file where logs will be saved. 
                        Defaults to 'year-month-day.log'.
        debug_mode (bool): Toggle the debug mode.
                        In normal mode, log format is 'timestamp, logger name, log level, and message'.
                        In debug mode, return message shows 'file name'.
                        And log format is 'timestamp, file name, logger name, log level, and message'.

    Example:
        setup_logger('my_log.log')
    """
    logger = logging.getLogger()

    # Prevent adding multiple handlers if the logger is initialized multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        if debug_mode:
            # Debug mode
            # Log format: timestamp, file name, logger name, log level, and message
            formatter = logging.Formatter(
                "%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s"
            )   
        else:
            # Log format: timestamp, logger name, log level, and message
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        # File handler to write logs to the specified file
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler to output logs to the terminal (optional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)