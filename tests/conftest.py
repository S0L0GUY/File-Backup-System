"""
Test configuration and fixtures for the backup system tests.
"""

import os
import tempfile
import shutil
import pytest
from unittest.mock import patch
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_files(temp_test_dir):
    """Create sample files for testing."""
    files = {}

    # Create some test files
    test_file1 = os.path.join(temp_test_dir, "test_file1.txt")
    with open(test_file1, "w") as f:
        f.write("This is test file 1")
    files["test_file1"] = test_file1

    test_file2 = os.path.join(temp_test_dir, "test_file2.txt")
    with open(test_file2, "w") as f:
        f.write("This is test file 2")
    files["test_file2"] = test_file2

    # Create a subdirectory with a file
    sub_dir = os.path.join(temp_test_dir, "subdir")
    os.makedirs(sub_dir)
    sub_file = os.path.join(sub_dir, "sub_file.txt")
    with open(sub_file, "w") as f:
        f.write("This is a file in subdirectory")
    files["sub_file"] = sub_file

    return files


@pytest.fixture
def mock_constants(temp_test_dir):
    """Mock constants for testing."""
    backup_dir = os.path.join(temp_test_dir, "backup")
    os.makedirs(backup_dir, exist_ok=True)

    with patch("constants.FileLocations") as mock_locations:
        mock_locations.ORIGINAL_FILE_LOCATIONS = [temp_test_dir]
        mock_locations.BACKUP_LOCATIONS = [backup_dir]
        mock_locations.BACKUP_FILE_NAME = "test_backup"
        mock_locations.DEFAULT_TIMEOUT = 10
        yield mock_locations
