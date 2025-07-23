"""
Tests for the temp_manager module.
"""

import unittest
import shutil
import os


class TestTempManager(unittest.TestCase):
    """Test cases for TempManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Import here to avoid import issues during test discovery
        from temp_manager import TempManager

        self.temp_manager = TempManager
        # Reset the temp path before each test
        self.temp_manager.set_temp_path(None)

    def tearDown(self):
        """Clean up after tests."""
        # Clean up any temp path that was created
        temp_path = self.temp_manager.get_temp_path()
        if temp_path and os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        self.temp_manager.set_temp_path(None)

    def test_get_temp_path_when_none(self):
        """Test getting temp path when none is set."""
        result = self.temp_manager.get_temp_path()
        self.assertIsNone(result)

    def test_create_temp_path(self):
        """Test creating a temporary path."""
        temp_path = self.temp_manager.create_temp_path()

        # Check that path was created and exists
        self.assertIsNotNone(temp_path)
        self.assertTrue(os.path.exists(temp_path))
        self.assertTrue(os.path.isdir(temp_path))

        # Check that get_temp_path returns the same path
        self.assertEqual(self.temp_manager.get_temp_path(), temp_path)

    def test_cleanup_temp_files(self):
        """Test cleaning up temporary files."""
        # First create a temp path
        temp_path = self.temp_manager.create_temp_path()
        self.assertTrue(os.path.exists(temp_path))

        # Create a test file in it
        test_file = os.path.join(temp_path, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Cleanup
        self.temp_manager.cleanup_temp_files()

        # Check that directory is removed and temp_path is None
        self.assertFalse(os.path.exists(temp_path))
        self.assertIsNone(self.temp_manager.get_temp_path())

    def test_cleanup_when_no_temp_path(self):
        """Test cleanup when no temp path exists."""
        # Should not raise an exception
        self.temp_manager.cleanup_temp_files()
        self.assertIsNone(self.temp_manager.get_temp_path())


if __name__ == "__main__":
    unittest.main()
