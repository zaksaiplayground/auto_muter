import logging
import os
import sys

def setup_logger():
    """Configure the logger with file and line number information"""

    # Get user's local AppData folder
    local_appdata = os.getenv('LOCALAPPDATA')  # C:\Users\<User>\AppData\Local
    log_dir = os.path.join(local_appdata, "AutoMuter", "logs")

    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "AutoMuter.log")

    # Configure logging
    log_format = "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)

    return logger
