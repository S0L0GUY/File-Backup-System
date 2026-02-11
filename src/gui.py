"""
File Backup System GUI
A simple graphical interface for the File Backup System
"""
import sys
import os
import threading
from pathlib import Path
from tkinter import (
    Tk, Text, Scrollbar, Listbox, END, Button, Label, Frame,
    Entry, StringVar, ttk, messagebox,filedialog
)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backup_workflow import execute_backup_workflow
from constants import FileLocations


class BackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Backup System")
        self.root.geometry("700x600")
        self.root.minsize(600, 400)
        
        # Style configuration
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=2)
        
        self.create_widgets()
        self.refresh_sources_list()
        self.refresh_backups_list()

    def create_widgets(self):
        """Create all GUI widgets."""
        
        # Title
        title_label = Label(
            self.root,
            text="File Backup System",
            font=("Arial", 18, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=15)
        
        # Main container
        main_frame = Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Source Folders
        left_panel = Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        Label(
            left_panel,
            text="Source Folders:",
            font=("Arial", 12, "bold"),
            fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 5))
        
        self.sources_listbox = Listbox(
            left_panel,
            height=8,
            bg="white",
            fg="#333",
            selectbackground="#3498db",
            bd=1,
            relief="solid"
        )
        self.sources_listbox.pack(fill="both", expand=True)
        
        source_btn_frame = Frame(left_panel)
        source_btn_frame.pack(fill="x", pady=5)
        
        Button(
            source_btn_frame,
            text="Add Folder",
            command=self.add_source,
            bg="#27ae60",
            fg="white",
            relief="flat",
            padx=10
        ).pack(side="left", padx=(0, 5))
        
        Button(
            source_btn_frame,
            text="Remove",
            command=self.remove_source,
            bg="#e74c3c",
            fg="white",
            relief="flat",
            padx=10
        ).pack(side="left")
        
        # Right panel - Backup Locations
        right_panel = Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        Label(
            right_panel,
            text="Backup Locations:",
            font=("Arial", 12, "bold"),
            fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 5))
        
        self.backups_listbox = Listbox(
            right_panel,
            height=8,
            bg="white",
            fg="#333",
            selectbackground="#3498db",
            bd=1,
            relief="solid"
        )
        self.backups_listbox.pack(fill="both", expand=True)
        
        backup_btn_frame = Frame(right_panel)
        backup_btn_frame.pack(fill="x", pady=5)
        
        Button(
            backup_btn_frame,
            text="Add Location",
            command=self.add_backup_location,
            bg="#27ae60",
            fg="white",
            relief="flat",
            padx=10
        ).pack(side="left", padx=(0, 5))
        
        Button(
            backup_btn_frame,
            text="Remove",
            command=self.remove_backup,
            bg="#e74c3c",
            fg="white",
            relief="flat",
            padx=10
        ).pack(side="left")
        
        # Backup Name
        name_frame = Frame(main_frame)
        name_frame.pack(fill="x", pady=15)
        
        Label(name_frame, text="Backup Name:", font=("Arial", 11)).pack(side="left")
        
        self.name_var = StringVar(value=FileLocations.BACKUP_FILE_NAME)
        self.name_entry = Entry(
            name_frame,
            textvariable=self.name_var,
            width=30,
            bd=1,
            relief="solid"
        )
        self.name_entry.pack(side="left", padx=10)
        
        # Run Button
        self.run_btn = Button(
            main_frame,
            text="RUN BACKUP",
            command=self.run_backup_thread,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            padx=30,
            pady=10
        )
        self.run_btn.pack(pady=10)
        
        # Progress
        self.progress_label = Label(
            main_frame,
            text="Ready",
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        self.progress_label.pack(pady=(5, 0))
        
        # Log output
        log_frame = Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=15)
        
        Label(
            log_frame,
            text="Log Output:",
            font=("Arial", 11, "bold"),
            fg="#2c3e50"
        ).pack(anchor="w")
        
        log_text_frame = Frame(log_frame)
        log_text_frame.pack(fill="both", expand=True)
        
        self.log_text = Text(
            log_text_frame,
            height=12,
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Consolas", 9),
            bd=0,
            padx=10,
            pady=10
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = Scrollbar(
            log_text_frame,
            command=self.log_text.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_label = Label(
            self.root,
            text="Configure folders and click 'RUN BACKUP' to start",
            font=("Arial", 9),
            fg="#7f8c8d",
            relief="sunken",
            bd=1
        )
        self.status_label.pack(side="bottom", fill="x", padx=2, pady=2)

    def log(self, message, level="INFO"):
        """Add a message to the log window."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(END)
        self.root.update_idletasks()
    
    def add_source(self):
        """Add a source folder."""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            FileLocations.ORIGINAL_FILE_LOCATIONS.append(folder)
            self.log(f"Added source: {folder}")
            self.refresh_sources_list()
            self.status_label.config(text=f"{len(FileLocations.ORIGINAL_FILE_LOCATIONS)} source(s), {len(FileLocations.BACKUP_LOCATIONS)} backup location(s)")

    def remove_source(self):
        """Remove selected source folder."""
        selection = self.sources_listbox.curselection()
        if selection:
            index = selection[0]
            folder = FileLocations.ORIGINAL_FILE_LOCATIONS.pop(index)
            self.log(f"Removed source: {folder}")
            self.refresh_sources_list()
            self.status_label.config(text=f"{len(FileLocations.ORIGINAL_FILE_LOCATIONS)} source(s), {len(FileLocations.BACKUP_LOCATIONS)} backup location(s)")

    def add_backup_location(self):
        """Add a backup location."""
        folder = filedialog.askdirectory(title="Select Backup Location")
        if folder:
            FileLocations.BACKUP_LOCATIONS.append(folder)
            self.log(f"Added backup location: {folder}")
            self.refresh_backups_list()
            self.status_label.config(text=f"{len(FileLocations.ORIGINAL_FILE_LOCATIONS)} source(s), {len(FileLocations.BACKUP_LOCATIONS)} backup location(s)")

    def remove_backup(self):
        """Remove selected backup location."""
        selection = self.backups_listbox.curselection()
        if selection:
            index = selection[0]
            folder = FileLocations.BACKUP_LOCATIONS.pop(index)
            self.log(f"Removed backup location: {folder}")
            self.refresh_backups_list()
            self.status_label.config(text=f"{len(FileLocations.ORIGINAL_FILE_LOCATIONS)} source(s), {len(FileLocations.BACKUP_LOCATIONS)} backup location(s)")

    def refresh_sources_list(self):
        """Refresh the sources listbox."""
        self.sources_listbox.delete(0, END)
        for folder in FileLocations.ORIGINAL_FILE_LOCATIONS:
            self.sources_listbox.insert(END, folder)

    def refresh_backups_list(self):
        """Refresh the backups listbox."""
        self.backups_listbox.delete(0, END)
        for folder in FileLocations.BACKUP_LOCATIONS:
            self.backups_listbox.insert(END, folder)

    def run_backup_thread(self):
        """Run backup in a separate thread."""
        # Update backup name
        FileLocations.BACKUP_FILE_NAME = self.name_var.get()
        
        if not FileLocations.ORIGINAL_FILE_LOCATIONS:
            messagebox.showwarning("No Sources", "Please add at least one source folder!")
            return
        
        if not FileLocations.BACKUP_LOCATIONS:
            messagebox.showwarning("No Backup Locations", "Please add at least one backup location!")
            return
        
        # Disable button during backup
        self.run_btn.config(state="disabled", bg="#95a5a6")
        self.progress_label.config(text="Backup in progress...")
        self.log("=" * 50)
        self.log("Starting backup...")
        self.log(f"Sources: {len(FileLocations.ORIGINAL_FILE_LOCATIONS)} folder(s)")
        self.log(f"Backups: {len(FileLocations.BACKUP_LOCATIONS)} location(s)")
        self.log("=" * 50)
        
        # Run in thread
        thread = threading.Thread(target=self._run_backup)
        thread.start()

    def _run_backup(self):
        """Execute backup (runs in thread)."""
        try:
            success = execute_backup_workflow()
            
            if success:
                self.log("Backup completed successfully!", "SUCCESS")
                self.progress_label.config(text="Backup complete!")
                self.root.after(0, lambda: messagebox.showinfo("Success", "Backup completed successfully!"))
            else:
                self.log("Backup failed. Check logs for details.", "ERROR")
                self.progress_label.config(text="Backup failed!")
                self.root.after(0, lambda: messagebox.showerror("Failed", "Backup failed. Check logs for details."))
        except Exception as e:
            self.log(f"Error: {e}", "ERROR")
            self.progress_label.config(text="Error occurred!")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self._enable_button)

    def _enable_button(self):
        """Re-enable the run button."""
        self.run_btn.config(state="normal", bg="#3498db")


def main():
    """Main entry point."""
    root = Tk()
    app = BackupGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
