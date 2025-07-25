# File Backup System


A robust, cross-platform file backup solution with intelligent change detection, comprehensive logging, and native system notifications. This modular system creates ZIP archives of your important files and maintains them across multiple backup locations automatically.

## ✨ Features

- **Smart Backup Detection**: Uses optimized SHA-256 hashing to detect file changes and only creates new backups when necessary
- **High Performance**: Optimized hashing with adaptive buffering, memory mapping, and parallel processing for 25-50% faster backups
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Multiple Backup Locations**: Automatically maintains backups across multiple specified locations
- **Comprehensive Logging**: Advanced logging with rotating log files and detailed operation tracking
- **Native Notifications**: Desktop notifications on all supported platforms with fallback mechanisms
- **Error Recovery**: Robust error handling with automatic cleanup and graceful failure management
- **Modular Architecture**: Clean separation of concerns with dedicated modules for each function
- **Configurable Performance**: Tunable threading, buffer sizes, and memory mapping for optimal system resource usage

## 📁 Project Structure

```
File-Backup-System/
├── src/                       # Main source code directory
│   ├── main.py               # Entry point
│   ├── backup_workflow.py    # Main workflow coordination
│   ├── backup_manager.py     # ZIP creation and backup management
│   ├── file_operations.py    # File operations and filtering
│   ├── temp_manager.py       # Temporary directory management
│   ├── notification_manager.py # Cross-platform notifications
│   ├── logging_config.py     # Logging configuration
│   └── constants.py          # Configuration constants
├── tests/                    # Unit tests and integration tests
├── scripts/                  # Utility scripts
├── logs/                     # Log files (auto-created)
├── pyproject.toml           # Python project configuration
└── requirements.txt         # Dependencies
```

## 🚀 Quick Start

1. **Clone the repository**
2. **Configure paths in `src/constants.py`**:
   ```python
   class FileLocations:
       ORIGINAL_FILE_LOCATIONS = [
           "C:/Users/YourName/Documents",
           "C:/Users/YourName/Pictures"
       ]
       BACKUP_LOCATIONS = [
           "C:/Backups",
           "D:/External_Backup"
       ]
   ```
3. **Run the backup**:
   ```bash
   python src/main.py
   ```

## 🖥️ Platform Setup

### Windows
- **Manual**: `python src/main.py` or use `scripts/run.bat`
- **Scheduled**: Use Task Scheduler for automatic backups
- **Prerequisites**: Python 3.7+, optional admin privileges

### macOS
- **Manual**: `python3 src/main.py`
- **Scheduled**: Use Launchd or cron
- **Prerequisites**: Python 3, built-in notification support

### Linux
- **Manual**: `python3 src/main.py`
- **Scheduled**: Use systemd or cron
- **Prerequisites**: Python 3, `libnotify-bin`, `zenity`

### Linux Systemd Service

1. **Create service file** (`/etc/systemd/system/filebackup.service`):
   ```ini
   [Unit]
   Description=File Backup System
   After=network.target

   [Service]
   Type=simple
   User=yourusername
   WorkingDirectory=/path/to/File-Backup-System
   ExecStart=/usr/bin/python3 /path/to/File-Backup-System/src/main.py
   Restart=no

   [Install]
   WantedBy=multi-user.target
   ```

2. **Create timer** (`/etc/systemd/system/filebackup.timer`):
   ```ini
   [Unit]
   Description=Run File Backup System every 30 minutes

   [Timer]
   OnBootSec=5min
   OnUnitActiveSec=30min

   [Install]
   WantedBy=timers.target
   ```

3. **Enable and start**:
   ```bash
   sudo systemctl enable filebackup.timer
   sudo systemctl start filebackup.timer
   ```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src
