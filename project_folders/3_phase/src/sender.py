"""
    Himadri Saha

    sender.py:

    TODO:
"""

""" Imports """
from socket import *
import helper
import time

class SENDER:
    def __init__(self):
        # Self vars
        self.all_chunks = []
        self.seq = 0

        # Countdown timer state (RDT 3.0 start_timer/timeout/stop_timer)
        self.timeout_interval = 5
        self.poll_interval = 0.5
        self.timer_deadline = None

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

    """ Countdown timer functions (RDT 3.0 start_timer/timeout/stop_timer) """
    def start_timer(self):
        # (Re)starts the countdown from timeout_interval seconds
        self.timer_deadline = time.time() + self.timeout_interval

    def timer_expired(self):
        # True once the countdown has reached zero with no valid ACK
        return self.timer_deadline is not None and time.time() >= self.timer_deadline

    def stop_timer(self):
        # Cancels the countdown once a valid ACK arrives
        self.timer_deadline = None

    """ Connection functions """
    def tx_send(self, data):
        # Transmits data over UDP
        self.sender_socket.sendto(data, (helper.receiver_name, helper.receiver_port))
        time.sleep(0.001)

    def tx_receive(self):
        # Poll for a message from the receiver - short socket timeout so the
        # countdown timer can be checked between attempts instead of blocking on it
        self.sender_socket.settimeout(self.poll_interval)
        try:
            data, rx_address = self.sender_socket.recvfrom(helper.buffer_size)
            return data
        except:
            return None

    def wait_for_valid_ack(self, packet, expected_ack_seq, transform=None):
        # RDT 3.0 "Wait for ACK" state: send packet and start_timer; on timeout,
        # retransmit and restart the timer; on a corrupt/duplicate ACK, keep waiting (Λ);
        # on a valid ACK, stop_timer and return so the sender can advance to the next chunk
        self.tx_send(packet)
        self.start_timer()
        while True:
            ack_packet = self.tx_receive()
            if transform is not None:
                ack_packet = transform(ack_packet)

            if self.valid_ack(ack_packet, expected_ack_seq):
                self.stop_timer()
                return

            if self.timer_expired():
                self.tx_send(packet)
                self.start_timer()

    """ Runner Functions for each Scenario """
    ## Scenario 1: No loss/bit-errors
    def run_tx_sc1(self):
        # Break down picture into packets
        self.pic_to_chunks()

        # Transmit Full Image - the countdown timer retransmits indefinitely
        # until a valid ACK is received (RDT 3.0 has no give-up state)
        for i in range(len(self.all_chunks)):
            packet = self.create_data_packet(self.all_chunks[i])
            expected_ack_seq = 1 - self.seq
            self.wait_for_valid_ack(packet, expected_ack_seq)

    ## Scenario 2: ACK packet bit-error
    def run_tx_sc2(self, error_rate):
        # Break down picture into packets
        self.pic_to_chunks()

        # Transmit Full Image - inject bit-errors into received ACKs; the
        # corrupted checksum fails validation and the countdown timer retransmits
        for i in range(len(self.all_chunks)):
            packet = self.create_data_packet(self.all_chunks[i])
            expected_ack_seq = 1 - self.seq
            self.wait_for_valid_ack(packet, expected_ack_seq,
                                    transform=lambda ack: helper.inject_error(ack, error_rate))

    ## Scenario 3: Data packet bit-error
    def run_tx_sc3(self):
        self.run_tx_sc1()

    ## Scenario 4: ACK packet loss
    def run_tx_sc4(self, loss_rate):
        # Break down picture into packets
        self.pic_to_chunks()

        # Transmit Full Image - dropped ACKs never arrive, so the countdown
        # timer expires and retransmits the same packet (RDT 3.0 loss recovery)
        for i in range(len(self.all_chunks)):
            packet = self.create_data_packet(self.all_chunks[i])
            expected_ack_seq = 1 - self.seq
            self.wait_for_valid_ack(packet, expected_ack_seq,
                                    transform=lambda ack: helper.inject_loss(ack, loss_rate))

    ## Scenario 5: Data packet loss
    def run_tx_sc5(self):
        self.run_tx_sc1()