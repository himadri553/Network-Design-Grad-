# Network-Design-Project
Repository for EECE 5830 Network Design Programming Project
Himadri Saha

# General Software Approach
- main() will handle starting all necessary threads, starting up connection pipes and initializing helper_files
- Senders and Receivers will be separated into different threads, each with functions to send/receive packets, and handle logic as described by each protocol 
- A plotter thread will handle all features relating to reading data for necessary plots (timers, creating plots etc.)
- helper_files are shared files that all threads can read/write to such as (output images, logs etc.). These are generally reset/deleted during the start of each main() run