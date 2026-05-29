"""
    Himadri Saha

    sender_2.py:

    TODO:
"""

""" Imports """
from socket import *
import main2_helper
import os

class SENDER_2:
    def __init__(self):
        # Setup socket
        self.sender_socket = socket(AF_INET, SOCK_DGRAM)

    def log_print(self, message):
        # Writes a message to the output log
        with open(main2_helper.log_path, 'a') as log_file:
            log_file.write(f"[SENDER] {message}\n")

    """ Helper Functions """

    """ Connection functions """
    def tx_send(self, data):
        # Transmits data over UDP
        self.sender_socket.sendto(data.encode(), (main2_helper.receiver_name, main2_helper.receiver_port))

    def tx_receive(self):
        # Listen for and return message from receiver
        self.sender_socket.settimeout(5)
        try:
            data, rx_address = self.sender_socket.recvfrom(main2_helper.buffer_size)
            return data.decode()
        except:
            self.log_print("Error: no response from receiver (timed out)")
            return None

    """ Runner Functions for each Scenario """
    def run_tx_sc1(self):
        ## Run tx scenario 1
        # Initial message
        self.log_print("Sender is up and running: Scenario 1")

        # Sending test msg 
        self.log_print("Saying hello")
        self.tx_send("HELLO")

        # Echo back test msg 
        echo_message = self.tx_receive()
        self.log_print(f"Echo Message: {echo_message}") 