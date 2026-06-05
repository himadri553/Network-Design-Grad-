"""
    Himadri Saha

    main_2.py
        - Main entry to this project, run this file to run the project
        - Chunk refers to picture data broken down into size main2_helper.packet_size
        - Packet is the data sent from the sender with all the headers

    TODO:
        - Fix corrupt and out of seq checks on rx
            - Seq check is breaking things, might be an issue with how tx is extracting ack packets
        - Add things to the log - plot log messages
        - Create plots based on time stamp

"""

""" Imports """
import threading
from socket import *
import time
import os
from sender_2 import SENDER_2
from receiver_2 import RECEIVER_2
import main2_helper

""" Entry """
def main():
    # Clear output files
    with open(main2_helper.log_path, 'w') as log_file:
        pass
    main2_helper.main_log_print("Clearing all output logs")

    # Run Scenario 1 - No loss/bit-errors
    tx = SENDER_2()
    rx = RECEIVER_2()
    tx_thread_sc1 = threading.Thread(target=tx.run_tx_sc1)
    rx_thread_sc1 = threading.Thread(target=rx.run_rx_sc1)
    main2_helper.main_log_print("Phase 2: Starting Scenario 1 - No loss/bit-errors")
    rx_thread_sc1.start()
    time.sleep(0.5)
    tx_thread_sc1.start()
    rx_thread_sc1.join()
    tx_thread_sc1.join()
    main2_helper.main_log_print("Both threads complete")

    # Run Scenario 2 - ACK packet bit-error

    # Run Scenario 3 - Data packet bit-error

if __name__ == "__main__":
    main()