"""
    Himadri Saha

    old_plotter.py
        - Script to create all plots

    NOTES:
        - parse_plot_logs()
            * returns all data from plot logs
        - generate_plot() 
            * called in main after scenario runs
        - generate_combined_plot()
            * called after all scenarios are finished

"""
import os
import re
import matplotlib.pyplot as plt
import helper

rates = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]

def parse_plot_logs():
    # Returns per-scenario matrix: { sc: { rate_pct: [durations] } }
    results = {}
    pending_start = {}  # sc -> (er_pct, start_time)

    with open(helper.log_path, 'r') as f:
        for line in f:
            if '[PLOT]' not in line:
                continue

            sc_match = re.search(r'sc=(\d+)', line)
            er_match = re.search(r'er=([\d.]+)', line)
            t_match  = re.search(r'@ ([\d.]+)', line)
            if not sc_match or not t_match:
                continue

            sc     = int(sc_match.group(1))
            t      = float(t_match.group(1))
            er_pct = round(float(er_match.group(1)) * 100) if er_match else 0

            if 'TX_START' in line:
                pending_start[sc] = (er_pct, t)

            elif 'TX_END' in line and sc in pending_start:
                start_er_pct, start_t = pending_start.pop(sc)
                duration = t - start_t
                results.setdefault(sc, {}).setdefault(start_er_pct, []).append(duration)

    return results

def generate_plot():
    results = parse_plot_logs()

    scenario_configs = [
        (1, 'Option 1 - No errors',      helper.plot_path_sc1),
        (2, 'Option 2 - ACK bit-error',  helper.plot_path_sc2),
        (3, 'Option 3 - Data bit-error', helper.plot_path_sc3),
    ]

    # Save one individual chart per scenario to its folder
    for sc, label, save_path in scenario_configs:
        if sc not in results:
            continue

        sc_data = results[sc]
        times   = [sc_data.get(r, []) for r in rates]
        plot_rates = [rates[i] for i, t in enumerate(times) if t]
        plot_avg   = [sum(t) / len(t) for t in times if t]

        plt.figure()
        plt.plot(plot_rates, plot_avg, marker='o', label=label)
        plt.title(f"RDT 2.2 Completion Time - {label}")
        plt.xlabel("Error Rate (%)")
        plt.ylabel("Avg Completion Time (s)")
        plt.xticks(rates, rotation=45)
        plt.xlim(-2, 97)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(save_path, 'completion_time.png'))
        plt.close()

    # Save combined chart with all 3 lines to plots root
    combined_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'plots')
    plt.figure()
    for sc, label, _ in scenario_configs:
        if sc not in results:
            continue
        sc_data    = results[sc]
        times      = [sc_data.get(r, []) for r in rates]
        plot_rates = [rates[i] for i, t in enumerate(times) if t]
        plot_avg   = [sum(t) / len(t) for t in times if t]
        plt.plot(plot_rates, plot_avg, marker='o', label=label)

    plt.title("RDT 2.2 Completion Time vs Error Rate")
    plt.xlabel("Error Rate (%)")
    plt.ylabel("Avg Completion Time (s)")
    plt.xticks(rates, rotation=45)
    plt.xlim(-2, 97)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(combined_path, 'completion_time_combined.png'))
    plt.close()

if __name__ == "__main__":
    generate_plot()
