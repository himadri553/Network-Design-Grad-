"""
    Himadri Saha

    helper.py
        - Contains helper functions that is used by main

    TODO:

"""

""" Imports """
import os

""" Vars """
log_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'output_log.txt')
pic_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'bos_skyline.bmp')
output_pic_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'output_pic.bmp')
receiver_name = 'localhost'
receiver_port = 12000
buffer_size = 2048
packet_size = 1024

""" Logger function """
def main_log_print(message):
    # Writes a message to the output log
    with open(log_path, 'a') as log_file:
        log_file.write(f"[MAIN] {message}\n")

""" Error Injection """
def inject_error(packet, error_rate):
    import random
    if packet is None:
        return None
    if random.random() < error_rate:
        packet = bytearray(packet)
        byte_index = random.randint(0, len(packet) - 1)
        bit_index  = random.randint(0, 7)
        packet[byte_index] ^= (1 << bit_index)
        return bytes(packet)
    return packet