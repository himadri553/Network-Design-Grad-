"""
    Himadri Saha

    main.py
        - Main entry to this project, run this file to run the project
        - Chunk refers to picture data broken down into size helper.packet_size
        - Packet is the data sent from the sender with all the headers

    PHASE 4 TASKS:
    
        
    TODO:
        - Make it so that plot logs are saved separately, only reset for each run 
        - Add all plot logs
        - Create all runs and plots

"""

""" Imports """
import threading
from socket import *
import time
import os
from sender import SENDER as sender
from receiver import RECEIVER as receiver
import helper
import plotter

""" Scenario Thread functions """
def run_scenario(scenario, error_rate=0.0, window_size=10):
    # Combined runner for Scenarios 1-5 (same structure as run1-run5 above).
    # error_rate is applied on the tx/ACK side for Options 2 & 4, on the rx/DATA
    # side for Options 3 & 5, and ignored for Option 1.
    helper.main_log_print(f"Starting Scenario {scenario}")
    tx = sender(window_size)
    rx = receiver(window_size)

    # Per-scenario tx/rx runner + which side receives error_rate
    tx_runners = {
        1: (tx.run_tx_sc1, ()),
        2: (tx.run_tx_sc2, (error_rate,)),
        3: (tx.run_tx_sc3, ()),
        4: (tx.run_tx_sc4, (error_rate,)),
        5: (tx.run_tx_sc5, ()),
    }
    rx_runners = {
        1: (rx.run_rx_sc1, ()),
        2: (rx.run_rx_sc2, ()),
        3: (rx.run_rx_sc3, (error_rate,)),
        4: (rx.run_rx_sc4, ()),
        5: (rx.run_rx_sc5, (error_rate,)),
    }
    tx_target, tx_args = tx_runners[scenario]
    rx_target, rx_args = rx_runners[scenario]

    # Start Threads
    tx_thread = threading.Thread(target=tx_target, args=tx_args)
    rx_thread = threading.Thread(target=rx_target, args=rx_args)
    rx_thread.start()
    time.sleep(0.5)
    start = time.time()
    tx_thread.start()
    rx_thread.join()
    tx_thread.join()
    duration = time.time() - start
    
    # Output logs for plotter
    helper.main_log_print(f"[PLOT] {time.time()}, sc:5, error_rate:{error_rate}, duration:{duration:.4f}")
    helper.main_log_print(f"[PLOT] {time.time()}, chart:2, N:{window_size}, duration:{duration:.4f}")
    helper.main_log_print(f"[PLOT] {time.time()}, chart:3, phase:4, duration:{duration:.4f}")
    
    # Close Threads
    rx.rx_socket.close()
    tx.sender_socket.close()
    time.sleep(0.5)

def run_recovery_demo():
    # R13: demonstrate Phase 4 with and without loss recovery active, using Option 5
    # (data packet loss). At 0% loss the recovery path never triggers; at 30% loss the
    # countdown timer + Go-Back-N retransmit kick in. Both must reconstruct the image.
    helper.main_log_print("Recovery demo: WITHOUT recovery (0% loss)")
    run_scenario(5, 0.0, 10)
    helper.main_log_print("Recovery demo: WITH recovery (30% loss)")
    run_scenario(5, 0.30, 10)

""" Entry """
def main():
    # Clear output files
    with open(helper.log_path, 'w') as log_file:
        pass
    helper.main_log_print("Clearing all output logs")

    # R17: silence per-packet [SENDER]/[RECEIVER] debug logs during timing sweeps
    helper.verbose_packet_logs = False

    ## Run each scenario 5 times with their corresponding rates
    rates = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 
             0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    num_runs = 5

    # Prompt the user to select scenario
    while True:
        user_input = input("Enter the scenario number or run_all: ")
        match user_input:
            case "run_all":
                for error_rates in rates:
                    run1()
                    run2(error_rates)
                    run3(error_rates)
                    run4(error_rates)
                    run5(error_rates)
                plotter.run_plotter()
                break
            case "1":
                run1()
                break
            case "2":
                for error_rate in rates:
                    run2(error_rate)
                break
            case "3":
                for error_rate in rates:
                    run3(error_rate)
                break
            case "4":
                for error_rate in rates:
                    run4(error_rate)
                break
            case "5":
                for error_rate in rates:
                    run5(error_rate)
                break
            case "demo":
                run_recovery_demo()
                break
            case "test":
                run_scenario(2, 0.0, 1)
                break
            case "plot":
                break
            case _: 
                print("Invalid scenario number, try again")
    
    # Update plots
    plotter.run_plotter()

    
if __name__ == "__main__":
    main()