"""
    Himadri Saha

    main_1b.py
        - Main entry to this project, run this file to run the project
        - Chunk refers to picture data broken down into size main2_helper.packet_size
        - Packet is the data sent from the sender with all the headers and stuff

    TODO:

"""

""" Imports """
import threading
from socket import *
import time
import os
from sender_1b import SENDER_2
from receiver_1b import RECEIVER_2
import main1b_helper as main1b_helper

""" Entry """
def main():
    # Clear output files
    with open(main1b_helper.log_path, 'w') as log_file:
        pass
    main1b_helper.main_log_print("Clearing all output logs")

    # Create sender and receiver threads
    tx = SENDER_2()
    rx = RECEIVER_2()
    tx_thread_sc1 = threading.Thread(target=tx.run_tx_sc1)
    rx_thread_sc1 = threading.Thread(target=rx.run_rx_sc1)

    # Start running receiver THEN sender, waiting for both to complete. For all scenarios
    main1b_helper.main_log_print("Starting tx and rx threads for Phase 1b")
    rx_thread_sc1.start()
    time.sleep(0.5)
    tx_thread_sc1.start()
    rx_thread_sc1.join()
    tx_thread_sc1.join()
    main1b_helper.main_log_print("Both threads complete")

if __name__ == "__main__":
    main()