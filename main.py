from notification_manager import send_notification
from file_operations import (
    create_temp_path,
    populate_temp_hold,
    cleanup_temp_files
)
from backup_manager import (
    zip_temp_hold,
    get_existing_backup_hashes,
    calculate_file_hash,
    all_hashes_match,
    update_all_backups,
)
from constants import FileLocations


def main():
    """Main execution function for the backup system."""
    print("Creating temporary file directory...")
    create_temp_path()

    print("Populating temporary hold with files...")
    populate_temp_hold()

    print("Retrieving existing backup hashes...")
    existing_backup_hashes = get_existing_backup_hashes()

    print("Zipping temporary hold files...")
    zipped_backup = zip_temp_hold()

    print("Calculating new backup hash...")
    new_backup_hash = calculate_file_hash(zipped_backup)

    print("Checking if existing backups match the new backup hash...")
    if not all_hashes_match(existing_backup_hashes, new_backup_hash):
        print("Existing backups do not match the new backup hash.")
        print("Updating all backups with the new zip file...")
        update_all_backups(zipped_backup)
    else:
        print("Backup is up to date. No changes needed.")

    print("Cleaning up temporary files...")
    cleanup_temp_files()
    print("Backup process completed successfully!")

    locations_str = "\n".join(FileLocations.BACKUP_LOCATIONS)
    send_notification(
        "Backup Complete",
        (
            "Your file backup has finished successfully.\n"
            f"Files saved to:\n{locations_str}"
        )
    )


if __name__ == "__main__":
    main()
