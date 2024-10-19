import logging
from datetime import datetime

LOG_LEVEL_WIDTH = 8                 # Longest level ('CRITICAL') contains 8 chars
CLASS_METHOD_WIDTH = 65             # Width for class and method names for alignment
LOG_COLORS = {
    logging.DEBUG: "\033[94m",      # Blue
    logging.INFO: "\033[92m",       # Green
    logging.WARNING: "\033[93m",    # Yellow
    logging.ERROR: "\033[91m",      # Red
    logging.CRITICAL: "\033[95m",   # Magenta
    "RESET": "\033[0m"              # Reset to default
    }

class CustomFormatter(logging.Formatter):
    """Custom logging format that includes time, class, method, and colored output."""

    # Overwrite default format
    def format(self, record):
        log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_level = record.levelname.center(LOG_LEVEL_WIDTH)
        log_class_method = f"{record.module}.{record.funcName}".ljust(CLASS_METHOD_WIDTH)

        log_msg = f"{log_time} | {log_class_method} | {log_level} | {record.getMessage()}"

        # Apply color based on the log level using ANSI escape codes
        color = LOG_COLORS.get(record.levelno, LOG_COLORS["RESET"])
        reset = LOG_COLORS["RESET"]

        # Return the colored log message
        return f"{color}{log_msg}{reset}"

def get_logger(name) -> logging.Logger:
    # Create the logger
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.setLevel(logging.DEBUG)  # Set logger level to DEBUG to capture all types of logs

    # Create console handler and set level to the specified log level
    ch = logging.StreamHandler()

    # Add a handler with a custom formatter
    formatter = CustomFormatter()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
