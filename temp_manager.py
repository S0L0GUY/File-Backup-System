import tempfile
import os
import shutil


class TempManager:
    """
    Manages temporary directory creation and cleanup for the backup system.
    """

    _temp_dir = None

    @classmethod
    def get_temp_path(cls):
        """Get the current temporary directory path."""
        return cls._temp_dir

    @classmethod
    def set_temp_path(cls, path):
        """Set the temporary directory path."""
        cls._temp_dir = path

    @classmethod
    def create_temp_path(cls) -> str:
        """
        Creates a temporary directory using tempfile.mkdtemp().
        This creates a secure temporary directory with appropriate permissions
        and returns the path to the created directory.

        Returns:
            str: The path to the created temporary directory
        """
        # Clean up any existing temporary files first
        cls.cleanup_temp_files()

        temp_dir = tempfile.mkdtemp(prefix="backup_temp_")

        cls.set_temp_path(temp_dir)

        return temp_dir

    @classmethod
    def cleanup_temp_files(cls) -> None:
        """
        Removes the temporary hold directory if it exists.
        This function checks if a temporary directory has been created
        and if so, deletes it along with all its contents.
        Handles permission errors that may occur on Windows systems.
        Returns:
            None
        """
        def handle_remove_readonly(func, path, exc):
            """Handle read-only files on Windows by changing permissions."""
            if os.path.exists(path):
                os.chmod(path, 0o777)
                func(path)

        temp_path = cls.get_temp_path()
        if temp_path is not None and os.path.exists(temp_path):
            shutil.rmtree(
                temp_path,
                onerror=handle_remove_readonly
            )
            cls.set_temp_path(None)
