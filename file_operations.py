"""
File operations module for the backup system.
Handles temporary directory creation, file copying, and cleanup operations.
"""

from constants import FileLocations as FileDIR
from temp_manager import TempManager
from logging_config import get_logger
import os
import shutil


def ignore_patterns(dir, files):
    """
    Define patterns to ignore during copying.

    Args:
        dir: Directory being processed
        files: List of files in the directory

    Returns:
        list: Files to ignore during copy operation
    """
    logger = get_logger("file_operations.ignore_patterns")
    ignore_list = []
    temp_path = TempManager.get_temp_path()

    try:
        for file in files:
            should_ignore = False
            reason = ""

            if file == ".git":
                should_ignore = True
                reason = "git repository directory"
            elif file == "__pycache__":
                should_ignore = True
                reason = "Python cache directory"
            elif file == "desktop.ini":
                should_ignore = True
                reason = "Windows desktop configuration file"
            elif file.lower() == "thumbs.db":
                should_ignore = True
                reason = "Windows thumbnail cache file"
            elif temp_path is not None and os.path.abspath(
                os.path.join(dir, file)
            ) == os.path.abspath(temp_path):
                should_ignore = True
                reason = "temporary backup directory"

            if should_ignore:
                ignore_list.append(file)
                logger.debug(f"Ignoring {file}: {reason}")

        if ignore_list:
            logger.debug(f"Ignoring {len(ignore_list)} items in {dir}")

        return ignore_list

    except Exception as e:
        logger.warning(f"Error in ignore_patterns for {dir}: {e}")
        # Return empty list to continue with backup
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
        logger.error(
            f"Failed to create temporary directory: {e}",
            exc_info=True
        )
        raise


def populate_temp_hold() -> None:
    """
    Recursively copies all files and folders from the locations specified in
    FileDIR.ORIGINAL_FILE_LOCATIONS to the temporary hold directory.
    Preserves the directory structure relative to the source location.
    Excludes .git directories and other system/temporary files.

    Returns:
        None

    Raises:
        RuntimeError: If temporary directory is not initialized.
        OSError: If there are issues copying files or directories.
        PermissionError: If insufficient permissions to copy files.
    """
    logger = get_logger("file_operations.populate_temp_hold")

    try:
        temp_path = TempManager.get_temp_path()
        if temp_path is None:
            raise RuntimeError(
                "Temporary directory not initialized. "
                "Call create_temp_path() first."
            )

        logger.debug(f"Populating temporary directory: {temp_path}")

        total_locations = len(FileDIR.ORIGINAL_FILE_LOCATIONS)
        logger.info(f"Processing {total_locations} source location(s)")

        successful_copies = 0
        failed_copies = 0
        total_files_copied = 0
        total_dirs_copied = 0

        for i, file_location in enumerate(FileDIR.ORIGINAL_FILE_LOCATIONS, 1):
            logger.debug(
                f"Processing location {i}/{total_locations}: "
                f"{file_location}"
            )

            try:
                if not os.path.exists(file_location):
                    logger.warning(
                        f"Source location does not exist: " f"{file_location}"
                    )
                    failed_copies += 1
                    continue

                if os.path.isfile(file_location):
                    # Copy single file
                    try:
                        filename = os.path.basename(file_location)
                        destination = os.path.join(temp_path, filename)
                        shutil.copy2(file_location, destination)
                        total_files_copied += 1
                        successful_copies += 1
                        logger.debug(f"Copied file: {file_location}")

                    except (OSError, PermissionError, shutil.Error) as e:
                        error_msg = f"Failed to copy file {file_location}: {e}"
                        logger.error(error_msg)
                        failed_copies += 1

                elif os.path.isdir(file_location):
                    # Copy directory tree
                    try:
                        dest_dir = os.path.join(
                            temp_path, os.path.basename(file_location)
                        )

                        debug_msg = (
                            f"Copying directory tree: {file_location} "
                            f"-> {dest_dir}"
                        )
                        logger.debug(debug_msg)

                        # Count files before copying for progress tracking
                        file_count = sum(
                            len(files) for _, _, files in os.walk(
                                file_location
                            )
                        )
                        logger.debug(f"Directory contains ~{file_count} files")

                        shutil.copytree(
                            file_location,
                            dest_dir,
                            dirs_exist_ok=True,
                            ignore=ignore_patterns,
                        )

                        # Count what was actually copied
                        copied_files = sum(
                            len(files) for _, _, files in os.walk(dest_dir)
                        )
                        total_files_copied += copied_files
                        total_dirs_copied += 1
                        successful_copies += 1

                        info_msg = (
                            f"Copied directory: {file_location} "
                            f"({copied_files} files)"
                        )
                        logger.info(info_msg)

                    except (OSError, PermissionError, shutil.Error) as e:
                        error_msg = "Failed to copy directory "
                        f"{file_location}: {e}"
                        logger.error(error_msg)
                        failed_copies += 1

                else:
                    warn_msg = f"Skipping unknown file type: {file_location}"
                    logger.warning(warn_msg)
                    failed_copies += 1

            except Exception as e:
                error_msg = f"Unexpected error processing {file_location}: {e}"
                logger.error(error_msg, exc_info=True)
                failed_copies += 1

        # Log summary
        summary_msg = (
            f"Copy operation completed: "
            f"{successful_copies} successful, "
            f"{failed_copies} failed"
        )
        logger.info(summary_msg)
        if total_files_copied > 0:
            logger.info(f"Total files copied: {total_files_copied}")
        if total_dirs_copied > 0:
            logger.info(f"Total directories copied: {total_dirs_copied}")

        if successful_copies == 0 and total_locations > 0:
            raise RuntimeError("Failed to copy any source locations")

    except Exception as e:
        logger.error(
            f"Error populating temporary directory: {e}",
            exc_info=True
        )
        raise


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
        logger.error(
            f"Error during temporary files cleanup: {e}",
            exc_info=True
        )
        raise