```

## 📊 Monitoring

- **Log Location**: `logs/` directory
- **Log Format**: `backup_system_YYYYMMDD_HHMMSS.log`
- **Log Rotation**: 10MB files, keeps 5 backups
- **Log Levels**: INFO, DEBUG, WARNING, ERROR

## 🚨 Troubleshooting

### Common Issues
- **Permission Errors**: Run as administrator (Windows) or check file permissions
- **Python Not Found**: Add Python to PATH or use full path
- **Notification Issues**: Install platform-specific notification tools

### Performance Tips
- Increase timeout values in `src/constants.py` for large files
- Use SSD storage for temporary directory
- Schedule during off-peak hours
- Exclude unnecessary files in `ignore_patterns()` function

## 🔧 Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Code formatting
black src/ tests/

# Type checking
mypy src/

# Security analysis
bandit -c bandit.yaml -r src/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

**Note**: This backup system is designed for personal use. For enterprise environments, consider additional features like encryption and incremental backups.

## 📁 Project Structure

```
File-Backup-System/
├── src/                       # Main source code directory
│   ├── main.py               # Entry point - simple workflow execution
│   ├── backup_workflow.py    # Main workflow coordination and error handling
│   ├── backup_manager.py     # ZIP creation, hash calculation, and backup management
│   ├── file_operations.py    # File copying, directory traversal, and filtering
│   ├── temp_manager.py       # Temporary directory creation and cleanup
│   ├── notification_manager.py # Cross-platform desktop notifications
│   ├── logging_config.py     # Advanced logging configuration with rotation
│   └── constants.py          # Configuration constants and file paths
├── tests/                    # Unit tests and integration tests
├── scripts/                  # Utility scripts
│   ├── run.bat              # Windows batch script for easy execution
│   └── run_tests.py         # Test runner script
├── logs/                     # Directory for log files (auto-created)
├── pyproject.toml           # Python project configuration
├── requirements.txt         # Production dependencies
└── requirements-dev.txt     # Development dependencies
```

## 🛠 How It Works

### Backup Process Overview

1. **Initialization**: Sets up comprehensive logging with rotating files and creates a secure temporary directory
2. **File Collection**: Recursively copies files from source locations to temporary directory with intelligent filtering
3. **Archive Creation**: Creates a compressed ZIP file of all collected files with detailed progress tracking
4. **Change Detection**: Calculates SHA-256 hash and compares with existing backups across all locations
5. **Backup Update**: Updates all backup locations if changes are detected, with atomic operations
6. **Cleanup & Notification**: Removes temporary files, logs completion status, and sends desktop notification

### Key Components

#### `src/main.py` - Entry Point
- Simple entry point that delegates to the backup workflow
- Provides clean exit codes for automated systems
- Minimal error handling at the top level

#### `src/backup_workflow.py` - Workflow Orchestration
- Orchestrates the entire backup process with comprehensive error handling
- Provides structured logging with operation context managers
- Handles graceful shutdown, cleanup, and user interruptions (Ctrl+C)
- Manages success/failure notifications and final status reporting
- Uses the `LoggedOperation` context manager for automatic operation logging

#### `src/backup_manager.py` - Backup Operations
- Creates ZIP archives using optimal compression with detailed file tracking
- Calculates and compares SHA-256 file hashes for change detection
- Manages multiple backup locations with atomic updates
- Handles backup file versioning and integrity validation
- Provides detailed statistics on backup operations

#### `src/file_operations.py` - File System Operations
- Recursively copies files while preserving directory structure
- Implements intelligent filtering (excludes `.git`, `__pycache__`, system files)
- Handles permission errors and file access issues gracefully
- Provides detailed progress logging and error recovery
- Uses efficient file operations with proper error handling

#### `src/temp_manager.py` - Temporary File Management
- Creates secure temporary directories with proper permissions
- Handles cleanup with Windows-specific readonly file handling
- Manages temporary file lifecycle with automatic cleanup
- Provides safe directory operations with comprehensive error handling

#### `src/notification_manager.py` - Cross-Platform Notifications
- Sends native desktop notifications on all platforms with multiple fallback methods
- Windows: Uses PowerShell with BurntToast or system tray fallback
- macOS: Uses osascript (AppleScript) for native notifications
- Linux: Tries notify-send, zenity, or kdialog with graceful degradation
- Handles platform-specific notification APIs with error recovery

#### `src/logging_config.py` - Advanced Logging System
- Configurable logging with file rotation (10MB files, 5 backups)
- Timestamped log files with structured formatting and automatic cleanup
- Console and file output with different log levels and filtering
- Context managers (`LoggedOperation`) for automatic operation logging
- Decorator support for function-level logging and error tracking
- Centralized logger management with module-specific loggers

## ⚙️ Configuration

### Basic Setup

1. **Configure Source Locations** (`src/constants.py`):
   ```python
   class FileLocations:
       ORIGINAL_FILE_LOCATIONS = [
           "C:/Users/YourName/Documents",
           "C:/Users/YourName/Pictures",
           "/path/to/important/files"
       ]
   ```

2. **Configure Backup Destinations** (`src/constants.py`):
   ```python
   class FileLocations:
       BACKUP_LOCATIONS = [
           "C:/Backups",
           "D:/External_Backup"
       ]
   ```

3. **Customize Backup Name** (`src/constants.py`):
   ```python
   class FileLocations:
       BACKUP_FILE_NAME = "my_backup"  # Creates "my_backup.zip"
   ```

4. **Adjust Timeout Settings** (`src/constants.py`):
   ```python
   class FileLocations:
       DEFAULT_TIMEOUT = 10  # seconds for subprocess operations
   ```

## 🖥️ System Setup Instructions

### Windows Setup

#### Prerequisites
- Python 3.7 or higher
- Administrative privileges (recommended for accessing all files)

#### Method 1: Manual Execution
1. **Clone or download the repository**
2. **Configure paths** in `src/constants.py`
3. **Run directly**:
   ```cmd
   python src/main.py
   ```
4. **Or use the batch file** (runs with admin privileges):
   ```cmd
   scripts/run.bat
   ```

#### Method 2: Windows Task Scheduler (Recommended)

##### Basic Setup - Run Once Daily
1. **Open Task Scheduler** (`Win + R`, type `taskschd.msc`)
2. **Create Basic Task**:
   - Name: "File Backup System"
   - Trigger: Daily at desired time
   - Action: Start a program
   - Program: `python.exe`
   - Arguments: `main.py`
   - Start in: `C:\path\to\File-Backup-System`

##### Advanced Setup - Startup + Every 30 Minutes
For continuous backup protection with startup execution and regular intervals:

1. **Create New Task** (not Basic Task):
   - **General Tab**:
     - Name: "File Backup System - Continuous"
     - Check "Run with highest privileges"
     - Check "Run whether user is logged on or not"

   - **Triggers Tab** - Create TWO triggers:
     
     **Trigger 1: At Startup**
     - Click "New..."
     - Begin the task: "At startup"
     - Advanced settings: Check "Enabled"
     - Click "OK"
     
     **Trigger 2: Every 30 Minutes**
     - Click "New..." again
     - Begin the task: "On a schedule"
     - Settings: Select "Daily"
     - Recur every: 1 days
     - Start time: Set to a time shortly after typical startup (e.g., 8:00 AM)
     - Click "Advanced settings"
     - Check "Repeat task every" and set to "30 minutes"
     - For duration: Select "Indefinitely"
     - Check "Enabled"
     - Click "OK"

   - **Actions Tab**:
     - Program: `C:\path\to\python.exe`
     - Arguments: `src/main.py`
     - Start in: `C:\path\to\File-Backup-System`

   - **Conditions Tab**:
     - Uncheck "Start the task only if the computer is on AC power" (for laptops)
     - Check "Wake the computer to run this task" (optional)

   - **Settings Tab**:
     - Check "Allow task to be run on demand"
     - Check "If the running task does not end when requested, force it to stop"
     - "If the task is already running": "Do not start a new instance"

#### Method 3: Windows Service
For advanced users, consider using `python-windows-service` or `nssm` to run as a Windows service.

### macOS Setup

#### Prerequisites
```bash
# Install Python 3 if not already installed
brew install python3

