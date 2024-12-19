# journaling-file-systems

12/09/2024

Jiwon Chae

CSIT431 – Term Project

file_tracker.py is a Journaling File System program that tracks changes (like creation, modification, and deletion) made to .txt files in a watched folder. These changes are logged in corresponding journal files stored in a journal folder. The watchdog library is used to monitor changes in the folder and the Tkinter library is used for GUI.

GUI for users to:
1. Start and stop monitoring the folder.
2. View logs of tracked changes.
3. Rebuild a file's content from its journal entries starting at a specific date.

Thank you.
