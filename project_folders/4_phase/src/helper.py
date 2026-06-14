"""
    Himadri Saha

    helper.py
        - Contains helper functions that is used by main

    TODO:

"""

""" Imports """
import os

""" Vars """
# Paths 
log_path            = os.path.join(os.path.dirname(__file__), '..', 'results', 'output_log.txt')
pic_path            = os.path.join(os.path.dirname(__file__), '..', 'results', 'bos_skyline.JPG')
output_pic_path     = os.path.join(os.path.dirname(__file__), '..', 'results', 'output_pic.JPG')
plot_path_test      = os.path.join(os.path.dirname(__file__), '..', 'results', 'plots', 'tests')
plot_path_chart1    = os.path.join(os.path.dirname(__file__), '..', 'results', 'plots', 'Chart 1')
plot_path_chart2    = os.path.join(os.path.dirname(__file__), '..', 'results', 'plots', 'Chart 2')
plot_path_chart3    = os.path.join(os.path.dirname(__file__), '..', 'results', 'plots', 'Chart 3')
for _p in [plot_path_test, plot_path_chart1, plot_path_chart2, plot_path_chart3]:
    os.makedirs(_p, exist_ok=True)

# Ports
receiver_name = 'localhost'
receiver_port = 12000
buffer_size = 2048
packet_size = 1024

# Logging verbosity flag - set to False to silence [SENDER]/[RECEIVER] logs during timing runs
verbose_packet_logs = False
scenario_timeout = 120

# Window stuff (phase 4)
window_sizes = [1, 2, 5, 10, 20, 50]

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

""" Loss Injection """
def inject_loss(packet, loss_rate):
    import random
    if packet is None:
        return None
    if random.random() < loss_rate:
        return None
    return packet