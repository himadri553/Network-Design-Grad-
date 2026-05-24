# Network-Design-Project
Repository for EECE 5830 Network Design Programming Project
Himadri Saha

# Guide
- Go to project_folders\project_X\code, and run project_x.py
- Files that the program will use (output images, logs etc.) are located in project_folders\project_X\helper_files
- project_folders\project_X\helper_files\output_log.txt contains an overall log of each thread 
- project_folders\project_X\docs\project_x_writeup.md contains a writeup of each project
- Using Python 3.13.12

# General Software Approach
- main() will handle starting all necessary threads, starting up connection pipes and initializing helper_files
- Senders and Receivers will be separated into different threads, each with functions to send/receive packets, and handle logic as described by each protocol 
- A plotter thread will handle all features relating to reading data for necessary plots (timers, creating plots etc.)
- helper_files are shared files that all threads can read/write to such as (output images, logs etc.). These are generally reset/deleted during the start of each main() run