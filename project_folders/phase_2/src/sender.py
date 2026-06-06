"""
    Himadri Saha

    sender.py:

    TODO:
"""

""" Imports """
from socket import *
import helper
import os
import time

class SENDER:
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
        # Create length
        length = len(data)

        # Create header without checksum first, then get checksum over header + data
        header_no_checksum = bytes([self.seq]) + length.to_bytes(4, byteorder='big')
        checksum = (sum(header_no_checksum) + sum(data)) % 256

        # Return a full packet with checksum inserted
        header = bytes([self.seq, checksum]) + length.to_bytes(4, byteorder='big')
        packet = header + data

        # Alternate seq number
        self.seq = 1 - self.seq

        return packet
    
    def valid_ack(self, ack_packet, expected_ack_seq):
        if ack_packet is None:
            return False
        ack_seq  = ack_packet[0]
        checksum = ack_packet[1]
        if ack_seq % 256 != checksum:
            return False
        if ack_seq != expected_ack_seq:
            return False
        return True

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
    ## Scenario 1: No loss/bit-errors
    def run_tx_sc1(self):
        # Break down picture into packets
        self.pic_to_chunks()

        # Transmit Full Image - Retransmit until valid Ack packet is received 
        for i in range(len(self.all_chunks)):
            packet = self.create_data_packet(self.all_chunks[i])
            expected_ack_seq = 1 - self.seq
            while True:
                # Transmit packet 
                self.tx_send(packet)

                # Check valid ack 
                ack_packet = self.tx_receive()
                if self.valid_ack(ack_packet, expected_ack_seq):
                    break