# Optional: Install notification enhancements
# The system uses built-in osascript, no additional packages needed
```

#### Method 1: Manual Execution
```bash
cd /path/to/File-Backup-System
python3 src/main.py
```

#### Method 2: Launchd (macOS Service)
1. **Create a launch agent** (`~/Library/LaunchAgents/com.user.filebackup.plist`):
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
             "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.user.filebackup</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/local/bin/python3</string>
           <string>/path/to/File-Backup-System/src/main.py</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/path/to/File-Backup-System</string>
       <key>StartInterval</key>
       <integer>1800</integer> <!-- 30 minutes -->
       <key>RunAtLoad</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/tmp/filebackup.out</string>
       <key>StandardErrorPath</key>
       <string>/tmp/filebackup.err</string>
   </dict>
   </plist>
   ```

2. **Load the service**:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.user.filebackup.plist
   launchctl start com.user.filebackup
   ```

#### Method 3: Cron
```bash
# Edit crontab
crontab -e

# Add entry for every 30 minutes
*/30 * * * * cd /path/to/File-Backup-System && /usr/local/bin/python3 src/main.py

# Or daily at 2 AM
0 2 * * * cd /path/to/File-Backup-System && /usr/local/bin/python3 src/main.py
```

### Linux Setup

#### Prerequisites
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip libnotify-bin zenity

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip libnotify zenity
# or for newer versions:
sudo dnf install python3 python3-pip libnotify zenity

# Arch Linux
sudo pacman -S python python-pip libnotify zenity
```

