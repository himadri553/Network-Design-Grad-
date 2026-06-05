"""
    Himadri Saha

    sender_2.py:

    TODO:
"""

""" Imports """
from socket import *
import helper
import os
import time

class SENDER_2:
    def __init__(self):
        # Self vars
        self.all_chunks = []
        self.seq = 0

        # Setup socket
        self.sender_socket = socket(AF_INET, SOCK_DGRAM)

    def log_print(self, message):
        # Writes a message to the output log
        with open(helper.log_path, 'a') as log_file:
            log_file.write(f"[SENDER] {message}\n")

    """ Helper Functions """
    def pic_to_chunks(self):
        # Splits image into chunks and Saves a full array/list of all the chunks as self.all_chunks
        if not self.all_chunks:
            with open(helper.pic_path, "rb") as f:
                data = f.read()
            
            total_bytes = len(data)
            num_packets = (total_bytes + helper.packet_size - 1) // helper.packet_size

            for i in range(num_packets):
                chunk = data[i * helper.packet_size : (i + 1) * helper.packet_size]
                self.all_chunks.append(chunk)

    def create_data_packet(self, data):
        # Alternate seq number
        self.seq = 1 - self.seq

        # Create length
        length = len(data)

        # Create header without checksum first, then get checksum over header + data
        header_no_checksum = bytes([self.seq]) + length.to_bytes(4, byteorder='big')
        checksum = (sum(header_no_checksum) + sum(data)) % 256

        # Return a full packet with checksum inserted
        header = bytes([self.seq, checksum]) + length.to_bytes(4, byteorder='big')
        packet = header + data
        return packet
    
    def create_ack_packet(self):
        pass

    """ Connection functions """
    def tx_send(self, data):
        # Transmits data over UDP
        self.sender_socket.sendto(data, (helper.receiver_name, helper.receiver_port))
        time.sleep(0.001)

    def tx_receive(self):
        # Listen for and return message from receiver
        self.sender_socket.settimeout(5)
        try:
            data, rx_address = self.sender_socket.recvfrom(helper.buffer_size)
            return data
        except:
            self.log_print("Error: no response from receiver (timed out)")
            return None

    """ Runner Functions for each Scenario """
    def run_tx_sc1(self):
        # Break down picture into packets
        self.pic_to_chunks()

        # Send all chunks
        self.log_print("Sending 5 chunks to the receiver")
        for i in range(len(self.all_chunks)):
            test_packet = self.create_data_packet(self.all_chunks[i])
            self.tx_send(test_packet)