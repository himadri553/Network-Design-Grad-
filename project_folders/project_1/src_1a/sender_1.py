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
    def __init__(self, rx_name, rx_port, buffer_size):
        # Set self vars
        self.buffer_size = buffer_size
        self.rx_name = rx_name
        self.rx_port = rx_port
        self.log_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'output_log.txt')

        # Setup socket
        self.sender_socket = socket(AF_INET, SOCK_DGRAM)

    def tx_send(self, data):
        # Transmits data over UDP
        self.sender_socket.sendto(data.encode(), (self.rx_name, self.rx_port))

    def tx_receive(self):
        # Listen for and return message from receiver
        self.sender_socket.settimeout(5)
        try:
            data, rx_address = self.sender_socket.recvfrom(self.buffer_size)
            return data.decode()
        except:
            self.log_print("Error: no response from receiver (timed out)")
            return None

    def log_print(self, message):
        # Writes a message to the output log
        with open(self.log_path, 'a') as log_file:
            log_file.write(f"[SENDER] {message}\n")