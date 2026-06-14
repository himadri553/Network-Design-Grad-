"""
    Himadri Saha

    plotter.py
        - Script to create all plots

    Plot log format
        Every line: [PLOT] <unix_time>, <key>:<value>, ...
        A `chart:` tag separates the three datasets in one output_log.txt.
        One line per individual run; the plotter averages the runs per point.

    +---------+---------------------------------------------------------------+---------------------------+
    | Chart   | [PLOT] line fields                                            | Plot (x vs y)             |
    +---------+---------------------------------------------------------------+---------------------------+
    | Chart 1 | chart:1, sc:<1-5>, error_rate:<0.0-0.95>, duration:<sec>      | rate % vs avg time,       |
    |         |                                                               | 5 lines (Option 1-5)      |
    +---------+---------------------------------------------------------------+---------------------------+
    | Chart 2 | chart:2, sc:5, N:<1|2|5|10|20|50>, error_rate:0.10, dur:<sec> | window size vs avg time,  |
    |         |                                                               | Option 5 @ fixed 10% loss |
    +---------+---------------------------------------------------------------+---------------------------+
    | Chart 3 | chart:3, phase:<1-4>, error_rate:0.10, duration:<sec>         | phase vs avg time,        |
    |         |                                                               | same image @ fixed 10%    |
    +---------+---------------------------------------------------------------+---------------------------+

    Examples
        [PLOT] 1718412345.91, chart:1, sc:3, error_rate:0.25, duration:4.8210
        [PLOT] 1718412390.02, chart:2, sc:5, N:20, error_rate:0.10, duration:3.1147
        [PLOT] 1718412501.55, chart:3, phase:2, error_rate:0.10, duration:12.4400
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

def generic_line_plot(x_data, y_data, title, x_title, y_title, *args):
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

def generate_chart1():
    '''
    Chart 1: Error Rate (x-axis) over Average completion time (y-axis)
    Plot line expected: [PLOT] <time>, chart:1, sc:<1-5>, error_rate:<0.0-0.95>, duration:<sec>
    '''
    data = parse_plot_logs(['sc', 'error_rate', 'duration'])

    scenario_configs = {
        1: ('Option 1 - No errors',      helper.plot_path_sc1),
        2: ('Option 2 - ACK bit-error',  helper.plot_path_sc2),
        3: ('Option 3 - Data bit-error', helper.plot_path_sc3),
        4: ('Option 4 - ACK packet loss', helper.plot_path_sc4),
        5: ('Option 5 - Data packet loss', helper.plot_path_sc5),
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

        generic_line_plot(x_data, y_data, f"Go-Back-N protocol - {label}", "Error Rate (%)", "Avg Completion Time (s)")
        plt.savefig(helper.plot_path_chart1, 'Chart_1.png')
        plt.close()

def generate_chart2():
    '''
    Chart 2: Window Sizes (x-axis) over Average completion time (y-axis)
    Plot line expected: [PLOT] 1718412390.02, chart:2, sc:5, N:20, error_rate:0.10, duration:3.1147
    '''
    # N is the discriminating tag for chart:2 lines (chart:1/3 lines don't carry it)
    data = parse_plot_logs(['N', 'duration'])

    # Group durations by window size
    buckets = {}
    for d in data:
        buckets.setdefault(d['N'], []).append(d['duration'])

    # Build x and y aligned to the window_sizes list, averaging each bucket
    x_data = [w for w in helper.window_sizes if w in buckets]
    y_data = [sum(buckets[w]) / len(buckets[w]) for w in x_data]

    # x-axis is window size here, so set ticks to window_sizes (not rates)
    plt.figure()
    plt.plot(x_data, y_data, marker='o')
    plt.title("Go-Back-N protocol - Chart 2 (Window Size, 10% loss)")
    plt.xlabel("Window Size (N)")
    plt.ylabel("Avg Completion Time (s)")
    plt.xticks(helper.window_sizes)
    plt.tight_layout()
    plt.savefig(os.path.join(helper.plot_path_chart2, 'Chart_2.png'))
    plt.close()

def generate_chart3():
    '''
    Chart 3 (Bar graph): Phase (x-axis) over Average completion time (y-axis)
    Plot line expected: [PLOT] <time>, chart:3, phase:<1-4>, error_rate:0.10, duration:<sec>
    '''
    # phase is the discriminating tag for chart:3 lines (chart:1/2 lines don't carry it)
    data = parse_plot_logs(['phase', 'duration'])

    # Group durations by phase number
    buckets = {}
    for d in data:
        buckets.setdefault(d['phase'], []).append(d['duration'])

    # Build x and y aligned to phases 1-4, averaging each bucket
    phases = [p for p in [1, 2, 3, 4] if p in buckets]
    x_labels = [f"Phase {p}" for p in phases]
    y_data = [sum(buckets[p]) / len(buckets[p]) for p in phases]

    # Bar graph: phase on x-axis (categorical), avg completion time on y-axis
    plt.figure()
    plt.bar(x_labels, y_data)
    plt.title("Go-Back-N protocol - Chart 3 (Phase comparison, 10% loss)")
    plt.xlabel("Phase")
    plt.ylabel("Avg Completion Time (s)")
    plt.tight_layout()
    plt.savefig(os.path.join(helper.plot_path_chart3, 'Chart_3.png'))
    plt.close()

def run_plotter():
    '''
    Creates all plots after required scenarios are complete 
    '''
    pass