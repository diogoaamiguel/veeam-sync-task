# veeam-sync-task
Description:
This project implements a one-way folder synchronization tool that keeps a replica folder in sync with a source folder. 
The program ensures that the contents of the replica folder match the source folder by performing periodic synchronization, 
which includes copying new or updated files and removing extra files or directories from the replica.

The program also logs all file operations (creation, updates, deletions) to both a log file and the console output for 
tracking and debugging purposes.


Features:

- One-way synchronization: The replica folder mirrors the source folder's contents.
- File comparison: Files are compared using their MD5 hash to ensure only changed files are updated.
- Periodic synchronization: You can configure the synchronization interval in seconds.
- Logging: Every file operation is logged to a file and printed to the console.


Usage:
You can run the program using the following command, which synchronizes the source folder with the replica folder, 
logs operations to a logfile, and runs the synchronization every N seconds.

Command Line: python3 Synchronization.py <source_folder> <replica_folder> <interval_in_seconds> <log_file_path>
