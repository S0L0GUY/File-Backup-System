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
