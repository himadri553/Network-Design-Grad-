"""
    Himadri Saha

    plotter.py
        - Script to create all plots
        - Plot log format
            [PLOT] time, sc:1, error_rate:0.5

    Outline:
        

"""
import os
import re
import matplotlib.pyplot as plt
import helper

rates = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]

def parse_plot_logs(tags):
    """
        Find data based on tags, returns the corresponding data
        Expected plot log: [PLOT] time, <tag1>:data1, <tag2>:data1

        inputs:  tags - list of tag names to extract e.g. ['sc', 'error_rate', 'duration']
        outputs: list of dicts, one per matching line e.g. [{'time': 1234.5, 'sc': 1, ...}, ...]
    """
    results = []

    with open(helper.log_path, 'r') as f:
        for line in f:
            if '[PLOT]' not in line:
                continue

            # Extract everything after [PLOT]
            plot_content = line.split('[PLOT]')[1].strip()

            # First segment is the timestamp, rest are key:value pairs
            segments = [s.strip() for s in plot_content.split(',')]
            try:
                parsed = {'time': float(segments[0])}
            except ValueError:
                continue

            for segment in segments[1:]:
                if ':' not in segment:
                    continue
                key, value = segment.split(':', 1)
                key, value = key.strip(), value.strip()
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                parsed[key] = value

            # Only include lines that contain all requested tags
            if all(tag in parsed for tag in tags):
                results.append({k: parsed[k] for k in ['time'] + tags})

    return results

def generic_plot(x_data, y_data, title, x_title, y_title, *args):
    # args: additional (x_data, y_data, label) tuples for extra lines
    plt.figure()
    plt.plot(x_data, y_data)
    for i in range(0, len(args) - 1, 3):
        plt.plot(args[i], args[i+1], label=args[i+2])
    plt.title(title)
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.xticks(rates, rotation=45)
    plt.legend()
    plt.tight_layout()

def generate_scenario_plot():
    ''' generates the plot corresponding with each scenario '''
    data = parse_plot_logs(['sc', 'error_rate', 'duration'])

    scenario_configs = {
        1: ('Option 1 - No errors',      helper.plot_path_sc1),
        2: ('Option 2 - ACK bit-error',  helper.plot_path_sc2),
        3: ('Option 3 - Data bit-error', helper.plot_path_sc3),
    }

    for sc, (label, save_path) in scenario_configs.items():
        sc_data = [d for d in data if d['sc'] == sc]
        if not sc_data:
            continue

        # Group durations by rate percentage bucket
        buckets = {}
        for d in sc_data:
            rate_pct = round(d['error_rate'] * 100)
            buckets.setdefault(rate_pct, []).append(d['duration'])

        # Build x and y aligned to the rates list, averaging each bucket
        x_data = [r for r in rates if r in buckets]
        y_data = [sum(buckets[r]) / len(buckets[r]) for r in x_data]

        generic_plot(x_data, y_data, f"RDT 2.2 - {label}", "Error Rate (%)", "Avg Completion Time (s)")
        plt.savefig(os.path.join(save_path, 'completion_time.png'))
        plt.close()

def generate_combined_plot():
    ''' called after all scenarios are finished '''
    pass

def run_plotter():
    pass