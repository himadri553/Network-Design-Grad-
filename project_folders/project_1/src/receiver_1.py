"""
    Himadri Saha

    receiver_1.py:
        - 

    TODO:
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

    def rx_receive(self):
        # Wait and get message from sender
        # Current implementation assumes sender_address will be the same address for the rx to send back to
        rx_data, self.sender_address = self.rx_socket.recvfrom(self.buffer_size)
        return rx_data.decode()
        
    def rx_send(self, data):
        # Send a message to the SAME place the last message came from
        self.rx_socket.sendto(data.encode(), self.sender_address)

    def log_print(self, message):
        # Writes a message to the output log
        with open(self.log_path, 'a') as log_file:
            log_file.write(f"[RECEIVER] {message}\n")

    def rx_run(self):
        # Initial message 
        self.log_print("Receiver is up and running")

        # Log message received
        received_message = self.rx_receive()
        self.log_print(f"received a message: {received_message}")

        # Echo back the message
        self.rx_send(received_message)




