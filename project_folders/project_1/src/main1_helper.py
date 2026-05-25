"""
    Himadri Saha

    main1_helper.py
        - Contains helper functions that is used by main

    TODO:

"""

""" Imports """
import os

""" Vars """
log_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'output_log.txt')

def main_log_print(message):
    # Writes a message to the output log
    with open(log_path, 'a') as log_file:
        log_file.write(f"[MAIN]: {message}\n")