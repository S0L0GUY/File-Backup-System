"""
Cross-platform notification manager for the backup system.
Handles sending native notifications on Windows, macOS, and Linux systems.
"""

import subprocess
import platform
import shutil
from constants import FileLocations
from logging_config import get_logger


def send_notification(title, message):
    """
    Send a native notification based on the operating system.

    Args:
        title (str): The title of the notification
        message (str): The message content of the notification

    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    logger = get_logger("notification_manager.send_notification")

    try:
        system = platform.system().lower()
        logger.debug(f"Sending notification on {system}: {title}")

        if system == "windows":
            return _send_windows_notification(title, message)
        elif system == "darwin":
            return _send_macos_notification(title, message)
        elif system == "linux":
            return _send_linux_notification(title, message)
        else:
            logger.warning(f"Unsupported operating system: {system}")
            logger.info(f"Notification: {title} - {message}")
            return False

    except Exception as e:
        logger.error(f"Error sending notification: {e}", exc_info=True)
        logger.info(f"Fallback notification: {title} - {message}")
        return False


def _send_windows_notification(title, message):
    """
    Send a native Windows toast notification using PowerShell.

    Args:
        title (str): The title of the notification
        message (str): The message content of the notification

    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    logger = get_logger("notification_manager._send_windows_notification")

    try:
        logger.debug("Attempting to send Windows notification...")

        powershell_command = f"""
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
        """

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_command,
            ],
            capture_output=True,
            text=True,
            timeout=FileLocations.DEFAULT_TIMEOUT,
        )

        if result.returncode == 0:
            logger.debug("Windows notification sent successfully")
            return True
        else:
            logger.warning(f"PowerShell notification failed: {result.stderr}")

            # Fallback to message box
            logger.debug("Trying fallback message box...")
            escaped_title = title.replace('"', '`"').replace("'", "`'")
            escaped_message = message.replace('"', '`"').replace("'", "`'")
            msg_cmd = (
                f"[System.Windows.Forms.MessageBox]::Show("
                f'"{escaped_message}", "{escaped_title}")'
            )

            fallback_result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", msg_cmd],
                timeout=FileLocations.DEFAULT_TIMEOUT,
                capture_output=True,
            )

            if fallback_result.returncode == 0:
                logger.debug("Fallback message box sent successfully")
                return True
            else:
                logger.error("Both notification methods failed")
                return False

    except subprocess.TimeoutExpired:
        logger.error("Windows notification timed out")
        return False
    except Exception as e:
        logger.error(f"Failed to send Windows notification: {e}")
        return False


def _send_macos_notification(title, message):
    """
    Send a native macOS notification using osascript.

    Args:
        title (str): The title of the notification
        message (str): The message content of the notification

    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    logger = get_logger("notification_manager._send_macos_notification")

    try:
        logger.debug("Attempting to send macOS notification...")

        title_escaped = title.replace('"', '\\"')
        message_escaped = message.replace('"', '\\"')

        applescript = f"""
        display notification "{message_escaped}" with title "{title_escaped}"
        """

        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            logger.debug("macOS notification sent successfully")
            return True
        else:
            logger.error(f"osascript error: {result.stderr}")
            logger.info(f"Fallback notification: {title} - {message}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("macOS notification timed out")
        return False
    except Exception as e:
        logger.error(f"Failed to send macOS notification: {e}")
        return False


def _send_linux_notification(title, message):
    """
    Send a native Linux notification using notify-send or zenity.

    Args:
        title (str): The title of the notification
        message (str): The message content of the notification

    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    logger = get_logger("notification_manager._send_linux_notification")

    try:
        logger.debug("Attempting to send Linux notification...")

        # Try notify-send first
        if shutil.which("notify-send"):
            logger.debug("Using notify-send...")
            result = subprocess.run(
                ["notify-send", title, message],
                capture_output=True,
                text=True,
                timeout=FileLocations.DEFAULT_TIMEOUT,
            )
            if result.returncode == 0:
                logger.debug("notify-send notification sent successfully")
                return True
            else:
                logger.warning(f"notify-send failed: {result.stderr}")

        # Try zenity as fallback
        if shutil.which("zenity"):
            logger.debug("Using zenity...")
            result = subprocess.run(
                ["zenity", "--info", "--title", title, "--text", message],
                capture_output=True,
                text=True,
                timeout=FileLocations.DEFAULT_TIMEOUT,
            )
            if result.returncode == 0:
                logger.debug("zenity notification sent successfully")
                return True
            else:
                logger.warning(f"zenity failed: {result.stderr}")

        # Try kdialog as final fallback
        if shutil.which("kdialog"):
            logger.debug("Using kdialog...")
            result = subprocess.run(
                ["kdialog", "--title", title, "--passivepopup", message, "5"],
                capture_output=True,
                text=True,
                timeout=FileLocations.DEFAULT_TIMEOUT,
            )
            if result.returncode == 0:
                logger.debug("kdialog notification sent successfully")
                return True
            else:
                logger.warning(f"kdialog failed: {result.stderr}")

        logger.warning("No notification system found on Linux")
        logger.info(f"Fallback notification: {title} - {message}")
        return False

    except subprocess.TimeoutExpired:
        logger.error("Linux notification timed out")
        return False
    except Exception as e:
        logger.error(f"Failed to send Linux notification: {e}")
        return False
