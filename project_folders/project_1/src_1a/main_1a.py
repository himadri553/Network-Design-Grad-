"""
    Himadri Saha

    main_1a.py
        - Main entry to this project, run this file to run the project
        - User starts control of the sender

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

""" Phase 1a Sender and receiver Run functions """
def tx_run_1a(sender):
    # Initial message
    sender.log_print("Sender is up and running")

    # Send HELLO over UDP
    sender.log_print("sending HELLO over UDP...")
    sender.tx_send("HELLO")
    sender.log_print("sent message, waiting for ECHO message from receiver...")

    # Wait for rx to echo a message back
    echo_message = sender.tx_receive()
    sender.log_print(f"Echo Message: {echo_message}")  

def rx_run_1a(receiver):
    # Initial message 
    receiver.log_print("Receiver is up and running")

    # Log message received
    received_message = receiver.rx_receive()
    receiver.log_print(f"received a message: {received_message}")

    # Echo back the message
    receiver.rx_send(received_message)

""" Entry """
def main():
    # Clear output logs
    with open(log_path, 'w') as log_file:
        pass
    main1_helper.main_log_print("Clearing all output logs")

    # Create sender and receiver threads
    rx = RECEIVER_1(buffer_size, receiver_port)
    tx = SENDER_1(receiver_name, receiver_port, buffer_size)
    rx_thread = threading.Thread(target=rx_run_1a, args=(rx,))
    tx_thread = threading.Thread(target=tx_run_1a, args=(tx,))

    # Start running receiver THEN sender, waiting for both to complete
    main1_helper.main_log_print("Starting tx and rx threads for phase 1a")
    rx_thread.start()
    time.sleep(0.5)
    tx_thread.start()
    rx_thread.join()
    tx_thread.join()
    main1_helper.main_log_print("Both threads complete")

if __name__ == "__main__":
    main()