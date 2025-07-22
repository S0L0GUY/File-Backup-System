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
            logger.error(
                f"Failed to create temporary directory: {e}",
                exc_info=True
            )
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

        def handle_remove_readonly(func, path, exc):
            """Handle read-only files on Windows by changing permissions."""
            try:
                if os.path.exists(path):
                    logger.debug(f"Changing permissions for: {path}")
                    os.chmod(path, 0o777)
                    func(path)
            except Exception as e:
                logger.warning(f"Failed to handle readonly file {path}: {e}")

        try:
            temp_path = cls.get_temp_path()
            if temp_path is None:
                logger.debug("No temporary directory to clean up")
                return

            if not os.path.exists(temp_path):
                debug_msg = f"Temporary directory already removed: {temp_path}"
                logger.debug(debug_msg)
                cls.set_temp_path(None)
                return

            logger.debug(f"Removing temporary directory: {temp_path}")

            # Count files for logging
            file_count = 0
            try:
                for root, dirs, files in os.walk(temp_path):
                    file_count += len(files)
            except Exception:
                pass  # Don't fail cleanup if we can't count files

            if file_count > 0:
                logger.debug(f"Removing {file_count} temporary files...")

            shutil.rmtree(temp_path, onerror=handle_remove_readonly)
            cls.set_temp_path(None)

            logger.debug("Temporary directory cleanup completed successfully")

        except Exception as e:
            logger.error(
                f"Error during temporary directory cleanup: {e}", exc_info=True
            )
            # Don't raise exception for cleanup failures to avoid masking
            # the original error that caused cleanup to be called
