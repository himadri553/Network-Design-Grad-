"""
    Himadri Saha

    receiver_2.py:
        - 

    TODO:
"""

""" Imports """
import threading
from socket import *
import os
import main2_helper

class RECEIVER_2:
    def __init__(self):
        # Setup sockets 
        self.rx_socket = socket(AF_INET, SOCK_DGRAM)
        self.rx_socket.bind(('localhost', main2_helper.receiver_port))

    def log_print(self, message):
        # Writes a message to the output log
        with open(main2_helper.log_path, 'a') as log_file:
            log_file.write(f"[RECEIVER] {message}\n")

    """ Helper Functions """

    """ Connection functions """
    def rx_receive(self):
        # Wait and get message from sender
        # Current implementation assumes sender_address will be the same address for the rx to send back to
        self.rx_socket.settimeout(5)
        try:
            rx_data, self.sender_address = self.rx_socket.recvfrom(main2_helper.buffer_size)
            return rx_data.decode()
        except:
            self.log_print("Error: no response from sender (timed out)")
            return None
    
    def rx_send(self, data):
        # Send a message to the SAME place the last message came from
        self.rx_socket.sendto(data.encode(), self.sender_address)

    """ Runner Functions for each Scenario """
    def run_rx_sc1(self):
        self.log_print("RX is up and running, Scenario 1")
        self.log_print("Waiting for a message...")
        received_message = self.rx_receive()
        self.log_print(f"Got this message: {received_message}")
        self.rx_send(received_message)
