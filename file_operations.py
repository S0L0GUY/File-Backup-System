"""
File operations module for the backup system.
Handles temporary directory creation, file copying, and cleanup operations.
"""

from constants import FileLocations as FileDIR
import os
import shutil


def ignore_patterns(dir, files):
    """Define patterns to ignore during copying."""
    ignore_list = []
    for file in files:
        if file == '.git':
            ignore_list.append(file)
        elif file == '__pycache__':
            ignore_list.append(file)
        elif file == 'desktop.ini':
            ignore_list.append(file)
        elif file.lower() == 'thumbs.db':
            ignore_list.append(file)
        elif (os.path.abspath(os.path.join(dir, file)) ==
              os.path.abspath(FileDIR.TEMPORARY_HOLD_FILE_PATH)):
            ignore_list.append(file)

    return ignore_list


def handle_remove_readonly(func, path, exc):
    """Handle read-only files on Windows by changing permissions."""
    if os.path.exists(path):
        os.chmod(path, 0o777)
        func(path)


def create_temp_path() -> None:
    """
    Creates a temporary directory if it does not already exist.
    Checks whether the directory specified by FileDIR.TEMPORARY_HOLD_FILE_PATH
    exists.If it does not exist, the function creates the directory.
    Returns:
        None
    """

    cleanup_temp_files()

    os.makedirs(FileDIR.TEMPORARY_HOLD_FILE_PATH)


def populate_temp_hold() -> None:
    """
    Recursively copies all files and folders from the locations specified in
    FileDIR.ORIGINAL_FILE_LOCATIONS to the temporary hold directory defined by
    FileDIR.TEMPORARY_HOLD_FILE_PATH.
    Preserves the directory structure relative to the source location.
    Excludes .git directories and other system/temporary files.
    Returns:
        None
    """

    for file_location in FileDIR.ORIGINAL_FILE_LOCATIONS:
        if os.path.exists(file_location):
            if os.path.isfile(file_location):
                shutil.copy(file_location, FileDIR.TEMPORARY_HOLD_FILE_PATH)
            elif os.path.isdir(file_location):
                dest_dir = os.path.join(
                    FileDIR.TEMPORARY_HOLD_FILE_PATH,
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
    This function checks if the directory specified by
    FileDIR.TEMPORARY_HOLD_FILE_PATH exists, and if so,
    deletes it along with all its contents.
    Handles permission errors that may occur on Windows systems.
    Returns:
        None
    """

    if os.path.exists(FileDIR.TEMPORARY_HOLD_FILE_PATH):
        shutil.rmtree(
            FileDIR.TEMPORARY_HOLD_FILE_PATH,
            onerror=handle_remove_readonly
        )
