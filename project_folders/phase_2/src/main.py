"""
    Himadri Saha

    main.py
        - Main entry to this project, run this file to run the project
        - Chunk refers to picture data broken down into size helper.packet_size
        - Packet is the data sent from the sender with all the headers

    Phase 2 Tasks:
        - Protocol Implementation: 
            - Implement a checksum for error detection on DATA and ACK packets. (corrupt packets)
            - Implement ACK-based recovery (RDT 2.2 is NAK-free).
            - Sender and receiver behavior must match the RDT 2.2 sender/receiver FSM semantics
        - Verify Image reconstruction
        - Scenarios
            - 2. ACK packet bit-error injection at the sender-side receive path (and correct recovery)
            - 3. DATA packet bit-error injection at the receiver-side receive path (and correct recovery
        - Plots
            - x-axis: loss/error rate (%)
            - y-axis: completion time in seconds (average of runs)
        - Deliverables 
            - Demo Video

    TODO:

"""

""" Imports """
import threading
from socket import *
import time
import os
from sender import SENDER as sender
from receiver import RECEIVER as receiver
import helper

""" Entry """
def main():
    # Clear output files
    with open(helper.log_path, 'w') as log_file:
        pass
    helper.main_log_print("Clearing all output logs")

    # Run Scenario 1 - No loss/bit-errors
    tx = sender()
    rx = receiver()
    tx_thread_sc1 = threading.Thread(target=tx.run_tx_sc1)
    rx_thread_sc1 = threading.Thread(target=rx.run_rx_sc1)
    helper.main_log_print(f"[PLOT] TX_START sc=1 @ {time.time()}")
    helper.main_log_print("Phase 2: Starting Scenario 1 - No loss/bit-errors")
    rx_thread_sc1.start()
    time.sleep(0.5)
    tx_thread_sc1.start()
    rx_thread_sc1.join()
    tx_thread_sc1.join()
    helper.main_log_print(f"[PLOT] TX_END sc=1 @ {time.time()}")
    helper.main_log_print("Both threads complete")

    # Run Scenario 2 - ACK packet bit-error

    # Run Scenario 3 - Data packet bit-error

if __name__ == "__main__":
    main()