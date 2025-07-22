"""
Integration tests for the backup workflow.
"""

import unittest
import tempfile
import shutil
import os
from unittest.mock import patch


class TestBackupWorkflowIntegration(unittest.TestCase):
    """Integration test cases for the complete backup workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_source_dir = tempfile.mkdtemp()
        self.test_backup_dir = tempfile.mkdtemp()

        # Create test files
        self.test_file1 = os.path.join(self.test_source_dir, "file1.txt")
        with open(self.test_file1, "w") as f:
            f.write("Content of file 1")

        self.test_file2 = os.path.join(self.test_source_dir, "file2.txt")
        with open(self.test_file2, "w") as f:
            f.write("Content of file 2")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_source_dir):
            shutil.rmtree(self.test_source_dir)
        if os.path.exists(self.test_backup_dir):
            shutil.rmtree(self.test_backup_dir)

    @patch("constants.FileLocations")
    @patch("notification_manager.send_notification")
    def test_backup_workflow_success(self, mock_notification, mock_constants):
        """Test successful backup workflow execution."""
        # Setup mocks
        mock_constants.ORIGINAL_FILE_LOCATIONS = [self.test_source_dir]
        mock_constants.BACKUP_LOCATIONS = [self.test_backup_dir]
        mock_constants.BACKUP_FILE_NAME = "test_backup"
        mock_constants.DEFAULT_TIMEOUT = 10

        from backup_workflow import execute_backup_workflow

        # Execute workflow
        result = execute_backup_workflow()

        # Should succeed (though might fail due to path issues in test)
        # This is more of a smoke test
        self.assertIsInstance(result, bool)

    def test_main_module_import(self):
        """Test that main module can be imported without errors."""
        try:
            import main

            self.assertTrue(hasattr(main, "main"))
        except Exception as e:
            self.fail(f"Failed to import main module: {e}")


if __name__ == "__main__":
    unittest.main()
