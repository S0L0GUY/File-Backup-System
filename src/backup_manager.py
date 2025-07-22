"""
Backup management module for the backup system.
Handles ZIP file creation, hash comparison, and backup updating operations.
"""

from constants import FileLocations as FileDIR
from temp_manager import TempManager
from logging_config import get_logger
import os
import shutil
import zipfile
import hashlib


def _validate_temp_path(temp_path: str) -> None:
    """Validates the temporary path."""
    if not os.path.exists(temp_path):
        raise FileNotFoundError(f"Temporary directory not found: {temp_path}")


def _add_file_to_zip(zipf, file_path, temp_path, zip_file_absolute_path):
    """Adds a single file to the zip archive, returning its size."""
    logger = get_logger("backup_manager._add_file_to_zip")
    file_absolute_path = os.path.abspath(file_path)

    if file_absolute_path == zip_file_absolute_path:
        return 0

    try:
        file_size = os.path.getsize(file_path)
        arcname = os.path.relpath(file_path, temp_path)
        zipf.write(file_path, arcname)
        logger.debug(f"Added to ZIP: {arcname} ({file_size} bytes)")
        return file_size
    except (OSError, PermissionError) as e:
        logger.warning(f"Failed to add file to ZIP: {file_path} - {e}")
        return 0


def zip_temp_hold() -> str:
    """
    Creates a ZIP archive of all files located in the temporary hold directory.
    The ZIP file is named using the backup file name and saved in the
    temporary hold directory. All files within the directory are added to the
    archive, preserving their relative paths.

    Returns:
        str: The file path to the created ZIP archive.

    Raises:
        RuntimeError: If temporary directory is not initialized.
        FileNotFoundError: If temporary directory doesn't exist.
        PermissionError: If unable to create ZIP file due to permissions.
        OSError: If there are issues accessing files or directories.
    """
    logger = get_logger("backup_manager.zip_temp_hold")
    try:
        temp_path = TempManager.get_temp_path()
        if temp_path is None:
            raise RuntimeError(
                "Temporary directory not initialized. " "Call create_temp_path() first."
            )
        _validate_temp_path(temp_path)

        zip_file_path = os.path.join(temp_path, f"{FileDIR.BACKUP_FILE_NAME}.zip")
        zip_file_absolute_path = os.path.abspath(zip_file_path)
        logger.debug(f"Creating ZIP archive at: {zip_file_path}")

        file_count = 0
        total_size = 0

        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = _add_file_to_zip(
                        zipf, file_path, temp_path, zip_file_absolute_path
                    )
                    if file_size > 0:
                        total_size += file_size
                        file_count += 1

        if file_count == 0:
            logger.warning("No files were added to the ZIP archive")
        else:
            logger.info(f"ZIP archive created: {file_count} files, {total_size} bytes")

        return zip_file_path

    except Exception as e:
        logger.error(f"Failed to create ZIP archive: {e}", exc_info=True)
        raise


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

    Raises:
        OSError: If there are issues accessing backup files.
        PermissionError: If unable to read backup files due to permissions.
    """
    logger = get_logger("backup_manager.get_existing_backup_hashes")
    backup_hashes = []

    try:
        for backup_location in FileDIR.BACKUP_LOCATIONS:
            backup_file_path = os.path.join(
                backup_location, f"{FileDIR.BACKUP_FILE_NAME}.zip"
            )

            logger.debug(f"Checking for backup at: {backup_file_path}")

            if os.path.exists(backup_file_path) and os.path.isfile(backup_file_path):
                try:
                    with open(backup_file_path, "rb") as f:
                        file_content = f.read()
                        file_hash = hashlib.sha256(file_content).hexdigest()
                        backup_hashes.append(file_hash)
                        logger.debug(
                            f"Hash computed for {backup_file_path}: "
                            f"{file_hash[:16]}..."
                        )

                except (OSError, PermissionError) as e:
                    logger.warning(
                        f"Failed to read backup file " f"{backup_file_path}: {e}"
                    )
                    # Continue with other backup locations
            else:
                logger.debug(f"Backup file not found: {backup_file_path}")

        logger.info(f"Found {len(backup_hashes)} readable backup file(s)")
        return backup_hashes

    except Exception as e:
        logger.error(f"Error retrieving backup hashes: {e}", exc_info=True)
        raise


def calculate_file_hash(file_path: str) -> str:
    """
    Calculates the SHA-256 hash of a file's content.

    Args:
        file_path (str): Path to the file to hash.

    Returns:
        str: SHA-256 hash value of the file's content as a hexadecimal string.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        PermissionError: If unable to read the file due to permissions.
        OSError: If there are issues accessing the file.
    """
    logger = get_logger("backup_manager.calculate_file_hash")

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")

        logger.debug(f"Calculating hash for: {file_path}")

        with open(file_path, "rb") as f:
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()

        logger.debug(f"Hash calculated: {file_hash[:16]}...")
        return file_hash

    except Exception as e:
        logger.error(f"Error calculating file hash for {file_path}: {e}", exc_info=True)
        raise


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
    logger = get_logger("backup_manager.all_hashes_match")

    try:
        if not existing_hashes:
            logger.debug("No existing hashes found - backup needed")
            return False

        if not isinstance(existing_hashes, list):
            logger.warning("existing_hashes is not a list")
            return False

        if not isinstance(new_hash, str):
            logger.warning("new_hash is not a string")
            return False

        matches = all(existing_hash == new_hash for existing_hash in existing_hashes)

        if matches:
            logger.debug(f"All {len(existing_hashes)} existing hashes match")
        else:
            logger.debug("Hash mismatch detected - backup needed")

        return matches

    except Exception as e:
        logger.error(f"Error comparing hashes: {e}", exc_info=True)
        # Return False to err on the side of caution (trigger backup)
        return False


def _copy_backup_to_location(zip_file_path: str, backup_location: str):
    """Copies the backup file to a single backup location."""
    logger = get_logger("backup_manager._copy_backup_to_location")
    backup_file_name = f"{FileDIR.BACKUP_FILE_NAME}.zip"
    destination_zip_path = os.path.join(backup_location, backup_file_name)

    try:
        if not os.path.exists(backup_location):
            os.makedirs(backup_location)
            logger.info(f"Created backup directory: {backup_location}")

        if os.path.exists(destination_zip_path):
            os.remove(destination_zip_path)
            logger.debug(f"Removed existing backup: {destination_zip_path}")

        shutil.copy2(zip_file_path, destination_zip_path)
        logger.info(f"Backup updated at: {destination_zip_path}")
        return True
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to update backup at {backup_location}: {e}")
        return False


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
        FileNotFoundError: If the source zip file doesn't exist.
        PermissionError: If unable to write to backup locations.
        OSError: If there are issues creating directories or copying files.
    """
    logger = get_logger("backup_manager.update_all_backups")
    if zip_file_path is None:
        raise ValueError("zip_file_path cannot be None.")
    if not os.path.exists(zip_file_path):
        raise FileNotFoundError(f"Source ZIP file not found: {zip_file_path}")

    success_count = 0
    for backup_location in FileDIR.BACKUP_LOCATIONS:
        if _copy_backup_to_location(zip_file_path, backup_location):
            success_count += 1

    if success_count == len(FileDIR.BACKUP_LOCATIONS):
        logger.info("All backup locations updated successfully.")
    else:
        logger.warning(
            f"Only {success_count} out of {len(FileDIR.BACKUP_LOCATIONS)} "
            "backups were updated successfully."
        )
