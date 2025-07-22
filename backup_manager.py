"""
Backup management module for the backup system.
Handles ZIP file creation, hash comparison, and backup updating operations.
"""

from constants import FileLocations as FileDIR
import os
import shutil
import zipfile


def zip_temp_hold() -> str:
    """
    Creates a ZIP archive of all files located in the temporary hold directory.
    The ZIP file is named using the backup file name and saved in the
    temporary hold directory. All files within the directory are added to the
    archive, preserving their relative paths.
    Returns:
        str: The file path to the created ZIP archive.
    """

    zip_file_path = os.path.join(
        FileDIR.TEMPORARY_HOLD_FILE_PATH,
        f"{FileDIR.BACKUP_FILE_NAME}.zip"
    )

    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(FileDIR.TEMPORARY_HOLD_FILE_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path == zip_file_path:
                    continue
                zipf.write(
                    file_path,
                    os.path.relpath(
                        file_path,
                        FileDIR.TEMPORARY_HOLD_FILE_PATH
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
        list: A list of hash values (integers) representing the contents of
        existing backup files.
    """

    backup_hashes = []

    for backup_location in FileDIR.BACKUP_LOCATIONS:
        backup_file_path = os.path.join(backup_location,
                                        f"{FileDIR.BACKUP_FILE_NAME}.zip")
        if (os.path.exists(backup_file_path) and
                os.path.isfile(backup_file_path)):
            with open(backup_file_path, 'rb') as f:
                file_content = f.read()
                backup_hashes.append(hash(file_content))

    return backup_hashes


def calculate_file_hash(file_path: str) -> int:
    """
    Calculates the hash of a file's content.
    Args:
        file_path (str): Path to the file to hash.
    Returns:
        int: Hash value of the file's content.
    """
    with open(file_path, 'rb') as f:
        return hash(f.read())


def all_hashes_match(existing_hashes: list, new_hash: int) -> bool:
    """
    Checks if all hashes in the existing_hashes list match the new_hash.
    Args:
        existing_hashes (list): A list of integer hash values to compare.
        new_hash (int): The hash value to compare against each element in
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
