# File Backup System

A Python-based automated backup solution that creates ZIP archives of specified directories and maintains multiple backup copies across different locations. The system uses hash comparison to detect changes and only updates backups when necessary.

## Features

- **Automated File Backup**: Recursively backs up specified directories
- **Hash-Based Change Detection**: Only updates backups when file contents change
- **Multiple Backup Locations**: Maintains copies across multiple storage locations
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Native Notifications**: Sends system notifications on all supported platforms
- **Windows Integration**: Includes batch file for easy execution with admin privileges
- **Smart Filtering**: Excludes system files like `.git` and `__pycache__` directories
- **Temporary File Management**: Uses temporary directories for safe processing

## System Requirements

- **Operating System**: 
  - Windows (with PowerShell support)
  - macOS (with osascript support)
  - Linux (with notify-send, zenity, or kdialog)
- **Python**: Python 3.6 or higher
- **Permissions**: Administrator/sudo privileges (for accessing system directories)
- **Dependencies**: No external Python packages required (uses only standard library)

### Platform-Specific Notification Requirements

#### Windows
- **Default**: Uses PowerShell for system tray notifications
- **Enhanced**: Install BurntToast module for better toast notifications:
  ```powershell
  Install-Module -Name BurntToast
  ```

#### macOS
- **Default**: Uses osascript (AppleScript) for native notifications
- **Requirements**: No additional setup needed

#### Linux
- **Ubuntu/Debian**: Install libnotify for notify-send:
  ```bash
  sudo apt-get install libnotify-bin
  ```
- **CentOS/RHEL**: 
  ```bash
  sudo yum install libnotify
  ```
- **Alternative**: Works with zenity or kdialog if available

## Installation and Setup

### 1. Download the Project
```bash
git clone https://github.com/S0L0GUY/File-Backup-System.git
cd File-Backup-System
```

### 2. Configure Backup Settings

Edit the `constants.py` file to customize your backup configuration:

```python
class FileLocations:
    # Directories to backup (add your source directories here)
    ORIGINAL_FILE_LOCATIONS = ["C:/Users/world/Downloads"]
    
    # Where to store backup copies (add your backup destinations)
    BACKUP_LOCATIONS = ["C:/"]
    
    # Temporary processing directory
    TEMPORARY_HOLD_FILE_PATH = "C:/temp_hold"
    
    # Name of the backup ZIP file
    BACKUP_FILE_NAME = "backup"
```

**Important Configuration Notes:**
- `ORIGINAL_FILE_LOCATIONS`: List of directories you want to back up
- `BACKUP_LOCATIONS`: List of directories where backup ZIP files will be stored
- `TEMPORARY_HOLD_FILE_PATH`: Temporary directory for processing (will be created/cleaned automatically)
- `BACKUP_FILE_NAME`: Name of the ZIP file (without extension)

### 3. Test the Backup System

Run the system manually to ensure everything works:

```bash
python main.py
```

Or use the provided batch file (runs with admin privileges):
```bash
run.bat
```

## Setting Up Automatic Startup on Windows

### Method 1: Windows Task Scheduler (Recommended)

1. **Open Task Scheduler**:
   - Press `Win + R`, type `taskschd.msc`, and press Enter
   - Or search for "Task Scheduler" in the Start menu

2. **Create a New Task**:
   - Click "Create Task..." in the Actions panel
   - Name: "File Backup System"
   - Description: "Automated file backup using Python script"
   - Check "Run with highest privileges"
   - Check "Run whether user is logged on or not"

3. **Configure Triggers**:
   - Go to the "Triggers" tab, click "New..."
   - Begin the task: "At startup" or "At log on"
   - For daily backups: Select "Daily" and set your preferred time
   - **For startup + recurring every 30 minutes**: See detailed instructions below
   - Advanced settings: Check "Enabled"

