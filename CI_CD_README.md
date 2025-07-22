# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the File Backup System.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` branch
- Manual workflow dispatch

## Pipeline Jobs

### 1. Code Quality & Linting (`lint`)
- **Purpose**: Ensures code quality and consistency
- **Tools Used**:
  - `flake8`: Python linting and style checking
  - `black`: Code formatting verification
  - `mypy`: Static type checking (optional)
- **Runs on**: Ubuntu Latest, Python 3.11

### 2. Test Suite (`test`)
- **Purpose**: Validates functionality across multiple environments
- **Matrix Strategy**:
  - **OS**: Ubuntu Latest, Windows Latest
  - **Python**: 3.9, 3.10, 3.11, 3.12
- **Features**:
  - Unit tests with pytest
  - Code coverage reporting
  - Coverage upload to Codecov (Ubuntu + Python 3.11 only)

### 3. Security Scan (`security`)
- **Purpose**: Identifies potential security vulnerabilities
- **Tool**: `bandit` - Python security linter
- **Output**: Security report artifact
- **Runs on**: Ubuntu Latest, Python 3.11

### 4. Build Validation (`build`)
- **Purpose**: Validates that the application can be built and imported
- **Tests**:
  - Module import verification
  - Distribution package creation
- **Dependencies**: Requires `lint` and `test` jobs to pass
- **Runs on**: Ubuntu Latest, Python 3.11

### 5. Documentation (`docs`)
- **Purpose**: Validates documentation completeness
- **Checks**:
  - README.md existence
  - Inline docstring coverage
- **Runs on**: Ubuntu Latest

### 6. Release (`release`)
- **Purpose**: Creates releases for main branch pushes
- **Triggers**: 
  - Push to `main` branch
  - Commit message contains `[release]`
- **Dependencies**: All other jobs must pass
- **Actions**:
  - Generates release notes from git history
  - Creates GitHub release with auto-generated tag

## Local Testing

Before pushing to the repository, you can run tests locally:

### Python Script (Cross-platform)
```bash
python run_tests.py
```

### Windows Batch Script
```cmd
run_tests.bat
```

### Manual Commands
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 .

# Check formatting
black --check .

# Run tests
python -m pytest test_files/ -v

# Test imports
python -c "import main; print('Success')"
```

## Configuration Files

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Main CI/CD pipeline definition |
| `requirements.txt` | Production dependencies |
| `requirements-dev.txt` | Development and testing dependencies |
| `.flake8` | Flake8 linter configuration |
| `pyproject.toml` | Black, pytest, mypy, and coverage configuration |
| `bandit.yaml` | Security scan configuration |

## Test Structure

```
test_files/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_constants.py        # Tests for constants module
├── test_temp_manager.py     # Tests for temp_manager module
├── test_backup_manager.py   # Tests for backup_manager module
├── test_logging_config.py   # Tests for logging configuration
└── test_integration.py      # Integration tests
```

## Coverage Reporting

- **Tool**: `pytest-cov`
- **Target**: 80%+ code coverage
- **Reports**: 
  - Terminal output during test runs
  - XML report uploaded to Codecov
  - Coverage badge available in repository

## Security Scanning

- **Tool**: Bandit
- **Scope**: All Python files except tests
- **Output**: JSON report available as CI artifact
- **Exclusions**: Test files, virtual environments

## Troubleshooting

### Common CI Failures

1. **Linting Failures**
   - Run `black .` to fix formatting
   - Check flake8 output for style violations

2. **Test Failures**
   - Run tests locally: `python -m pytest test_files/ -v`
   - Check for platform-specific issues (Windows vs Linux)

3. **Import Errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check for missing `__init__.py` files

4. **Security Scan Issues**
   - Review bandit report in CI artifacts
   - Add exclusions to `bandit.yaml` if false positives

### Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd File-Backup-System

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
python run_tests.py
```

## Badges

Add these badges to your README.md:

```markdown
![CI Status](https://github.com/S0L0GUY/File-Backup-System/workflows/CI/CD%20Pipeline/badge.svg)
[![codecov](https://codecov.io/gh/S0L0GUY/File-Backup-System/branch/main/graph/badge.svg)](https://codecov.io/gh/S0L0GUY/File-Backup-System)
```

## Future Enhancements

- [ ] Add integration tests with real file operations
- [ ] Implement deployment to PyPI for releases
- [ ] Add performance benchmarking
- [ ] Implement automated security dependency updates
- [ ] Add code quality gates based on coverage thresholds
