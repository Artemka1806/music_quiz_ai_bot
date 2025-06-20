import logging
import sys
from pathlib import Path

def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with consistent formatting and handlers.
    
    Args:
        name: The name of the logger (usually __name__ of the module)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # Avoid adding handlers multiple times
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(log_dir / "music_quiz_bot.log")
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatters and add it to the handlers
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(log_format)
        console_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