4. **Configure Actions**:
   - Go to the "Actions" tab, click "New..."
   - Action: "Start a program"
   - Program/script: `C:\path\to\your\File-Backup-System\run.bat`
   - Start in: `C:\path\to\your\File-Backup-System\`

5. **Configure Conditions** (Optional):
   - Go to the "Conditions" tab
   - Uncheck "Start the task only if the computer is on AC power" for laptops
   - Check "Wake the computer to run this task" if needed

6. **Configure Settings**:
   - Go to the "Settings" tab
   - Check "Allow task to be run on demand"
   - If task fails, restart every: 1 minute, attempt restart up to: 3 times

### Special Configuration: Startup + Every 30 Minutes

To run the backup on startup and then every 30 minutes thereafter, you'll need to create **two triggers** in the same task:

#### Trigger 1: At Startup
1. In the "Triggers" tab, click "New..."
2. Begin the task: **"At startup"**
3. Advanced settings: Check "Enabled"
4. Click "OK"

#### Trigger 2: Every 30 Minutes (All Day)
1. Click "New..." again to create a second trigger
2. Begin the task: **"On a schedule"**
3. Settings: Select **"Daily"**
4. Recur every: **1 days**
5. Start time: Set to a time shortly after typical startup (e.g., 8:00 AM)
6. Click **"Advanced settings"**
7. Check **"Repeat task every"** and set to **"30 minutes"**
8. For duration: Select **"Indefinitely"** or **"24 hours"**
9. Check "Enabled"
10. Click "OK"

#### Alternative: PowerShell Script Method

If you prefer more control, create a PowerShell script that handles the scheduling:

1. **Create `backup_scheduler.ps1`**:
```powershell
# Run backup immediately on startup
& "C:\path\to\your\File-Backup-System\run.bat"

# Then run every 30 minutes indefinitely
while ($true) {
    Start-Sleep -Seconds 1800  # 30 minutes = 1800 seconds
    & "C:\path\to\your\File-Backup-System\run.bat"
}
```

2. **Create Task Scheduler entry for PowerShell script**:
   - Program/script: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\path\to\your\backup_scheduler.ps1"`
   - Trigger: "At startup"

### Method 2: Windows Startup Folder (Simple Startup Only)

**Note**: This method only runs the backup once at startup. For recurring 30-minute intervals, use Task Scheduler instead.

1. **Open Startup Folder**:
   ```
   Win + R → shell:startup → Enter
   ```

2. **Create Shortcut**:
   - Right-click in the startup folder
   - New → Shortcut
   - Location: `C:\path\to\your\File-Backup-System\run.bat`
   - Name: "File Backup System"

### Method 3: Windows Registry (Advanced Users - Startup Only)

**Note**: This method only runs the backup once at startup. For recurring intervals, use Task Scheduler.

1. **Open Registry Editor**:
   ```
   Win + R → regedit → Enter
   ```

2. **Navigate to**:
   ```
   HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
   ```

3. **Add New String Value**:
   - Name: `FileBackupSystem`
   - Value: `C:\path\to\your\File-Backup-System\run.bat`

### Method 4: Create a Custom Windows Service (Advanced)

For the most robust solution that runs on startup and every 30 minutes, you can create a Windows service:

1. **Install Python service wrapper** (if desired):
```bash
pip install pywin32
```

2. **Create `backup_service.py`**:
```python
import time
import subprocess
import os
import sys

def run_backup():
    """Run the backup script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    run_bat = os.path.join(script_dir, "run.bat")
    subprocess.run([run_bat], shell=True)

def main():
    """Main service loop"""
    # Run immediately on service start
    run_backup()
    
    # Then run every 30 minutes
    while True:
        time.sleep(1800)  # 30 minutes
        run_backup()

if __name__ == "__main__":
    main()
```

3. **Use Task Scheduler to run the service script**:
   - Create task with trigger "At startup"
   - Action: Start program `python.exe`
   - Arguments: `C:\path\to\your\backup_service.py`

## How the Code Works

### Architecture Overview

The system is organized into five main modules:

```
File-Backup-System/
├── main.py                  # Main execution flow
├── constants.py             # Configuration settings
├── file_operations.py       # File handling operations
├── backup_manager.py        # Backup creation and management
├── notification_manager.py  # Cross-platform notifications
└── run.bat                 # Windows batch launcher
```

### Detailed Code Flow

#### 1. Main Execution (`main.py`)

The main function orchestrates the entire backup process:

```python
def main():
    # 1. Create temporary directory
    create_temp_path()
    
    # 2. Copy files to temporary location
    populate_temp_hold()
    
    # 3. Get hashes of existing backups
    existing_backup_hashes = get_existing_backup_hashes()
    
    # 4. Create ZIP of temporary files
    zipped_backup = zip_temp_hold()
    
    # 5. Calculate hash of new backup
    new_backup_hash = calculate_file_hash(zipped_backup)
    
    # 6. Compare hashes and update if needed
    if not all_hashes_match(existing_backup_hashes, new_backup_hash):
        update_all_backups(zipped_backup)
    
    # 7. Clean up temporary files
    cleanup_temp_files()
```

#### 2. File Operations (`file_operations.py`)

Handles all file system operations:

