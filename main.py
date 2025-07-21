from constants import FileLocations as FileDIR
import os
import shutil
import zipfile


def create_temp_path() -> None:
    if not os.path.exists(FileDIR.TEMPORARY_HOLD_FILE_PATH):
        os.makedirs(FileDIR.TEMPORARY_HOLD_FILE_PATH)


def populate_temp_hold() -> None:
    for file_location in FileDIR.ORIGINAL_FILE_LOCATIONS:
        if os.path.exists(file_location):
            shutil.copy(file_location, FileDIR.TEMPORARY_HOLD_FILE_PATH)


def zip_temp_hold() -> str:
    zip_file_path = os.path.join(FileDIR.TEMPORARY_HOLD_FILE_PATH, f"{FileDIR.BACKUP_FILE_NAME}.zip")

    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(FileDIR.TEMPORARY_HOLD_FILE_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, FileDIR.TEMPORARY_HOLD_FILE_PATH))

    return zip_file_path


def get_existing_backup_hashes() -> list:
    backup_hashes = []

    for backup_location in FileDIR.BACKUP_LOCATIONS:
        for root, dirs, files in os.walk(backup_location):
            for file in files:
                if file.endswith(".zip"):
                    file_path = os.path.join(root, file)
                    backup_hashes.append(hash(file_path))

    return backup_hashes


def all_hashes_match(existing_hashes: list, new_hash: int) -> bool:
    return all(existing_hash == new_hash for existing_hash in existing_hashes)


if __name__ == "__main__":
    """
    1. Look in the ORIGINAL_FILE_LOCATIONS constant and copy all of those
    files to the TEMPORARY_HOLD_FILE_PATH directory
    2. Zip all of the files in the TEMPORARY_HOLD_FILE_PATH directory
    3. Get the hash of the zip file in the TEMPORARY_HOLD_FILE_PATH
    4. Look in all of the locations at BACKUP_LOCATIONS and get all zip files
    hashes
    5. Compare hashes of BACKUP_LOCATIONS with the hash of the zip file at
    TEMPORARY_HOLD_FILE_PATH
    6. If hashes are different, copy the zip file in TEMPORARY_HOLD_FILE_PATH
    to all of the file paths in BACKUP_LOCATIONS
    7. Delete all unended files at TEMPORARY_HOLD_FILE_PATH
    """
    create_temp_path()
    populate_temp_hold()

    zipped_backup = zip_temp_hold()
    new_backup_hash = hash(zipped_backup)
    existing_backup_hashes = get_existing_backup_hashes()

    if not all_hashes_match(existing_backup_hashes, new_backup_hash):
        pass
