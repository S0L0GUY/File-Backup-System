"""
Tests for the constants module.
"""

import unittest


class TestFileLocations(unittest.TestCase):
    """Test cases for FileLocations constants."""

    def test_backup_file_name_default(self):
        """Test that backup file name has a default value."""
        from constants import FileLocations

        self.assertEqual(FileLocations.BACKUP_FILE_NAME, "backup")

    def test_default_timeout(self):
        """Test that default timeout is set."""
        from constants import FileLocations

        self.assertEqual(FileLocations.DEFAULT_TIMEOUT, 10)

    def test_original_file_locations_is_list(self):
        """Test that original file locations is a list."""
        from constants import FileLocations

        self.assertIsInstance(FileLocations.ORIGINAL_FILE_LOCATIONS, list)

    def test_backup_locations_is_list(self):
        """Test that backup locations is a list."""
        from constants import FileLocations

        self.assertIsInstance(FileLocations.BACKUP_LOCATIONS, list)


if __name__ == "__main__":
    unittest.main()
