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
            if os.path.isfile(file_location):
                shutil.copy(file_location, FileDIR.TEMPORARY_HOLD_FILE_PATH)
            elif os.path.isdir(file_location):
                items = os.listdir(file_location)
                for item in items:
                    item_path = os.path.join(file_location, item)

                    if os.path.isfile(item_path):
                        shutil.copy(item_path,
                                    FileDIR.TEMPORARY_HOLD_FILE_PATH)
                    elif os.path.isdir(item_path):
                        pass


def zip_temp_hold() -> str:
    zip_file_path = os.path.join(
        FileDIR.TEMPORARY_HOLD_FILE_PATH,
        f"{FileDIR.BACKUP_FILE_NAME}.zip"
    )

    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(FileDIR.TEMPORARY_HOLD_FILE_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(
                    file_path,
                    os.path.relpath(
                        file_path,
                        FileDIR.TEMPORARY_HOLD_FILE_PATH
                    )
                )

    return zip_file_path


def get_existing_backup_hashes() -> list:
    backup_hashes = []

    for backup_location in FileDIR.BACKUP_LOCATIONS:
        backup_file_path = os.path.join(backup_location,
                                        f"{FileDIR.BACKUP_FILE_NAME}.zip")
        if (os.path.exists(backup_file_path) and
                os.path.isfile(backup_file_path)):
            # Calculate hash based on file content, not just path
            with open(backup_file_path, 'rb') as f:
                file_content = f.read()
                backup_hashes.append(hash(file_content))

    return backup_hashes


def all_hashes_match(existing_hashes: list, new_hash: int) -> bool:
    if not existing_hashes:
        # If there are no existing backups, we need to create one
        return False

    return all(existing_hash == new_hash for existing_hash in existing_hashes)


def update_all_backups(zip_file_path: str) -> None:
    for backup_location in FileDIR.BACKUP_LOCATIONS:
        file_dir = os.path.join(backup_location,
                                f"{FileDIR.BACKUP_FILE_NAME}.zip")
        if os.path.exists(file_dir):
            os.remove(file_dir)

        shutil.copy(zip_file_path, file_dir)


def cleanup_temp_files() -> None:
    if os.path.exists(FileDIR.TEMPORARY_HOLD_FILE_PATH):
        shutil.rmtree(FileDIR.TEMPORARY_HOLD_FILE_PATH)


if __name__ == "__main__":
    create_temp_path()

    populate_temp_hold()

    zipped_backup = zip_temp_hold()

    with open(zipped_backup, 'rb') as f:
        new_backup_hash = hash(f.read())

    existing_backup_hashes = get_existing_backup_hashes()

    if not all_hashes_match(existing_backup_hashes, new_backup_hash):
        update_all_backups(zipped_backup)

    cleanup_temp_files()
