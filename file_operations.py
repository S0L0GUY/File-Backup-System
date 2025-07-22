"""
File operations module for the backup system.
Handles temporary directory creation, file copying, and cleanup operations.
"""

from constants import FileLocations as FileDIR
from temp_manager import TempManager
import os
import shutil


def ignore_patterns(dir, files):
    """Define patterns to ignore during copying."""
    ignore_list = []
    temp_path = TempManager.get_temp_path()

    for file in files:
        if file == '.git':
            ignore_list.append(file)
        elif file == '__pycache__':
            ignore_list.append(file)
        elif file == 'desktop.ini':
            ignore_list.append(file)
        elif file.lower() == 'thumbs.db':
            ignore_list.append(file)
        elif (temp_path is not None and
              os.path.abspath(os.path.join(dir, file)) ==
              os.path.abspath(temp_path)):
            ignore_list.append(file)

    return ignore_list


def create_temp_path() -> str:
    """
    Creates a temporary directory using TempManager.
    This creates a secure temporary directory with appropriate permissions
    and returns the path to the created directory.

    Returns:
        str: The path to the created temporary directory
    """
    return TempManager.create_temp_path()


def populate_temp_hold() -> None:
    """
    Recursively copies all files and folders from the locations specified in
    FileDIR.ORIGINAL_FILE_LOCATIONS to the temporary hold directory.
    Preserves the directory structure relative to the source location.
    Excludes .git directories and other system/temporary files.
    Returns:
        None
    """
    temp_path = TempManager.get_temp_path()
    if temp_path is None:
        raise RuntimeError(
            "Temporary directory not initialized. "
            "Call create_temp_path() first."
        )

    for file_location in FileDIR.ORIGINAL_FILE_LOCATIONS:
        if os.path.exists(file_location):
            if os.path.isfile(file_location):
                shutil.copy(file_location, temp_path)
            elif os.path.isdir(file_location):
                dest_dir = os.path.join(
                    temp_path,
                    os.path.basename(file_location)
                )
                shutil.copytree(
                    file_location,
                    dest_dir,
                    dirs_exist_ok=True,
                    ignore=ignore_patterns
                )
        else:
            print(f"Original file location does not exist: {file_location}")


def cleanup_temp_files() -> None:
    """
    Removes the temporary hold directory if it exists.
    This function delegates to TempManager for cleanup operations.
    Returns:
        None
    """
    TempManager.cleanup_temp_files()
