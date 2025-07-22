import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path


class BackupLogger:
    """Centralized logging configuration for the backup system."""

    _logger = None
    _log_file = None

    @classmethod
    def setup_logging(cls, log_level=logging.INFO, log_to_file=True,
                      log_directory="logs"):
        """
        Set up centralized logging for the backup system.

        Args:
            log_level: Logging level (default: INFO)
            log_to_file: Whether to log to file (default: True)
            log_directory: Directory for log files (default: "logs")

        Returns:
            logging.Logger: Configured logger instance
        """
        if cls._logger is not None:
            return cls._logger

        cls._logger = logging.getLogger('backup_system')
        cls._logger.setLevel(log_level)

        cls._logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)

        if log_to_file:
            try:
                log_path = Path(log_directory)
                log_path.mkdir(exist_ok=True)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                cls._log_file = log_path / f'backup_system_{timestamp}.log'

                file_handler = logging.handlers.RotatingFileHandler(
                    cls._log_file,
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5
                )
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                cls._logger.addHandler(file_handler)

                cls._logger.info(f"Logging to file: {cls._log_file}")

            except Exception as e:
                cls._logger.warning(f"Could not set up file logging: {e}")

        return cls._logger

    @classmethod
    def get_logger(cls, name=None):
        """
        Get a logger instance. If no main logger exists, creates one.

        Args:
            name: Logger name (default: backup_system)

        Returns:
            logging.Logger: Logger instance
        """
        if cls._logger is None:
            cls.setup_logging()

        if name:
            return logging.getLogger(f'backup_system.{name}')
        return cls._logger

    @classmethod
    def get_log_file_path(cls):
        """Get the current log file path."""
        return cls._log_file


def get_logger(name=None):
    """
    Convenience function to get a logger.

    Args:
        name: Module name for the logger

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = BackupLogger.get_logger(name)
    # Ensure logger is properly initialized
    if logger is None:
        logger = BackupLogger.setup_logging()
    return logger


def log_function_call(func):
    """
    Decorator to log function calls and handle exceptions.

    Args:
        func: Function to decorate

    Returns:
        Decorated function with logging
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        function_name = func.__name__

        try:
            logger.debug(f"Starting {function_name}")
            result = func(*args, **kwargs)
            logger.debug(f"Completed {function_name} successfully")
            return result

        except Exception as e:
            logger.error(f"Error in {function_name}: {str(e)}", exc_info=True)
            raise

    return wrapper


class LoggedOperation:
    """
    Context manager for logging operations with automatic success/failure
    logging.
    """

    def __init__(self, operation_name, logger=None):
        """
        Initialize logged operation.

        Args:
            operation_name: Name of the operation being performed
            logger: Logger instance (optional)
        """
        self.operation_name = operation_name
        self.logger = logger or get_logger()

    def __enter__(self):
        """Start the logged operation."""
        self.logger.info(f"Starting {self.operation_name}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the logged operation."""
        if exc_type is None:
            self.logger.info(f"Successfully completed {self.operation_name}")
        else:
            self.logger.error(
                f"Failed to complete {self.operation_name}: {exc_val}",
                exc_info=True
            )
        return False
