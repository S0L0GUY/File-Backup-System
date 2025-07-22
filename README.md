# File Backup System

A robust, cross-platform file backup solution with intelligent change detection, comprehensive logging, and native system notifications. This system creates ZIP archives of your important files and maintains them across multiple backup locations automatically.

## 🚀 Features

- **Smart Backup Detection**: Uses SHA-256 hashing to detect file changes and only creates new backups when necessary
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Multiple Backup Locations**: Automatically maintains backups across multiple specified locations
- **Comprehensive Logging**: Detailed logging with rotating log files and console output
- **Native Notifications**: Desktop notifications on all supported platforms
- **Recursive File Processing**: Handles complex directory structures with intelligent filtering
- **Error Recovery**: Robust error handling with automatic cleanup
- **Temporary File Management**: Secure temporary directory handling with proper cleanup
- **Administrative Privileges**: Optional elevated permissions for accessing protected files

## 📁 Project Structure

```
File-Backup-System/
├── main.py                    # Entry point - orchestrates the backup process
├── backup_workflow.py         # Main workflow coordination and error handling
├── backup_manager.py          # ZIP creation, hash calculation, and backup management
├── file_operations.py         # File copying, directory traversal, and filtering
├── temp_manager.py           # Temporary directory creation and cleanup
├── notification_manager.py    # Cross-platform desktop notifications
├── logging_config.py         # Centralized logging configuration
├── constants.py              # Configuration constants and file paths
├── run.bat                   # Windows batch script for easy execution
└── logs/                     # Directory for log files (auto-created)
```

## 🛠 How It Works

### Backup Process Overview

1. **Initialization**: Sets up logging and creates a secure temporary directory
2. **File Collection**: Recursively copies files from source locations to temporary directory
3. **Archive Creation**: Creates a compressed ZIP file of all collected files
4. **Change Detection**: Calculates SHA-256 hash and compares with existing backups
5. **Backup Update**: Updates all backup locations if changes are detected
6. **Cleanup**: Removes temporary files and sends completion notification

### Key Components

#### `backup_workflow.py`
- Orchestrates the entire backup process
- Provides comprehensive error handling and recovery
- Manages logging operations and user notifications
- Handles graceful shutdown and cleanup

#### `backup_manager.py`
- Creates ZIP archives using optimal compression
- Calculates and compares SHA-256 file hashes
- Manages multiple backup locations
- Handles backup file versioning and updates

#### `file_operations.py`
- Recursively copies files while preserving directory structure
- Implements intelligent filtering (excludes .git, __pycache__, etc.)
- Handles permission errors and file access issues
- Provides detailed progress logging

#### `temp_manager.py`
- Creates secure temporary directories with proper permissions
- Handles cleanup with Windows-specific readonly file handling
- Manages temporary file lifecycle

#### `notification_manager.py`
- Sends native desktop notifications on all platforms
- Provides multiple fallback notification methods
- Handles platform-specific notification APIs

#### `logging_config.py`
- Configurable logging with file rotation (10MB files, 5 backups)
- Timestamped log files with structured formatting
- Console and file output with different log levels
- Context managers for operation logging

## ⚙️ Configuration

### Basic Setup

1. **Configure Source Locations** (`constants.py`):
   ```python
   ORIGINAL_FILE_LOCATIONS = [
       "C:/Users/YourName/Documents",
       "C:/Users/YourName/Pictures",
       "/path/to/important/files"
   ]
   ```

2. **Configure Backup Destinations** (`constants.py`):
   ```python
   BACKUP_LOCATIONS = [
       "C:/Backups",
       "D:/External_Backup"
   ]
   ```

3. **Customize Backup Name** (`constants.py`):
   ```python
   BACKUP_FILE_NAME = "my_backup"  # Creates "my_backup.zip"
   ```

## 🖥️ System Setup Instructions

### Windows Setup

#### Prerequisites
- Python 3.7 or higher
- Administrative privileges (recommended for accessing all files)

#### Method 1: Manual Execution
1. **Clone or download the repository**
2. **Configure paths** in `constants.py`
3. **Run directly**:
   ```cmd
   python main.py
   ```
4. **Or use the batch file** (runs with admin privileges):
   ```cmd
   run.bat
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
     - Arguments: `main.py`
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
python3 main.py
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
           <string>/path/to/File-Backup-System/main.py</string>
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
*/30 * * * * cd /path/to/File-Backup-System && /usr/local/bin/python3 main.py

# Or daily at 2 AM
0 2 * * * cd /path/to/File-Backup-System && /usr/local/bin/python3 main.py
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
python3 main.py
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
*/30 * * * * cd /path/to/File-Backup-System && /usr/bin/python3 main.py

# Daily at 3 AM
0 3 * * * cd /path/to/File-Backup-System && /usr/bin/python3 main.py
```

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
2025-07-22 14:21:15 - backup_system - INFO - Processing 1 source location(s)
2025-07-22 14:21:15 - backup_system - INFO - Successfully completed file population to temporary directory
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
- Adjust `DEFAULT_TIMEOUT` in `constants.py` for large files
- Consider excluding large, non-essential files

#### Network Backup Locations
- Ensure network paths are accessible and mounted
- Use UNC paths on Windows: `\\server\share\path`
- Consider authentication for network drives

### Performance Optimization

#### For Large Datasets
1. **Increase timeout values** in `constants.py`
2. **Use SSD storage** for temporary directory
3. **Schedule during off-peak hours**
4. **Exclude unnecessary file types** in `ignore_patterns()`

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
- Configure log retention policies based on privacy requirements
- Consider log file encryption for sensitive environments

## 🔄 Maintenance

### Regular Tasks
1. **Monitor log files** for errors and warnings
2. **Check backup integrity** periodically
3. **Review disk space** in backup locations
4. **Update source/destination paths** as needed
5. **Test restore procedures** regularly

### Updates
- Keep Python installation updated
- Review and update ignore patterns
- Adjust timing based on data change patterns
- Monitor system performance impact

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