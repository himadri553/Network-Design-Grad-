"""
    Himadri Saha

    main_1.py
        - Main entry to this project, run this file to run the project
        - Prompts user to select scenario

    TODO:
        

"""

""" Imports """
import threading
from socket import *
import time
import os
from sender_1 import SENDER_1
from receiver_1 import RECEIVER_1
import main1_helper

""" Vars """
receiver_name = 'localhost'
receiver_port = 12000
buffer_size = 1024
log_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'output_log.txt')

""" Entry """
def main():
    # Clear output logs
    with open(log_path, 'w') as log_file:
        pass
    main1_helper.main_log_print("Clearing all output logs")
    
    # Create sender and receiver threads
    rx = RECEIVER_1(buffer_size, receiver_port)
    tx = SENDER_1(receiver_name, receiver_port, buffer_size)
    rx_thread = threading.Thread(target=rx.rx_run)
    tx_thread = threading.Thread(target=tx.tx_run)

    # Start running receiver THEN sender, waiting for both to complete
    main1_helper.main_log_print("Starting tx and rx threads")
    rx_thread.start()
    time.sleep(0.5)
    tx_thread.start()
    rx_thread.join()
    tx_thread.join()
    main1_helper.main_log_print("Both threads complete")

if __name__ == "__main__":
    main()