"""
    Himadri Saha

    receiver.py:
        - 

    TODO:
"""

""" Imports """
from socket import *
import helper
import time

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

    def create_ack_packet(self, ack_seq):
        checksum = ack_seq % 256
        return bytes([ack_seq, checksum])

    """ Connection functions """
    def rx_receive(self):
        # Wait and get message from sender
        # Current implementation assumes sender_address will be the same address for the rx to send back to
        self.rx_socket.settimeout(5)
        try:
            rx_data, self.sender_address = self.rx_socket.recvfrom(helper.buffer_size)
            return rx_data
        except:
            return None
    
    def rx_send(self, data):
        # Send a message to the SAME place the last message came from
        self.rx_socket.sendto(data, self.sender_address)
        time.sleep(0.001)

    """ Runner Functions for each Scenario """
    def run_rx_sc1(self):
        # Receive all packets and reconstruct image
        while True:
            # Keep listening for packets until there is none left
            rx_packet = self.rx_receive()
            if rx_packet is None:
                break

            seq, checksum, length, data = self.extract(rx_packet)

            if seq != self.expected_seq:
                self.rx_send(self.create_ack_packet(1 - self.expected_seq))
            elif self.corrupt(rx_packet):
                self.rx_send(self.create_ack_packet(1 - self.expected_seq))
            else:
                self.full_pic.append(data)
                self.rx_send(self.create_ack_packet(seq))
                self.expected_seq = 1 - self.expected_seq

        self.reconstruct_image(self.full_pic)

    def run_rx_sc2(self):
        self.run_rx_sc1()

    def run_rx_sc3(self, error_rate):
        while True:
            rx_packet = self.rx_receive()
            if rx_packet is None:
                break
            rx_packet = helper.inject_error(rx_packet, error_rate)

            seq, checksum, length, data = self.extract(rx_packet)

            if seq != self.expected_seq:
                self.rx_send(self.create_ack_packet(1 - self.expected_seq))
            elif self.corrupt(rx_packet):
                self.rx_send(self.create_ack_packet(1 - self.expected_seq))
            else:
                self.full_pic.append(data)
                self.rx_send(self.create_ack_packet(seq))
                self.expected_seq = 1 - self.expected_seq

        self.reconstruct_image(self.full_pic)

    def run_rx_sc4(self):
        self.run_rx_sc1()

    def run_rx_sc5(self, loss_rate):
        while True:
            rx_packet = self.rx_receive()
            if rx_packet is None:
                break
            rx_packet = helper.inject_loss(rx_packet, loss_rate)
            if rx_packet is None:
                # Packet dropped - send nothing back; the sender's countdown
                # timer will expire and retransmit (RDT 3.0 loss recovery)
                continue

            seq, checksum, length, data = self.extract(rx_packet)

            if seq != self.expected_seq:
                self.rx_send(self.create_ack_packet(1 - self.expected_seq))
            elif self.corrupt(rx_packet):
                self.rx_send(self.create_ack_packet(1 - self.expected_seq))
            else:
                self.full_pic.append(data)
                self.rx_send(self.create_ack_packet(seq))
                self.expected_seq = 1 - self.expected_seq

        self.reconstruct_image(self.full_pic)