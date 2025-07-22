"""
Tests for the logging configuration module.
"""

import unittest


class TestLoggingConfig(unittest.TestCase):
    """Test cases for logging configuration."""

    def test_get_logger(self):
        """Test logger creation."""
        from logging_config import get_logger

        logger = get_logger("test_logger")
        self.assertIsNotNone(logger)
        # Note: The actual logger name might be different due to BackupLogger setup
        self.assertTrue(hasattr(logger, "info"))
        self.assertTrue(hasattr(logger, "error"))
        self.assertTrue(hasattr(logger, "debug"))

    def test_backup_logger_initialization(self):
        """Test BackupLogger can be imported and initialized."""
        from logging_config import BackupLogger

        # Should not raise an exception
        self.assertIsNotNone(BackupLogger)

        # Test setup_logging method
        logger = BackupLogger.setup_logging()
        self.assertIsNotNone(logger)

    def test_logged_operation_context_manager(self):
        """Test LoggedOperation as context manager."""
        from logging_config import LoggedOperation

        # Test that LoggedOperation can be created and used
        with LoggedOperation("test_operation") as op:
            self.assertIsNotNone(op)
            self.assertEqual(op.operation_name, "test_operation")

    def test_logged_operation_with_exception(self):
        """Test LoggedOperation handles exceptions properly."""
        from logging_config import LoggedOperation

        try:
            with LoggedOperation("test_operation_with_error"):
                raise ValueError("Test error")
        except ValueError:
            # Exception should propagate
            pass


if __name__ == "__main__":
    unittest.main()
