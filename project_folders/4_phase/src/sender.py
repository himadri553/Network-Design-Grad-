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
    def __init__(self, window_size=None):
        # Self vars
        self.all_chunks = []

        # Countdown timer state (start_timer/timeout/stop_timer)
        self.timeout_interval = 5
        self.poll_interval = 0.5
        self.timer_deadline = None

        # Go-Back-window_size sender state. base/nextseqnum are absolute chunk indices
        # (monotonic); the seq byte placed in each packet is index % 256. Because
        # window_size <= 50 < 256, (nextseqnum - base) never needs an explicit mod here.
        self.window_size = window_size if window_size is not None else helper.window_size
        self.base = 0          # absolute index of oldest unACKed chunk
        self.nextseqnum = 0    # absolute index of next chunk to send
        self.sndpkt = {}       # absolute index -> built packet, currently in flight

        # Setup socket
        self.sender_socket = socket(AF_INET, SOCK_DGRAM)

    def log_print(self, message):
        # Writes a message to the output log (silenced during timing runs, R17)
        if not helper.verbose_packet_logs:
            return
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

    def create_data_packet(self, data, seq):
        # Builds a data packet for the given seq byte (0-255):
        # [ seq | checksum | length(4B BE) | data ]
        length = len(data)

        # Checksum over header (excluding the checksum byte) + payload, mod 256
        header_no_checksum = bytes([seq]) + length.to_bytes(4, byteorder='big')
        checksum = (sum(header_no_checksum) + sum(data)) % 256

        header = bytes([seq, checksum]) + length.to_bytes(4, byteorder='big')
        return header + data

    def valid_ack(self, ack_packet):
        # Returns the cumulative ack_seq byte if the ACK is present and uncorrupted,
        # otherwise None (corrupt/lost ACK -> Lambda transition, no state change)
        if ack_packet is None or len(ack_packet) < 2:
            return None
        ack_seq  = ack_packet[0]
        checksum = ack_packet[1]
        if ack_seq % 256 != checksum:
            return None
        return ack_seq

    def ack_to_abs(self, ack_byte):
        # Map a cumulative ACK byte back to an absolute chunk index inside the
        # current window [base, nextseqnum). Window < 256, so at most one match.
        for idx in range(self.base, self.nextseqnum):
            if idx % 256 == ack_byte:
                return idx
        return None

    """ Countdown timer functions (start_timer/timeout/stop_timer) """
    def start_timer(self):
        # (Re)starts the countdown from timeout_interval seconds
        self.timer_deadline = time.time() + self.timeout_interval

    def timer_expired(self):
        # True once the countdown has reached zero with no valid ACK
        return self.timer_deadline is not None and time.time() >= self.timer_deadline

    def stop_timer(self):
        # Cancels the countdown once the window fully drains
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

    def gbn_send_loop(self, ack_transform=None, deadline=None):
        # Pipelined Go-Back-window_size send loop (replaces stop-and-wait wait_for_valid_ack).
        #   ack_transform: optional fn applied to each received ACK before validation
        #                  (per-scenario error/loss injection on the ACK path)
        #   deadline:      wall-clock scenario cap so a run always terminates
        total = len(self.all_chunks)

        while self.base < total:
            # --- Send step: fill the window with new packets, back-to-back ---
            while self.nextseqnum < total and (self.nextseqnum - self.base) < self.window_size:
                seq = self.nextseqnum % 256
                packet = self.create_data_packet(self.all_chunks[self.nextseqnum], seq)
                self.sndpkt[self.nextseqnum] = packet
                self.tx_send(packet)
                if self.base == self.nextseqnum:   # window was empty -> start timer
                    self.start_timer()
                self.nextseqnum += 1

            # --- Receive-ACK step ---
            ack_packet = self.tx_receive()
            if ack_transform is not None:
                ack_packet = ack_transform(ack_packet)

            ack_seq = self.valid_ack(ack_packet)
            if ack_seq is not None:
                acked = self.ack_to_abs(ack_seq)
                if acked is not None and acked >= self.base:
                    # Cumulative ACK: advance base past acked, prune buffered packets
                    for idx in range(self.base, acked + 1):
                        self.sndpkt.pop(idx, None)
                    self.base = acked + 1
                    if self.base == self.nextseqnum:
                        self.stop_timer()          # window drained
                    else:
                        self.start_timer()         # restart for new oldest unACKed
            # Corrupt/lost ACK -> ack_seq is None -> ignore (Lambda), no state change

            # --- Timeout step: Go-Back-window_size batch retransmit ---
            if self.timer_expired():
                if deadline is not None and time.time() >= deadline:
                    return
                for idx in range(self.base, self.nextseqnum):
                    self.tx_send(self.sndpkt[idx])
                self.start_timer()

        self.stop_timer()

    """ Runner Functions for each Scenario """
    ## Scenario 1: No loss/bit-errors
    def run_tx_sc1(self):
        self.pic_to_chunks()
        deadline = time.time() + helper.scenario_timeout
        self.gbn_send_loop(deadline=deadline)

    ## Scenario 2: ACK packet bit-error
    def run_tx_sc2(self, error_rate):
        self.pic_to_chunks()
        deadline = time.time() + helper.scenario_timeout
        self.gbn_send_loop(ack_transform=lambda ack: helper.inject_error(ack, error_rate),
                           deadline=deadline)

    ## Scenario 3: Data packet bit-error (injection is receiver-side)
    def run_tx_sc3(self):
        self.run_tx_sc1()

    ## Scenario 4: ACK packet loss
    def run_tx_sc4(self, loss_rate):
        self.pic_to_chunks()
        deadline = time.time() + helper.scenario_timeout
        self.gbn_send_loop(ack_transform=lambda ack: helper.inject_loss(ack, loss_rate),
                           deadline=deadline)

    ## Scenario 5: Data packet loss (injection is receiver-side)
    def run_tx_sc5(self):
        self.run_tx_sc1()