#### Method 1: Manual Execution
```bash
cd /path/to/File-Backup-System
python3 src/main.py
```

#### Method 2: Systemd Service (Recommended)
1. **Create service file** (`/etc/systemd/system/filebackup.service`):
   ```ini
   [Unit]
   Description=File Backup System
   After=network.target

   [Service]
   Type=simple
   User=yourusername
   WorkingDirectory=/path/to/File-Backup-System
   ExecStart=/usr/bin/python3 /path/to/File-Backup-System/main.py
   Restart=no
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```

2. **Create timer for regular execution** (`/etc/systemd/system/filebackup.timer`):
   ```ini
   [Unit]
   Description=Run File Backup System every 30 minutes
   Requires=filebackup.service

   [Timer]
   OnBootSec=5min
   OnUnitActiveSec=30min
   Unit=filebackup.service

   [Install]
   WantedBy=timers.target
   ```

3. **Enable and start**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable filebackup.timer
   sudo systemctl start filebackup.timer
   
   # Check status
   sudo systemctl status filebackup.timer
   sudo systemctl status filebackup.service
   ```

#### Method 3: Cron
```bash
# Edit crontab
crontab -e

# Every 30 minutes
*/30 * * * * cd /path/to/File-Backup-System && /usr/bin/python3 src/main.py

# Daily at 3 AM
0 3 * * * cd /path/to/File-Backup-System && /usr/bin/python3 src/main.py
```

## 🧪 Testing

### Running Tests

The project includes comprehensive unit tests and integration tests:

```bash
# Run all tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=src

# Run specific test file
python -m pytest tests/test_backup_manager.py

# Use the test runner script
python scripts/run_tests.py
```

### Test Structure
- `tests/test_backup_manager.py` - Tests for backup operations
- `tests/test_constants.py` - Configuration validation tests
- `tests/test_integration.py` - End-to-end integration tests
- `tests/test_logging_config.py` - Logging system tests
- `tests/test_temp_manager.py` - Temporary file management tests

## 📊 Monitoring and Logs

### Log Files
- **Location**: `logs/` directory
- **Format**: `backup_system_YYYYMMDD_HHMMSS.log`
- **Rotation**: 10MB per file, keeps 5 backup files
- **Content**: Detailed operation logs, error messages, and performance metrics

### Log Levels
- **INFO**: Normal operation progress
- **DEBUG**: Detailed operation information
- **WARNING**: Non-critical issues
- **ERROR**: Operation failures and exceptions

### Sample Log Output
```
2025-07-22 14:21:12 - backup_system - INFO - ==================================================
2025-07-22 14:21:12 - backup_system - INFO - Starting File Backup System
2025-07-22 14:21:12 - backup_system - INFO - ==================================================
2025-07-22 14:21:12 - backup_system - INFO - Starting temporary directory creation...
2025-07-22 14:21:12 - backup_system - INFO - Successfully completed temporary directory creation
2025-07-22 14:21:12 - backup_system - INFO - Starting file population to temporary directory...
2025-07-22 14:21:15 - backup_system - INFO - Copy operation completed: 1 successful, 0 failed. Copied 42 files and 1 directories.
2025-07-22 14:21:15 - backup_system - INFO - Successfully completed file population to temporary directory
2025-07-22 14:21:15 - backup_system - INFO - Starting retrieving existing backup hashes...
2025-07-22 14:21:15 - backup_system - INFO - Found 2 existing backup(s)
2025-07-22 14:21:15 - backup_system - INFO - Successfully completed retrieving existing backup hashes
2025-07-22 14:21:15 - backup_system - INFO - Starting creating ZIP backup...
2025-07-22 14:21:16 - backup_system - INFO - ZIP archive created: 42 files, 15728640 bytes
2025-07-22 14:21:16 - backup_system - INFO - Successfully completed creating ZIP backup
```

## 🚨 Troubleshooting

### Common Issues

#### Permission Errors
- **Windows**: Run as administrator or use `run.bat`
- **macOS/Linux**: Ensure user has read access to source directories and write access to backup locations

#### Python Not Found
- **Windows**: Add Python to PATH or specify full path in scripts
- **macOS**: Use `python3` instead of `python`
- **Linux**: Install Python 3 using package manager

#### Notification Issues
- **Windows**: Install BurntToast module: `pip install BurntToast`
- **Linux**: Install notification tools: `sudo apt install libnotify-bin zenity`
- **macOS**: Notifications work out of the box with osascript

#### Large File Handling
- Monitor disk space in temporary directory location
- Adjust `DEFAULT_TIMEOUT` in `src/constants.py` for large files
- Consider excluding large, non-essential files in `ignore_patterns()` function
- Monitor temporary directory cleanup in logs for potential issues

#### Network Backup Locations
- Ensure network paths are accessible and mounted
- Use UNC paths on Windows: `\\server\share\path`
- Consider authentication for network drives

### Performance Optimization

#### For Large Datasets
1. **Increase timeout values** in `src/constants.py`
2. **Use SSD storage** for temporary directory
3. **Schedule during off-peak hours**
4. **Exclude unnecessary file types** in `ignore_patterns()` function in `src/file_operations.py`

#### Memory Usage
- The system processes files incrementally
- Memory usage scales with temporary directory size
- Monitor system resources during large backups

## 🔒 Security Considerations

### File Permissions
- Temporary directories are created with secure permissions
- Backup files inherit destination directory permissions
- Consider encrypting backup locations for sensitive data

### Network Security
- Use secure network protocols for remote backup locations
- Consider VPN for internet-based backup destinations
- Implement proper authentication for network shares

### Data Privacy
- Log files may contain file paths and system information
- Configure log retention policies based on privacy requirements using the rotating file handler settings
- Consider log file encryption for sensitive environments
- Review log levels to control information verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- Temporary directories are automatically cleaned up to prevent data leakage

## �️ Development

### Project Dependencies

The project uses modern Python development practices:

- **Production Dependencies**: Listed in `requirements.txt` (currently uses only standard library)
- **Development Dependencies**: Listed in `requirements-dev.txt` (testing frameworks, linting tools)
- **Project Configuration**: `pyproject.toml` with Black, pytest, and mypy configurations

### Code Quality Tools

- **Black**: Code formatting with 88-character line length
- **pytest**: Testing framework with comprehensive test coverage
- **mypy**: Type checking for better code reliability
- **Bandit**: Security analysis (configuration in `bandit.yaml`)

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run code formatting
black src/ tests/

# Run type checking
mypy src/

# Run security analysis
bandit -c bandit.yaml -r src/

# Run all tests with coverage
python -m pytest tests/ --cov=src
```

