"""
    Himadri Saha

    plotter.py
        - Script to create all plots

"""
import re
import matplotlib.pyplot as plt
import helper

def parse_plot_logs():
    # Returns list of completion times for each scenario
    # { sc: [completion_time, ...] }
    results = {}
    pending_start = {}

    with open(helper.log_path, 'r') as f:
        for line in f:
            if '[PLOT]' not in line:
                continue

            sc_match  = re.search(r'sc=(\d+)', line)
            t_match   = re.search(r'@ ([\d.]+)', line)
            if not sc_match or not t_match:
                continue

            sc = int(sc_match.group(1))
            t  = float(t_match.group(1))

            if 'TX_START' in line:
                pending_start[sc] = t

            elif 'TX_END' in line and sc in pending_start:
                duration = t - pending_start.pop(sc)
                results.setdefault(sc, []).append(duration)

    return results

def generate_plot():
    results = parse_plot_logs()

    plt.figure()

    # Scenario 1
    if 1 in results:
        runs = range(1, len(results[1]) + 1)
        plt.plot(runs, results[1], marker='o', label='Scenario 1 (no errors)')

    plt.title("RDT 2.2 Completion Time")
    plt.xlabel("Run")
    plt.ylabel("Completion Time (s)")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    generate_plot()