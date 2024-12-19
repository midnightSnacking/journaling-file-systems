# file_tracker.py

# Dec 9,2024
# Jiwon Chae

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# folder paths
watched_folder = "folder_1"
journal_folder = "folder_2"

# monitoring class using Watchdog
class WatchHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".txt"):
            log_change(event.src_path, "modified")

    def on_created(self, event):
        if event.src_path.endswith(".txt"):
            log_change(event.src_path, "created")

    def on_deleted(self, event):
        if event.src_path.endswith(".txt"):
            log_change(event.src_path, "deleted")

def log_change(file_path, action):
    journal_name = create_journal_name(file_path)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    # read the current file content
    current_lines = []
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            current_lines = file.readlines()

    # get previous file content from journal
    previous_lines = get_previous_lines(journal_name)

    # compare old and new content to detect changes
    changes = detect_changes(previous_lines, current_lines)

    # write changes to the journal
    with open(journal_name, "a+") as journal:
        journal.seek(0)
        lines = journal.readlines()

        for change in changes:
            log_entry = f"{timestamp}, {change['action']}, l{change['line_number']}: {change['line_content']}\n"
            lines.append(log_entry)

        # maintain circular journal of 50 entries
        if len(lines) > 50:
            lines = lines[-50:]  # keep the last 50 entries

        journal.seek(0)
        journal.truncate()
        journal.writelines(lines)

def create_journal_name(file_path):
    file_name = os.path.basename(file_path)
    random_suffix = str(hash(file_path))[:6]
    return os.path.join(journal_folder, f"j1_{file_name}_{random_suffix}.DAT")

def get_previous_lines(journal_name):
    """Reconstruct the previous state of the file from the journal."""
    if not os.path.exists(journal_name):
        return []

    lines = []
    with open(journal_name, "r") as journal:
        for entry in journal:
            _, action, change = entry.strip().split(", ", 2)
            line_number, line_content = change.split(": ", 1)
            line_index = int(line_number[1:]) - 1

            if action == "added":
                if line_index < len(lines):
                    lines.insert(line_index, line_content)
                else:
                    lines.append(line_content)
            elif action == "removed":
                if line_index < len(lines):
                    lines.pop(line_index)
    return lines


def detect_changes(old_lines, new_lines):
    """Detect differences between old and new file content."""
    changes = []
    max_length = max(len(old_lines), len(new_lines))

    for i in range(max_length):
        old_line = old_lines[i] if i < len(old_lines) else None
        new_line = new_lines[i] if i < len(new_lines) else None

        if old_line != new_line:
            if old_line is not None:
                changes.append({"action": "removed", "line_number": i + 1, "line_content": old_line.strip()})
            if new_line is not None:
                changes.append({"action": "added", "line_number": i + 1, "line_content": new_line.strip()})

    return changes

def replay_journal(journal_path, start_date):
    """Reconstruct the file content from a specific date."""
    reconstructed_lines = []
    try:
        with open(journal_path, "r") as journal:
            for line in journal:
                timestamp, action, change = line.split(", ", 2)
                if timestamp >= start_date:
                    line_number, line_content = change.split(": ", 1)
                    line_index = int(line_number[1:]) - 1

                    if action == "added":
                        if line_index < len(reconstructed_lines):
                            reconstructed_lines.insert(line_index, line_content)
                        else:
                            reconstructed_lines.append(line_content)
                    elif action == "removed":
                        if line_index < len(reconstructed_lines):
                            reconstructed_lines.pop(line_index)
        return reconstructed_lines
    except FileNotFoundError:
        return []

# GUI
class JournalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Journaling File System")
        self.root.geometry('300x200')
        

        # observer for monitoring
        self.observer = None

        # buttons
        self.start_btn = tk.Button(root, text="Start", command=self.start)
        self.start_btn.pack(pady=10)

        self.stop_btn = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(pady=10)

        self.view_btn = tk.Button(root, text="View Journals", command=self.view_journals)
        self.view_btn.pack(pady=10)

        self.replay_btn = tk.Button(root, text="Rebuild Journal", command=self.rebuild_journal)
        self.replay_btn.pack(pady=10)

    def start(self):
        self.observer = Observer()
        self.event_handler = WatchHandler()
        self.observer.schedule(self.event_handler, watched_folder, recursive=False)
        self.observer.start()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Info", "Started monitoring the folder.")

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        messagebox.showinfo("Info", "Stopped monitoring the folder.")

    def view_journals(self):
        journals = os.listdir(journal_folder)
        if not journals:
            messagebox.showinfo("Info", "No journals found.")
            return
        journal = simpledialog.askstring("Select Journal", f"Available Journals:\n{', '.join(journals)}")
        if journal and journal in journals:
            with open(os.path.join(journal_folder, journal), "r") as file:
                content = file.read()
                messagebox.showinfo("Journal Content", content)
        else:
            messagebox.showerror("Error", "Invalid file name.")

    def rebuild_journal(self):
        journals = os.listdir(journal_folder)
        if not journals:
            messagebox.showinfo("Journaling File System", "No journals found.")
            return
        journal = simpledialog.askstring("Select Journal", f"Available Journals:\n{', '.join(journals)}")
        if journal and journal in journals:
            start_date = simpledialog.askstring("Replay From", "Enter start date (YYYY-MM-DD HH:MM:SS):")
            if start_date:
                result = replay_journal(os.path.join(journal_folder, journal), start_date)
                messagebox.showinfo("Replayed Content", "\n".join(result))
        else:
            messagebox.showerror("Error", "Invalid file name.")


# main
if __name__ == "__main__":
    root = tk.Tk()
    app = JournalGUI(root)
    root.mainloop()
