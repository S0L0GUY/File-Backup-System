"""
Simple tests for backup manager functionality.
"""

import unittest


class TestBackupManagerSimple(unittest.TestCase):
    """Simple test cases for backup manager."""

    def test_backup_manager_import(self):
        """Test that backup_manager can be imported."""
        try:
            import backup_manager

            self.assertTrue(hasattr(backup_manager, "zip_temp_hold"))
            self.assertTrue(hasattr(backup_manager, "calculate_file_hash"))
        except ImportError as e:
            self.fail(f"Failed to import backup_manager: {e}")

    def test_hash_calculation_method_exists(self):
        """Test that hash calculation function exists."""
        from backup_manager import calculate_file_hash

        self.assertTrue(callable(calculate_file_hash))


if __name__ == "__main__":
    unittest.main()
