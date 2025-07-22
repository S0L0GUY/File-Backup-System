import subprocess
import platform
import shutil
from constants import FileLocations


def send_notification(title, message):
    """Send a native notification based on the operating system."""
    system = platform.system().lower()

    if system == "windows":
        _send_windows_notification(title, message)
    elif system == "darwin":
        _send_macos_notification(title, message)
    elif system == "linux":
        _send_linux_notification(title, message)
    else:
        print(f"Unsupported operating system: {system}")
        print(f"Notification: {title} - {message}")


def _send_windows_notification(title, message):
    """Send a native Windows toast notification using PowerShell."""
    try:
        powershell_command = f'''
        if (Get-Module -ListAvailable -Name BurntToast) {{
            Import-Module BurntToast
            New-BurntToastNotification -Text "{title}", "{message}" -Silent
        }} else {{
            # Fallback to system tray balloon (older but more reliable)
            Add-Type -AssemblyName System.Windows.Forms
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::Information
            $notification.BalloonTipIcon = `
                [System.Windows.Forms.ToolTipIcon]::Info
            $notification.BalloonTipText = "{message}"
            $notification.BalloonTipTitle = "{title}"
            $notification.Visible = $true
            $notification.ShowBalloonTip(5000)
            Start-Sleep -Seconds 1
            $notification.Dispose()
        }}
        '''
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-Command", powershell_command],
            capture_output=True,
            text=True,
            timeout=FileLocations.DEFAULT_TIMEOUT
        )

        if result.returncode != 0:
            escaped_title = title.replace('"', '`"').replace("'", "`'")
            escaped_message = message.replace('"', '`"').replace("'", "`'")
            msg_cmd = (f'[System.Windows.Forms.MessageBox]::Show('
                       f'"{escaped_message}", "{escaped_title}")')
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", msg_cmd],
                timeout=FileLocations.DEFAULT_TIMEOUT
            )

    except Exception as e:
        print(f"Failed to send Windows notification: {e}")


def _send_macos_notification(title, message):
    """Send a native macOS notification using osascript."""
    try:
        title_escaped = title.replace('"', '\\"')
        message_escaped = message.replace('"', '\\"')

        applescript = f'''
        display notification "{message_escaped}" with title "{title_escaped}"
        '''

        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"osascript error: {result.stderr}")
            print(f"Notification: {title} - {message}")

    except Exception as e:
        print(f"Failed to send macOS notification: {e}")


def _send_linux_notification(title, message):
    """Send a native Linux notification using notify-send or zenity."""
    try:
        if shutil.which("notify-send"):
            result = subprocess.run(
                ["notify-send", title, message],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return

        if shutil.which("zenity"):
            result = subprocess.run(
                ["zenity", "--info", "--title", title, "--text", message],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return

        if shutil.which("kdialog"):
            result = subprocess.run(
                ["kdialog", "--title", title, "--passivepopup", message, "5"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return

        print("No notification system found.")
        print(f"Notification: {title} - {message}")

    except Exception as e:
        print(f"Failed to send Linux notification: {e}")
