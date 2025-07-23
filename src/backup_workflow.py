"""
Backup workflow management module.
Handles the main backup process execution and coordination.
"""

import sys
from logging_config import BackupLogger, LoggedOperation
from notification_manager import send_notification
from file_operations import (
    create_temp_path,
    populate_temp_hold,
    cleanup_temp_files,
)
from backup_manager import (
    zip_temp_hold,
    get_existing_backup_hashes,
    calculate_file_hash,
    all_hashes_match,
    update_all_backups,
)
from constants import FileLocations


def execute_backup_workflow():
    """
    Execute the complete backup workflow with comprehensive error handling.

    Returns:
        bool: True if backup was successful, False otherwise
    """
    logger = None
    backup_successful = False

    try:
        # Initialize logging
        logger = BackupLogger.setup_logging()
        logger.info("=" * 50)
        logger.info("Starting File Backup System")
        logger.info("=" * 50)

        # Execute main backup steps
        _run_backup_steps(logger)

        # Send success notification
        _send_success_notification(logger)

        logger.info("Backup process completed successfully!")
        backup_successful = True
        return True

    except KeyboardInterrupt:
        _handle_user_interruption(logger)
        return False

    except Exception as e:
        _handle_backup_error(logger, e)
        return False

    finally:
        _finalize_logging(logger, backup_successful)


def _run_backup_steps(logger):
    """Execute the main backup process steps."""
    # Step 1: Create temporary directory
    with LoggedOperation("temporary directory creation", logger):
        temp_path = create_temp_path()
        logger.info(f"Created temporary directory: {temp_path}")

    # Step 2: Populate temporary hold with files
    with LoggedOperation("file population to temporary directory", logger):
        populate_temp_hold()

    # Step 3: Get existing backup hashes
    with LoggedOperation("retrieving existing backup hashes", logger):
        existing_backup_hashes = get_existing_backup_hashes()
        backup_count = len(existing_backup_hashes)
        logger.info(f"Found {backup_count} existing backup(s)")

    # Step 4: Create ZIP backup
    with LoggedOperation("creating ZIP backup", logger):
        zipped_backup = zip_temp_hold()
        logger.info(f"Created backup ZIP: {zipped_backup}")

    # Step 5: Calculate new backup hash
    with LoggedOperation("calculating backup hash", logger):
        new_backup_hash = calculate_file_hash(zipped_backup)
        logger.info(f"New backup hash: {new_backup_hash[:16]}...")

    # Step 6: Check if backup needs updating
    with LoggedOperation("comparing backup hashes", logger):
        if not all_hashes_match(existing_backup_hashes, new_backup_hash):
            logger.info("Backup changes detected - updating all locations")

            with LoggedOperation("updating all backup locations", logger):
                update_all_backups(zipped_backup)
                logger.info("All backup locations updated successfully")
        else:
            logger.info("No changes detected - backup is up to date")

    # Step 7: Cleanup temporary files
    with LoggedOperation("cleaning up temporary files", logger):
        cleanup_temp_files()


def _send_success_notification(logger):
    """Send success notification to the user."""
    try:
        locations_str = "\n".join(FileLocations.BACKUP_LOCATIONS)
        send_notification(
            "Backup Complete",
            (
                "Your file backup has finished successfully. "
                f"Files saved to:\n{locations_str}"
            ),
        )
    except Exception as notification_error:
        msg = f"Failed to send notification: {notification_error}"
        logger.warning(msg)


def _handle_user_interruption(logger):
    """Handle backup interruption by user (Ctrl+C)."""
    error_msg = "Backup process interrupted by user"
    if logger:
        logger.warning(error_msg)
    else:
        print(f"WARNING: {error_msg}")

    _attempt_cleanup(logger, "Failed to cleanup after interruption")
    _send_interruption_notification(logger)
    sys.exit(1)


def _handle_backup_error(logger, error):
    """Handle unexpected backup errors."""
    error_msg = f"Backup process failed with error: {str(error)}"
    if logger:
        logger.error(error_msg, exc_info=True)
    else:
        print(f"CRITICAL ERROR: {error_msg}")

    _attempt_cleanup(logger, "Failed to cleanup temporary files after error")
    _send_failure_notification(logger, error)
    sys.exit(1)


def _attempt_cleanup(logger, error_prefix):
    """Attempt to cleanup temporary files with error handling."""
    try:
        cleanup_temp_files()
        if logger:
            logger.info("Temporary files cleaned up after error")
    except Exception as cleanup_error:
        cleanup_msg = f"{error_prefix}: {cleanup_error}"
        if logger:
            logger.error(cleanup_msg)
        else:
            print(f"ERROR: {cleanup_msg}")


def _send_interruption_notification(logger):
    """Send notification for user interruption."""
    try:
        send_notification(
            "Backup Interrupted", "The backup process was interrupted by the user."
        )
    except Exception:
        pass  # Ignore notification errors during interruption


def _send_failure_notification(logger, error):
    """Send notification for backup failure."""
    try:
        message = f"The backup process failed: {str(error)}"
        send_notification("Backup Failed", message)
    except Exception as notification_error:
        msg = f"Failed to send failure notification: {notification_error}"
        if logger:
            logger.warning(msg)


def _finalize_logging(logger, backup_successful):
    """Complete the logging process with final messages."""
    if logger:
        log_file = BackupLogger.get_log_file_path()
        if log_file and backup_successful:
            logger.info(f"Detailed logs saved to: {log_file}")
        logger.info("=" * 50)
        logger.info("File Backup System Finished")
        logger.info("=" * 50)
