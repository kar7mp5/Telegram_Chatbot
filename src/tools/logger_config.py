import logging

def setup_logger(log_file='app.log'):
    """
    Configures the logger to write logs to a file and optionally to the console.

    This function sets up a global logger with INFO level logging. It adds a file handler 
    to save logs to the specified log file and a console handler to display logs on the terminal.
    It prevents multiple handlers from being added if the logger is initialized multiple times.

    Args:
        log_file (str): The name of the log file where logs will be saved. 
                        Defaults to 'app.log'.

    Example:
        setup_logger('my_log.log')
    """
    logger = logging.getLogger()

    # Prevent adding multiple handlers if the logger is initialized multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Log format: timestamp, logger name, log level, and message
        formatter = logging.Formatter(
            "%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s"
        )

        # File handler to write logs to the specified file
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler to output logs to the terminal (optional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)