- **`create_temp_path()`**: Creates the temporary directory, cleaning up any existing one
- **`populate_temp_hold()`**: Recursively copies source files to temporary directory
- **`ignore_patterns()`**: Filters out unwanted files/directories (`.git`, `__pycache__`, etc.)
- **`cleanup_temp_files()`**: Removes temporary directory and handles Windows permission issues
- **`handle_remove_readonly()`**: Resolves Windows read-only file deletion issues

#### 3. Backup Management (`backup_manager.py`)

Manages backup creation and verification:

- **`zip_temp_hold()`**: Creates ZIP archive from temporary directory
- **`get_existing_backup_hashes()`**: Calculates hashes of existing backup files
- **`calculate_file_hash()`**: Computes hash of a single file
- **`all_hashes_match()`**: Compares new backup hash with existing ones
- **`update_all_backups()`**: Copies new backup to all specified locations

#### 4. Cross-Platform Notifications (`notification_manager.py`)

Provides native notifications across different operating systems:

- **`send_notification()`**: Main function that detects OS and routes to appropriate handler
- **`_send_windows_notification()`**: Uses PowerShell with BurntToast or system tray fallback
- **`_send_macos_notification()`**: Uses osascript (AppleScript) for native macOS notifications
- **`_send_linux_notification()`**: Tries notify-send, zenity, or kdialog in order

**Platform Detection:**
- Automatically detects the operating system using `platform.system()`
- Gracefully falls back to console output if no notification system is available
- Handles special characters and escaping for each platform

#### 5. Configuration (`constants.py`)

Centralizes all configuration in the `FileLocations` class:
- Source directories to backup
- Destination directories for backups
- Temporary processing directory
- Backup file naming

#### 6. Windows Launcher (`run.bat`)

Provides Windows integration:
- Checks for administrator privileges
- Automatically elevates permissions if needed
- Changes to script directory before execution
- Launches Python script

### Hash-Based Change Detection

The system uses Python's built-in `hash()` function to detect changes:

1. **On startup**: Calculate hashes of all existing backup files
2. **After creating new backup**: Calculate hash of the new ZIP file
3. **Comparison**: Only update backups if hashes don't match
4. **Efficiency**: Avoids unnecessary copying when files haven't changed

### Error Handling and Edge Cases

- **Permission Issues**: Uses `handle_remove_readonly()` for Windows file permissions
- **Missing Directories**: Checks existence before operations
- **File Conflicts**: Overwrites existing backups when updates are needed
- **Admin Rights**: Batch file automatically requests elevation

## Usage Examples

### Basic Usage
```bash
# Run backup once
python main.py

# Run with admin privileges (Windows)
run.bat
```

### Customization Examples

**Backup multiple directories**:
```python
ORIGINAL_FILE_LOCATIONS = [
    "C:/Users/world/Documents",
    "C:/Users/world/Desktop", 
    "C:/Users/world/Pictures"
]
```

**Multiple backup destinations**:
```python
BACKUP_LOCATIONS = [
    "D:/Backups",
    "E:/BackupDrive", 
    "//NetworkDrive/Backups"
]
```

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**:
   - Run as Administrator
   - Use the provided `run.bat` file
   - Check file/directory permissions

2. **Python Not Found**:
   - Ensure Python is installed and in PATH
   - Use full path to Python executable in batch file

3. **Backup Not Updating**:
   - Check if source files actually changed
   - Verify backup locations are writable
   - Check disk space

4. **Task Scheduler Not Working**:
   - Verify task runs with highest privileges
   - Check "Run whether user is logged on or not"
   - Test the batch file manually first

5. **30-Minute Recurring Backups Not Working**:
   - Ensure both triggers are properly configured in Task Scheduler
   - Check that "Repeat task every 30 minutes" is set with "Indefinitely" duration
   - Verify the task isn't being blocked by power settings
   - Check Windows Event Viewer for task execution logs

6. **High System Resource Usage**:
   - Consider increasing the interval if 30 minutes is too frequent
   - Monitor disk I/O during backup operations
   - Exclude unnecessary large directories from backup

### Logs and Debugging

The system provides console output for each step:
```
Creating temporary file directory...
Populating temporary hold with files...
Retrieving existing backup hashes...
Zipping temporary hold files...
Calculating new backup hash...
Checking if existing backups match the new backup hash...
```

**To monitor scheduled backups**:
- Check Windows Event Viewer: `Windows Logs > Application`
- Look for Task Scheduler entries related to your backup task
- Enable task history in Task Scheduler for detailed execution logs

## Security Considerations

- **Admin Privileges**: Required for accessing system directories
- **File Permissions**: Handles Windows read-only files appropriately
- **Temporary Files**: Automatically cleaned up after each run
- **Network Paths**: Supported for network backup locations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on Windows
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.