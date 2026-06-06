"""
    Himadri Saha

    receiver.py:
        - 

    TODO:
"""

""" Imports """
import threading
from socket import *
import os
import helper

class RECEIVER:
    def __init__(self):
        # Self Vars
        self.full_pic = []
        self.expected_seq = 0

        # Setup sockets 
        self.rx_socket = socket(AF_INET, SOCK_DGRAM)
        self.rx_socket.bind(('localhost', helper.receiver_port))

    def log_print(self, message):
        # Writes a message to the output log
        with open(helper.log_path, 'a') as log_file:
            log_file.write(f"[RECEIVER] {message}\n")

    """ Helper Functions """
    def extract(self, packet):
        # Extract all parts of the packet
        seq      = packet[0]
        checksum = packet[1]
        length   = int.from_bytes(packet[2:6], byteorder='big')
        data     = packet[6:6 + length]

        return seq, checksum, length, data

    def corrupt(self, packet):
        # Check to see if packet is corrupted. Returns True if corrupted
        seq, checksum, length, data = self.extract(packet)
        # Calculate checksum over header + data
        header_no_checksum = bytes([seq]) + length.to_bytes(4, byteorder='big')
        recalculated_checksum = (sum(header_no_checksum) + sum(data)) % 256
        return recalculated_checksum != checksum

    def reconstruct_image(self, pic_data):
        # Concatenate all chunks and write to file
        full_data = b''.join(pic_data)
        with open (helper.output_pic_path, "wb") as f:
            f.write(full_data)

    """ Connection functions """
    def rx_receive(self):
        # Wait and get message from sender
        # Current implementation assumes sender_address will be the same address for the rx to send back to
        self.rx_socket.settimeout(5)
        try:
            rx_data, self.sender_address = self.rx_socket.recvfrom(helper.buffer_size)
            self.log_print("Received something")
            return rx_data
        except:
            self.log_print("Error: no response from sender (5 sec time out)")
            return None
    
    def rx_send(self, data):
        # Send a message to the SAME place the last message came from
        self.rx_socket.sendto(data, self.sender_address)

    """ Runner Functions for each Scenario """
    def run_rx_sc1(self):
        # Receive all packets and reconstruct image
        while True:
            # Keep listening for packets until there is none left
            rx_data = self.rx_receive()
            if rx_data is None:
                self.log_print("No more packets, reconstructing image")
                break
            
            # Extract Packet headers
            seq, checksum, length, data = self.extract(rx_data)
            self.log_print(f"Seq: {seq}, Checksum: {checksum}, Length: {length}")

            # Check if packet is corrupted, or out of order
            '''
            if self.corrupt(rx_data):
                self.log_print("Packet corrupted, discarding")
            elif seq != self.expected_seq:
                self.log_print(f"Out of order packet (expected {self.expected_seq}, got {seq}), discarding")
            # Valid packet
            else:
            '''
            
            # Add to final image
            self.full_pic.append(data)

            # Update seq number
            self.expected_seq = 1 - self.expected_seq
            
        # Reconstruct Image
        self.reconstruct_image(self.full_pic)
        self.log_print("Image successfully reconstructed")