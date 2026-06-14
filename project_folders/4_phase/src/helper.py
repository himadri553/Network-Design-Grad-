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
plot_log_path       = os.path.join(os.path.dirname(__file__), '..', 'results', 'plot_log.txt')
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

# Go-Back-N window size: default and the Chart 2 sweep values
N = 10
window_sizes = [1, 2, 5, 10, 20, 50]

# Logging verbosity flag - set to False to silence [SENDER]/[RECEIVER] logs during timing runs
verbose_packet_logs = False
scenario_timeout = 120

""" Logger function """
def main_log_print(message):
    # Writes a message to the output log
    with open(log_path, 'a') as log_file:
        log_file.write(f"[MAIN] {message}\n")

""" Plot-log persistence """
# A [PLOT] line's identity is defined by its configuration fields: the chart /
# scenario / phase discriminator PLUS the error_rate and the window size. Two
# lines that match on all of these are the "same scenario run" and the new one
# replaces the old. (time and duration are results, never part of the identity.)
_IDENTITY_FIELDS = ('chart', 'sc', 'phase', 'error_rate', 'N', 'window_size', 'run')

def _plot_line_identity(plot_line):
    content = plot_line.split('[PLOT]', 1)[1].strip()
    segments = [s.strip() for s in content.split(',')]
    key_parts = []
    for seg in segments[1:]:          # skip the timestamp (first segment)
        if ':' not in seg:
            continue
        k, v = seg.split(':', 1)
        if k.strip() in _IDENTITY_FIELDS:   # error_rate + window size now keyed on
            key_parts.append((k.strip(), v.strip()))
    return tuple(sorted(key_parts))

def update_plot_log():
    # Merge the [PLOT] lines from output_log into the persistent plot_log:
    #   - output_log is cleared every run, so it only holds this run's results
    #   - in plot_log, an old line is cleared ONLY when a new line for that same
    #     scenario identity is ready; scenarios not re-run keep their old lines
    new_lines = []
    with open(log_path, 'r') as f:
        for line in f:
            if '[PLOT]' in line:
                new_lines.append(line.rstrip('\n'))
    if not new_lines:
        return

    # Collapse duplicates WITHIN this run: if the same config was run more than
    # once, only the last line for that identity is kept (it overrides the earlier).
    deduped = {}
    for line in new_lines:
        deduped[_plot_line_identity(line)] = line   # later lines overwrite earlier
    new_lines = list(deduped.values())

    refreshed = set(deduped.keys())

    kept = []
    if os.path.exists(plot_log_path):
        with open(plot_log_path, 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                if '[PLOT]' in line and _plot_line_identity(line) in refreshed:
                    continue              # cleared - new data ready for this scenario
                kept.append(line)

    with open(plot_log_path, 'w') as f:
        for line in kept + new_lines:
            f.write(line + '\n')

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