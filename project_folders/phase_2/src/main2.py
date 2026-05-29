"""
    Himadri Saha

    main_2.py
        - Main entry to this project, run this file to run the project

    TODO:
        - Set up sockets and connection
        - Create make_packet function (tx)
        - Create build_image function (rx) to output image
        - Implement sequence numbers and other packet headers

"""

""" Imports """
import threading
from socket import *
import time
import os
from sender_2 import SENDER_2
from receiver_2 import RECEIVER_2
import main2_helper

""" Vars """

""" Entry """
def main():
    # Clear output logs
    with open(main2_helper.log_path, 'w') as log_file:
        pass
    main2_helper.main_log_print("Clearing all output logs")

    # Create sender and receiver threads
    tx = SENDER_2()
    rx = RECEIVER_2()
    tx_thread_sc1 = threading.Thread(target=tx.run_tx_sc1)
    rx_thread_sc1 = threading.Thread(target=rx.run_rx_sc1)

    # Start running receiver THEN sender, waiting for both to complete. For all scenarios
    main2_helper.main_log_print("Starting tx and rx threads for Phase 2 - Scenario 1")
    rx_thread_sc1.start()
    time.sleep(0.5)
    tx_thread_sc1.start()
    rx_thread_sc1.join()
    tx_thread_sc1.join()
    main2_helper.main_log_print("Both threads complete")

if __name__ == "__main__":
    main()