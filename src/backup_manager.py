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
import concurrent.futures
import threading
import mmap


def _validate_temp_path(temp_path: str) -> None:
    """Validates the temporary path."""
    if not os.path.exists(temp_path):
        raise FileNotFoundError(f"Temporary directory not found: {temp_path}")


def _get_optimal_buffer_size(file_size: int) -> int:
    """
    Calculate optimal buffer size based on file size and system resources.

    Args:
        file_size (int): Size of the file in bytes

    Returns:
        int: Optimal buffer size in bytes
    """
    # Base buffer size from configuration
    base_buffer_mb = FileDIR.HASH_BUFFER_SIZE_MB
    base_buffer_bytes = base_buffer_mb * 1024 * 1024

    # For small files, use smaller buffers to avoid over-allocation
    if file_size < base_buffer_bytes:
        # Use 1/4 of file size, but at least 64KB
        return max(64 * 1024, file_size // 4)

    # For larger files, use the configured buffer size
    # But cap it at 64MB to avoid excessive memory usage
    return min(base_buffer_bytes, 64 * 1024 * 1024)


def _should_use_memory_mapping(file_size: int) -> bool:
    """
    Determine if memory mapping should be used based on file size and configuration.

    Args:
        file_size (int): Size of the file in bytes

    Returns:
        bool: True if memory mapping should be used
    """
    if not FileDIR.USE_MEMORY_MAPPING:
        return False

    threshold_bytes = FileDIR.MEMORY_MAP_THRESHOLD_MB * 1024 * 1024
    return file_size > threshold_bytes


def _add_file_to_zip_threaded(args):
    """Thread-safe version of _add_file_to_zip for concurrent processing."""
    zipf, file_path, temp_path, zip_file_absolute_path = args
    logger = get_logger("backup_manager._add_file_to_zip_threaded")
    file_absolute_path = os.path.abspath(file_path)

    if file_absolute_path == zip_file_absolute_path:
        return 0, None

    try:
        file_size = os.path.getsize(file_path)
        arcname = os.path.relpath(file_path, temp_path)

        # Instead of reading the whole file, return the file path and arcname for streaming
        logger.debug(f"Prepared for ZIP: {arcname} ({file_size} bytes)")
        return file_size, (arcname, file_path)
    except (OSError, PermissionError) as e:
        logger.warning(f"Failed to prepare file for ZIP: {file_path} - {e}")
        return 0, None


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


def _get_files_to_zip(temp_path: str, zip_file_absolute_path: str) -> list[str]:
    """Collects all files to be added to the ZIP archive."""
    all_files = []
    for root, _, files in os.walk(temp_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.abspath(file_path) != zip_file_absolute_path:
                all_files.append(file_path)
    return all_files


def _process_files_for_zip(
    zipf, all_files: list[str], temp_path: str, zip_file_absolute_path: str
) -> tuple[int, int]:
    """Processes and adds files to the ZIP archive using multi-threading."""
    logger = get_logger("backup_manager._process_files_for_zip")
    file_count = 0
    total_size = 0
    write_lock = threading.Lock()

    max_workers = (
        FileDIR.ZIP_THREADS if FileDIR.ZIP_THREADS > 0 else min(4, os.cpu_count() or 1)
    )
    logger.debug(f"Using {max_workers} worker threads for zipping.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(
                _add_file_to_zip_threaded,
                (zipf, file_path, temp_path, zip_file_absolute_path),
            ): file_path
            for file_path in all_files
        }

        for future in concurrent.futures.as_completed(future_to_file):
            try:
                file_size, file_data = future.result()
                if file_data:
                    arcname, file_path = file_data
                    with write_lock:
                        with open(file_path, "rb") as f:
                            zipf.writestr(
                                arcname, f.read(), compress_type=zipfile.ZIP_DEFLATED
                            )
                    total_size += file_size
                    file_count += 1
            except Exception as e:
                file_path = future_to_file[future]
                logger.warning(f"Failed to process file {file_path}: {e}")

    return file_count, total_size


def zip_temp_hold() -> str:
    """
    Creates a ZIP archive of all files located in the temporary hold directory.
    Uses multi-threading for faster file processing and higher compression level.
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
                "Temporary directory not initialized. Call create_temp_path() first."
            )
        _validate_temp_path(temp_path)

        zip_file_path = os.path.join(temp_path, f"{FileDIR.BACKUP_FILE_NAME}.zip")
        zip_file_absolute_path = os.path.abspath(zip_file_path)
        logger.debug(f"Creating ZIP archive at: {zip_file_path}")

        all_files = _get_files_to_zip(temp_path, zip_file_absolute_path)

        compression_level = FileDIR.ZIP_COMPRESSION_LEVEL
        with zipfile.ZipFile(
            zip_file_path, "w", zipfile.ZIP_DEFLATED, compresslevel=compression_level
        ) as zipf:
            if not all_files:
                logger.warning(
                    "No files found to add to ZIP archive. Creating empty ZIP."
                )
                return zip_file_path

            logger.info(f"Processing {len(all_files)} files for ZIP archive...")
            file_count, total_size = _process_files_for_zip(
                zipf, all_files, temp_path, zip_file_absolute_path
            )

        if file_count == 0:
            logger.warning("No files were added to the ZIP archive")
        else:
            logger.info(f"ZIP archive created: {file_count} files, {total_size} bytes")

        return zip_file_path

    except Exception as e:
        logger.error(f"Failed to create ZIP archive: {e}", exc_info=True)
        raise


def _collect_backup_files() -> list[str]:
    """Collects all existing backup file paths."""
    logger = get_logger("backup_manager._collect_backup_files")
    backup_files = []
    for backup_location in FileDIR.BACKUP_LOCATIONS:
        backup_file_path = os.path.join(
            backup_location, f"{FileDIR.BACKUP_FILE_NAME}.zip"
        )
        logger.debug(f"Checking for backup at: {backup_file_path}")
        if os.path.exists(backup_file_path) and os.path.isfile(backup_file_path):
            backup_files.append(backup_file_path)
        else:
            logger.debug(f"Backup file not found: {backup_file_path}")
    return backup_files


def _calculate_hashes_in_parallel(backup_files: list[str]) -> list[str]:
    """Calculates hashes for multiple files in parallel."""
    logger = get_logger("backup_manager._calculate_hashes_in_parallel")
    logger.debug(f"Processing {len(backup_files)} backup files in parallel")
    backup_hashes = []

    max_workers = (
        FileDIR.HASH_THREADS
        if FileDIR.HASH_THREADS > 0
        else min(len(backup_files), os.cpu_count() or 1)
    )
    logger.debug(f"Using {max_workers} worker threads for hashing")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(calculate_file_hash, file_path): file_path
            for file_path in backup_files
        }
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                file_hash = future.result()
                backup_hashes.append(file_hash)
                logger.debug(f"Hash computed for {file_path}: {file_hash[:16]}...")
            except (OSError, PermissionError) as e:
                logger.warning(f"Failed to read backup file {file_path}: {e}")
            except Exception as e:
                logger.error(
                    f"Unexpected error hashing {file_path}: {e}", exc_info=True
                )
    return backup_hashes


def get_existing_backup_hashes() -> list:
    """
    Retrieves a list of hash values for existing backup files using optimized hashing.
    Uses parallel processing when multiple backup files exist for better performance.
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
    try:
        backup_files = _collect_backup_files()

        if not backup_files:
            logger.info("No existing backup files found")
            return []

        if len(backup_files) == 1:
            try:
                file_hash = calculate_file_hash(backup_files[0])
                logger.debug(
                    f"Hash computed for {backup_files[0]}: {file_hash[:16]}..."
                )
                logger.info("Found 1 readable backup file")
                return [file_hash]
            except (OSError, PermissionError) as e:
                logger.warning(f"Failed to read backup file {backup_files[0]}: {e}")
                return []

        backup_hashes = _calculate_hashes_in_parallel(backup_files)
        logger.info(f"Found {len(backup_hashes)} readable backup file(s)")
        return backup_hashes

    except Exception as e:
        logger.error(f"Error retrieving backup hashes: {e}", exc_info=True)
        raise


def calculate_file_hash(file_path: str) -> str:
    """
    Calculates the SHA-256 hash of a file's content using optimized I/O methods.
    Uses adaptive buffer sizing and memory mapping for large files.

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

        # Get file size for optimization decisions
        file_size = os.path.getsize(file_path)
        logger.debug(f"File size: {file_size:,} bytes")

        hash_sha256 = hashlib.sha256()

        # Use memory mapping for large files if enabled
        if _should_use_memory_mapping(file_size):
            logger.debug("Using memory mapping for large file")
            try:
                with open(file_path, "rb") as f:
                    with mmap.mmap(
                        f.fileno(), 0, access=mmap.ACCESS_READ
                    ) as mmapped_file:
                        # Process in chunks to avoid loading entire file into memory at once
                        buffer_size = _get_optimal_buffer_size(file_size)
                        for i in range(0, len(mmapped_file), buffer_size):
                            chunk = mmapped_file[i : i + buffer_size]
                            hash_sha256.update(chunk)
            except (OSError, ValueError) as e:
                # Fall back to regular reading if memory mapping fails
                logger.debug(
                    f"Memory mapping failed, falling back to buffered reading: {e}"
                )
                hash_sha256 = hashlib.sha256()  # Reset hash
                _calculate_hash_buffered(file_path, hash_sha256, file_size)
        else:
            # Use optimized buffered reading for smaller files
            _calculate_hash_buffered(file_path, hash_sha256, file_size)

        file_hash = hash_sha256.hexdigest()
        logger.debug(f"Hash calculated: {file_hash[:16]}...")
        return file_hash

    except Exception as e:
        logger.error(f"Error calculating file hash for {file_path}: {e}", exc_info=True)
        raise


def _calculate_hash_buffered(file_path: str, hash_obj, file_size: int) -> None:
    """
    Calculate hash using optimized buffered reading.

    Args:
        file_path (str): Path to the file
        hash_obj: Hash object to update
        file_size (int): Size of the file in bytes
    """
    buffer_size = _get_optimal_buffer_size(file_size)

    with open(file_path, "rb") as f:
        while chunk := f.read(buffer_size):
            hash_obj.update(chunk)


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
