"""
Backup management module for the backup system.
Handles ZIP file creation, hash comparison, and backup updating operations.
"""

from constants import FileLocations as FileDIR
from temp_manager import TempManager
import os
import shutil
import zipfile
import hashlib


def zip_temp_hold() -> str:
    """
    Creates a ZIP archive of all files located in the temporary hold directory.
    The ZIP file is named using the backup file name and saved in the
    temporary hold directory. All files within the directory are added to the
    archive, preserving their relative paths.
    Returns:
        str: The file path to the created ZIP archive.
    """
    temp_path = TempManager.get_temp_path()
    if temp_path is None:
        raise RuntimeError(
            "Temporary directory not initialized. "
            "Call create_temp_path() first."
        )

    zip_file_path = os.path.join(
        temp_path,
        f"{FileDIR.BACKUP_FILE_NAME}.zip"
    )
    zip_file_absolute_path = os.path.abspath(zip_file_path)

    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(temp_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_absolute_path = os.path.abspath(file_path)
                if file_absolute_path == zip_file_absolute_path:
                    continue
                zipf.write(
                    file_path,
                    os.path.relpath(
                        file_path,
                        temp_path
                    )
                )

    return zip_file_path


def get_existing_backup_hashes() -> list:
    """
    Retrieves a list of hash values for existing backup files.
    Iterates through all backup locations specified in FileDIR.
    BACKUP_LOCATIONS, checks if the backup file exists and is a file, then
    reads its content and computes a hash value based on the file's content.
    The hash values are collected and returned as a list.
    Returns:
        list: A list of hash values (strings) representing the SHA-256
        hashes of existing backup files.
    """

    backup_hashes = []

    for backup_location in FileDIR.BACKUP_LOCATIONS:
        backup_file_path = os.path.join(backup_location,
                                        f"{FileDIR.BACKUP_FILE_NAME}.zip")
        if (os.path.exists(backup_file_path) and
                os.path.isfile(backup_file_path)):
            with open(backup_file_path, 'rb') as f:
                file_content = f.read()
                backup_hashes.append(hashlib.sha256(file_content).hexdigest())

    return backup_hashes


def calculate_file_hash(file_path: str) -> str:
    """
    Calculates the SHA-256 hash of a file's content.
    Args:
        file_path (str): Path to the file to hash.
    Returns:
        str: SHA-256 hash value of the file's content as a hexadecimal string.
    """
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def all_hashes_match(existing_hashes: list, new_hash: str) -> bool:
    """
    Checks if all hashes in the existing_hashes list match the new_hash.
    Args:
        existing_hashes (list): A list of string hash values to compare.
        new_hash (str): The hash value to compare against each element in
        existing_hashes.
    Returns:
        bool: True if all elements in existing_hashes are equal to new_hash
        and the list is not empty, False otherwise.
    """

    if not existing_hashes:
        return False

    return all(existing_hash == new_hash for existing_hash in existing_hashes)


def update_all_backups(zip_file_path: str) -> None:
    """
    Updates all backup locations with the specified zip file.
    This function iterates through all backup locations defined in `FileDIR.
    BACKUP_LOCATIONS`. For each location, it removes any existing backup zip
    file named according to `FileDIR.BACKUP_FILE_NAME.zip`, and then copies
    the provided `zip_file_path` to that location.
    Args:
        zip_file_path (str): The path to the zip file to be copied to all
        backup locations.
    Raises:
        OSError: If there is an error removing or copying files.
    """

    for backup_location in FileDIR.BACKUP_LOCATIONS:
        file_dir = os.path.join(backup_location,
                                f"{FileDIR.BACKUP_FILE_NAME}.zip")

        os.makedirs(backup_location, exist_ok=True)

        if os.path.exists(file_dir):
            os.remove(file_dir)

        shutil.copy(zip_file_path, file_dir)
