"""
File operations module for the backup system.
Handles temporary directory creation, file copying, and cleanup operations.
"""

from constants import FileLocations as FileDIR
from temp_manager import TempManager
from logging_config import get_logger
import os
import shutil

# A set of file/directory names to be ignored during backup.
# This provides a more efficient lookup than a list.
IGNORED_NAMES = {
    ".git",
    "__pycache__",
    "desktop.ini",
    "Thumbs.db",
    "thumbs.db",  # Both cases included for completeness
}


def ignore_patterns(directory, files):
    """
    Define patterns to ignore during copying.

    Args:
        directory (str): The directory being processed.
        files (list): A list of files in the directory.

    Returns:
        list: A list of files to ignore during the copy operation.
    """
    logger = get_logger("file_operations.ignore_patterns")
    ignore_list = []
    temp_path = TempManager.get_temp_path()

    try:
        for file in files:
            # Check against a predefined set of names
            if file in IGNORED_NAMES:
                ignore_list.append(file)
                logger.debug(f"Ignoring '{file}': Predefined ignore pattern.")
                continue

            # Ignore the temporary directory itself to prevent recursion
            if temp_path:
                file_abs_path = os.path.abspath(os.path.join(directory, file))
                if file_abs_path == os.path.abspath(temp_path):
                    ignore_list.append(file)
                    logger.debug(f"Ignoring '{file}': Is the temp directory.")

        if ignore_list:
            logger.debug(f"Ignoring {len(ignore_list)} items in {directory}")

        return ignore_list

    except Exception as e:
        logger.warning(f"Error in ignore_patterns for {directory}: {e}")
        return []


def create_temp_path() -> str:
    """
    Creates a temporary directory using TempManager.
    This creates a secure temporary directory with appropriate permissions
    and returns the path to the created directory.

    Returns:
        str: The path to the created temporary directory

    Raises:
        OSError: If unable to create temporary directory.
        PermissionError: If insufficient permissions to create directory.
    """
    logger = get_logger("file_operations.create_temp_path")

    try:
        logger.debug("Creating temporary directory...")
        temp_path = TempManager.create_temp_path()
        logger.debug(f"Temporary directory created: {temp_path}")
        return temp_path

    except Exception as e:
        logger.error(f"Failed to create temporary directory: {e}", exc_info=True)
        raise


def _copy_single_file(file_location, temp_path):
    """Copies a single file to the temporary directory."""
    logger = get_logger("file_operations._copy_single_file")
    try:
        filename = os.path.basename(file_location)
        destination = os.path.join(temp_path, filename)
        shutil.copy2(file_location, destination)
        logger.debug(f"Copied file: {file_location} to {destination}")
        return True
    except (OSError, PermissionError, shutil.Error) as e:
        logger.error(f"Failed to copy file {file_location}: {e}")
        return False


def _copy_directory_tree(file_location, temp_path):
    """Copies a directory tree to the temporary directory."""
    logger = get_logger("file_operations._copy_directory_tree")
    try:
        dest_dir = os.path.join(temp_path, os.path.basename(file_location))
        logger.debug(f"Copying directory tree: {file_location} -> {dest_dir}")

        shutil.copytree(
            file_location,
            dest_dir,
            dirs_exist_ok=True,
            ignore=ignore_patterns,
        )

        copied_files = sum(len(files) for _, _, files in os.walk(dest_dir))
        logger.info(f"Copied directory: {file_location} ({copied_files} files)")
        return True, copied_files
    except (OSError, PermissionError, shutil.Error) as e:
        logger.error(f"Failed to copy directory {file_location}: {e}")
        return False, 0


def populate_temp_hold() -> None:
    """
    Recursively copies all files and folders from the locations specified in
    FileDIR.ORIGINAL_FILE_LOCATIONS to the temporary hold directory.
    Preserves the directory structure relative to the source location.
    Excludes .git directories and other system/temporary files.

    Raises:
        RuntimeError: If temporary directory is not initialized or no sources are copied.
    """
    logger = get_logger("file_operations.populate_temp_hold")
    temp_path = TempManager.get_temp_path()
    if not temp_path:
        raise RuntimeError(
            "Temporary directory not initialized. Call create_temp_path() first."
        )

    logger.debug(f"Populating temporary directory: {temp_path}")
    stats = {"successful": 0, "failed": 0, "files": 0, "dirs": 0}

    for loc in FileDIR.ORIGINAL_FILE_LOCATIONS:
        if not os.path.exists(loc):
            logger.warning(f"Source location does not exist: {loc}")
            stats["failed"] += 1
            continue

        if os.path.isfile(loc):
            if _copy_single_file(loc, temp_path):
                stats["successful"] += 1
                stats["files"] += 1
            else:
                stats["failed"] += 1
        elif os.path.isdir(loc):
            success, file_count = _copy_directory_tree(loc, temp_path)
            if success:
                stats["successful"] += 1
                stats["dirs"] += 1
                stats["files"] += file_count
            else:
                stats["failed"] += 1
        else:
            logger.warning(f"Skipping unknown file type: {loc}")
            stats["failed"] += 1

    logger.info(
        f"Copy operation completed: {stats['successful']} successful, {stats['failed']} failed. "
        f"Copied {stats['files']} files and {stats['dirs']} directories."
    )

    if stats["successful"] == 0 and FileDIR.ORIGINAL_FILE_LOCATIONS:
        raise RuntimeError("Failed to copy any source locations.")


def cleanup_temp_files() -> None:
    """
    Removes the temporary hold directory if it exists.
    This function delegates to TempManager for cleanup operations.

    Returns:
        None

    Raises:
        OSError: If there are issues removing temporary files.
        PermissionError: If insufficient permissions to remove files.
    """
    logger = get_logger("file_operations.cleanup_temp_files")

    try:
        temp_path = TempManager.get_temp_path()
        if temp_path:
            logger.debug(f"Cleaning up temporary directory: {temp_path}")
        else:
            logger.debug("No temporary directory to clean up")

        TempManager.cleanup_temp_files()
        logger.debug("Temporary files cleanup completed successfully")

    except Exception as e:
        logger.error(f"Error during temporary files cleanup: {e}", exc_info=True)
        raise
