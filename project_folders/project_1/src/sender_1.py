"""
    Himadri Saha

    sender_1.py:
        - sender class holding all logic required for phase 1

    TODO:
"""

""" Imports """
from socket import *
import os

class SENDER_1:
    def __init__(self, rx_name, rx_port):
        # Set self vars
        self.rx_name = rx_name
        self.rx_port = rx_port
        self.log_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'output_log.txt')

        # Setup socket
        self.sender_socket = socket(AF_INET, SOCK_DGRAM)

    def send(self, data):
        # Transmits data over UDP
        self.sender_socket.sendto(data.encode(), (self.rx_name, self.rx_port))

    def log_print(self, message):
        # Writes a message to the output log
        with open(self.log_path, 'a') as log_file:
            log_file.write(f"[SENDER]: {message}\n")

    def tx_run(self):
        # Initial message
        self.log_print("Sender is up and running")

        self.log_print("sending HELLO over UDP...")
        self.send("HELLO")
        self.log_print("sent message, waiting for ECHO message from receiver...")