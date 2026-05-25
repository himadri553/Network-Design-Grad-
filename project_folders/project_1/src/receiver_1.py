"""
    Himadri Saha

    receiver_1.py:
        - 

    TODO:
        - get tx/rx to connect and send some message 
"""

""" Imports """
import threading
from socket import *
import os

class RECEIVER_1:
    def __init__(self, buffer_size, port):
        # Set class vars
        self.port = port
        self.buffer_size = buffer_size
        self.log_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'output_log.txt')

        # Setup sockets 
        self.rx_socket = socket(AF_INET, SOCK_DGRAM)
        self.rx_socket.bind(('localhost', self.port))

    def rx_message(self):
        # Wait and get message from sender
        rx_data, rx_address = self.rx_socket.recvfrom(self.buffer_size)
        return rx_data
        
    def log_print(self, message):
        # Writes a message to the output log
        with open(self.log_path, 'a') as log_file:
            log_file.write(f"[RECEIVER]: {message}\n")

    def rx_run(self):
        # Initial message 
        self.log_print("Receiver is up and running")

        # Send "HELLO"
        received_message = self.rx_message()
        self.log_print(f"received a message: {received_message}")


