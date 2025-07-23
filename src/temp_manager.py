"""
Temporary file manager module for the backup system.
Handles creation and cleanup of temporary directories.
"""

import tempfile
import os
import shutil
from logging_config import get_logger


class TempManager:
    """
    Manages temporary directory creation and cleanup for the backup system.
    """

    _temp_dir = None

    @classmethod
    def get_temp_path(cls):
        """Get the current temporary directory path."""
        return cls._temp_dir

    @classmethod
    def set_temp_path(cls, path):
        """Set the temporary directory path."""
        cls._temp_dir = path

    @classmethod
    def create_temp_path(cls) -> str:
        """
        Creates a temporary directory using tempfile.mkdtemp().
        This creates a secure temporary directory with appropriate permissions
        and returns the path to the created directory.

        Returns:
            str: The path to the created temporary directory

        Raises:
            OSError: If unable to create temporary directory.
            PermissionError: If insufficient permissions to create directory.
        """
        logger = get_logger("temp_manager.create_temp_path")

        try:
            # Clean up any existing temporary files first
            logger.debug("Cleaning up any existing temporary files...")
            cls.cleanup_temp_files()

            logger.debug("Creating new temporary directory...")
            temp_dir = tempfile.mkdtemp(prefix="backup_temp_")

            cls.set_temp_path(temp_dir)
            logger.debug(f"Temporary directory created: {temp_dir}")

            return temp_dir

        except Exception as e:
            logger.error(f"Failed to create temporary directory: {e}", exc_info=True)
            raise

    @classmethod
    def cleanup_temp_files(cls) -> None:
        """
        Removes the temporary hold directory if it exists.
        This function checks if a temporary directory has been created
        and if so, deletes it along with all its contents.
        Handles permission errors that may occur on Windows systems.

        Returns:
            None

        Raises:
            OSError: If there are issues removing files or directories.
            PermissionError: If insufficient permissions to remove files.
        """
        logger = get_logger("temp_manager.cleanup_temp_files")

        temp_path = cls.get_temp_path()
        if temp_path is None:
            logger.debug("No temporary directory to clean up.")
            return

        if not os.path.exists(temp_path):
            logger.debug(f"Temporary directory already removed: {temp_path}")
            cls.set_temp_path(None)
            return

        logger.debug(f"Cleaning up temporary directory: {temp_path}")

        try:
            shutil.rmtree(temp_path, onerror=cls._handle_remove_readonly)
            logger.info(f"Successfully removed temporary directory: {temp_path}")
        except Exception as e:
            logger.error(
                f"Failed to remove temporary directory {temp_path}: {e}", exc_info=True
            )
            # Still set path to None to prevent reuse of a partially deleted directory
        finally:
            cls.set_temp_path(None)

    @staticmethod
    def _handle_remove_readonly(func, path, exc_info):
        """
        Error handler for shutil.rmtree.
        If a file is read-only, it changes its permissions and retries the removal.
        This is a common issue on Windows.
        """
        logger = get_logger("temp_manager._handle_remove_readonly")
        # Check if the error is a PermissionError
        if not isinstance(exc_info[1], PermissionError):
            # If not, re-raise the exception
            raise exc_info[1]

        logger.warning(
            f"Permission error removing {path}. Attempting to change permissions."
        )
        try:
            # Change the file permissions to be writable
            os.chmod(path, 0o777)
            # Retry the function that failed (e.g., os.remove)
            func(path)
            logger.debug(f"Successfully changed permissions and removed {path}")
        except Exception as e:
            logger.error(
                f"Failed to remove {path} even after changing permissions: {e}",
                exc_info=True,
            )
            # Re-raise the original exception if the retry fails
            raise exc_info[1]
