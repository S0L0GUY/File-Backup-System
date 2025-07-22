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
    logger = get_logger('backup_manager.zip_temp_hold')

    try:
        temp_path = TempManager.get_temp_path()
        if temp_path is None:
            raise RuntimeError(
                "Temporary directory not initialized. "
                "Call create_temp_path() first."
            )

        if not os.path.exists(temp_path):
            error_msg = f"Temporary directory not found: {temp_path}"
            raise FileNotFoundError(error_msg)

        zip_file_path = os.path.join(
            temp_path,
            f"{FileDIR.BACKUP_FILE_NAME}.zip"
        )
        zip_file_absolute_path = os.path.abspath(zip_file_path)

        logger.debug(f"Creating ZIP archive at: {zip_file_path}")

        file_count = 0
        total_size = 0

        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_absolute_path = os.path.abspath(file_path)

                    # Skip the zip file itself
                    if file_absolute_path == zip_file_absolute_path:
                        continue

                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        file_count += 1

                        arcname = os.path.relpath(file_path, temp_path)
                        zipf.write(file_path, arcname)
                        debug_msg = (f"Added to ZIP: {arcname} "
                                     f"({file_size} bytes)")
                        logger.debug(debug_msg)

                    except (OSError, PermissionError) as e:
                        warn_msg = (f"Failed to add file to ZIP: "
                                    f"{file_path} - {e}")
                        logger.warning(warn_msg)
                        # Continue with other files instead of failing

        if file_count == 0:
            logger.warning("No files were added to the ZIP archive")
        else:
            info_msg = (f"ZIP archive created: {file_count} files, "
                        f"{total_size} bytes")
            logger.info(info_msg)

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
    logger = get_logger('backup_manager.get_existing_backup_hashes')
    backup_hashes = []

    try:
        for backup_location in FileDIR.BACKUP_LOCATIONS:
            backup_file_path = os.path.join(
                backup_location,
                f"{FileDIR.BACKUP_FILE_NAME}.zip"
            )

            logger.debug(f"Checking for backup at: {backup_file_path}")

            if (os.path.exists(backup_file_path) and
                    os.path.isfile(backup_file_path)):
                try:
                    with open(backup_file_path, 'rb') as f:
                        file_content = f.read()
                        file_hash = hashlib.sha256(file_content).hexdigest()
                        backup_hashes.append(file_hash)
                        logger.debug(f"Hash computed for {backup_file_path}: "
                                     f"{file_hash[:16]}...")

                except (OSError, PermissionError) as e:
                    logger.warning(f"Failed to read backup file "
                                   f"{backup_file_path}: {e}")
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
    logger = get_logger('backup_manager.calculate_file_hash')

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")

        logger.debug(f"Calculating hash for: {file_path}")

        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()

        logger.debug(f"Hash calculated: {file_hash[:16]}...")
        return file_hash

    except Exception as e:
        logger.error(f"Error calculating file hash for {file_path}: {e}",
                     exc_info=True)
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
    logger = get_logger('backup_manager.all_hashes_match')

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

        matches = all(existing_hash == new_hash for existing_hash
                      in existing_hashes)

        if matches:
            logger.debug(f"All {len(existing_hashes)} existing hashes match")
        else:
            logger.debug("Hash mismatch detected - backup needed")

        return matches

    except Exception as e:
        logger.error(f"Error comparing hashes: {e}", exc_info=True)
        # Return False to err on the side of caution (trigger backup)
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
    logger = get_logger('backup_manager.update_all_backups')

    try:
        if not os.path.exists(zip_file_path):
            error_msg = f"Source zip file not found: {zip_file_path}"
            raise FileNotFoundError(error_msg)

        if not os.path.isfile(zip_file_path):
            raise ValueError(f"Source path is not a file: {zip_file_path}")

        backup_count = len(FileDIR.BACKUP_LOCATIONS)
        logger.info(f"Updating {backup_count} backup location(s)")

        successful_backups = 0
        failed_backups = 0

        for backup_location in FileDIR.BACKUP_LOCATIONS:
            try:
                backup_file_path = os.path.join(
                    backup_location,
                    f"{FileDIR.BACKUP_FILE_NAME}.zip"
                )

                logger.debug(f"Updating backup at: {backup_location}")

                # Create backup directory if it doesn't exist
                os.makedirs(backup_location, exist_ok=True)

                # Remove existing backup if it exists
                if os.path.exists(backup_file_path):
                    debug_msg = f"Removing existing backup: {backup_file_path}"
                    logger.debug(debug_msg)
                    os.remove(backup_file_path)

                # Copy new backup
                logger.debug(f"Copying backup to: {backup_file_path}")
                shutil.copy2(zip_file_path, backup_file_path)

                # Verify the copy was successful
                if os.path.exists(backup_file_path):
                    successful_backups += 1
                    logger.debug(f"Successfully updated: {backup_location}")
                else:
                    failed_backups += 1
                    error_msg = f"Copy verification failed: {backup_location}"
                    logger.error(error_msg)

            except (OSError, PermissionError, shutil.Error) as e:
                failed_backups += 1
                error_msg = (f"Failed to update backup at "
                             f"{backup_location}: {e}")
                logger.error(error_msg)
                # Continue with other backup locations

        # Log final results
        if successful_backups > 0:
            logger.info(f"Successfully updated {successful_backups} backup(s)")
        if failed_backups > 0:
            logger.warning(f"Failed to update {failed_backups} backup(s)")

        if successful_backups == 0:
            raise RuntimeError("Failed to update any backup locations")

    except Exception as e:
        logger.error(f"Error updating backups: {e}", exc_info=True)
        raise