## �🔄 Maintenance

### Regular Tasks
1. **Monitor log files** in the `logs/` directory for errors and warnings
2. **Check backup integrity** by verifying ZIP files can be opened and extracted
3. **Review disk space** in backup locations and temporary directory
4. **Update source/destination paths** in `src/constants.py` as needed
5. **Test restore procedures** regularly by extracting backup files
6. **Review ignored file patterns** in `src/file_operations.py` based on new file types

### Updates and Upgrades
- Keep Python installation updated to latest stable version
- Review and update ignore patterns for new system files or build artifacts
- Adjust logging levels and rotation settings based on usage patterns
- Monitor system performance impact and adjust timing intervals accordingly
- Update notification settings based on changes in operating system APIs

## 🏗️ Architecture Highlights

### Modular Design
The system is built with a clean separation of concerns:
- **`main.py`**: Simple entry point with minimal logic
- **`backup_workflow.py`**: Orchestrates the entire process with comprehensive error handling
- **Specialized modules**: Each handles a specific aspect (files, backups, notifications, logging, temp management)
- **Configuration centralization**: All settings in `constants.py` for easy management

### Advanced Error Handling
- **Graceful degradation**: System continues operating when non-critical components fail
- **Comprehensive logging**: All operations logged with context and error details
- **Automatic cleanup**: Temporary files cleaned up even when operations fail
- **User interruption handling**: Clean shutdown on Ctrl+C with proper cleanup
- **Notification fallbacks**: Multiple notification methods with graceful fallback to console output

### Logging Architecture
- **Rotating logs**: Automatic log rotation (10MB files, 5 backups) prevents disk space issues
- **Structured logging**: Consistent formatting with timestamps and operation context
- **Module-specific loggers**: Detailed tracking of which component generated each log entry
- **Operation context managers**: Automatic start/success/failure logging for major operations
- **Debug support**: Detailed debug logging for troubleshooting without overwhelming normal logs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Update documentation as needed
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review log files for detailed error information
3. Create an issue in the repository with:
   - Operating system and version
   - Python version
   - Complete error messages
   - Relevant log file excerpts

---

**Note**: This backup system is designed for personal use. For enterprise environments, consider additional features like encryption, incremental backups, and centralized management.