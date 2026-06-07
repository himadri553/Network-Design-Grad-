"""
    Himadri Saha

    main.py
        - Main entry to this project, run this file to run the project
        - Chunk refers to picture data broken down into size helper.packet_size
        - Packet is the data sent from the sender with all the headers

    Phase 2 Tasks:
        - Plots
            - x-axis: loss/error rate (%)
            - y-axis: completion time in seconds (average of runs)
        - Deliverables 
            - Demo Video

    TODO:
        - 
        
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
def run1():
    # Run Scenario 1 - No bit-error
    helper.main_log_print("Starting Scenario 1")
    tx = sender()
    rx = receiver()
    tx_thread = threading.Thread(target=tx.run_tx_sc1)
    rx_thread = threading.Thread(target=rx.run_rx_sc1)
    rx_thread.start()
    time.sleep(0.5)
    start = time.time()
    tx_thread.start()
    rx_thread.join()
    tx_thread.join()
    duration = time.time() - start
    helper.main_log_print(f"[PLOT] {time.time()}, sc:1, error_rate:0.0, duration:{duration:.4f}")
    rx.rx_socket.close()
    tx.sender_socket.close()
    time.sleep(0.5)

def run2(error_rate):
    # Run Scenario 2 - Ack packet bit-error
    tx2 = sender()
    rx2 = receiver()
    tx_thread = threading.Thread(target=tx2.run_tx_sc2, args=(error_rate,))
    rx_thread = threading.Thread(target=rx2.run_rx_sc2)
    rx_thread.start()
    time.sleep(0.5)
    start = time.time()
    tx_thread.start()
    rx_thread.join()
    tx_thread.join()
    duration = time.time() - start
    helper.main_log_print(f"[PLOT] {time.time()}, sc:2, error_rate:{error_rate}, duration:{duration:.4f}")
    rx2.rx_socket.close()
    tx2.sender_socket.close()
    time.sleep(0.5)

def run3(error_rate):
    # Run Scenario 3 - Data packet bit-error
    tx3 = sender()
    rx3 = receiver()
    tx_thread = threading.Thread(target=tx3.run_tx_sc3)
    rx_thread = threading.Thread(target=rx3.run_rx_sc3, args=(error_rate,))
    rx_thread.start()
    time.sleep(0.5)
    start = time.time()
    tx_thread.start()
    rx_thread.join()
    tx_thread.join()
    duration = time.time() - start
    helper.main_log_print(f"[PLOT] {time.time()}, sc:3, error_rate:{error_rate}, duration:{duration:.4f}")
    rx3.rx_socket.close()
    tx3.sender_socket.close()
    time.sleep(0.5)

""" Entry """
def main():
    # Clear output files
    with open(helper.log_path, 'w') as log_file:
        pass
    helper.main_log_print("Clearing all output logs")

    ## Run each scenario 5 times with their corresponding rates
    rates = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 
             0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    num_runs = 5

    # run1()
    # plotter.generate_scenario_plot()

    for error_rate in rates:
        run2(error_rate)
    plotter.generate_scenario_plot()

    '''
    for error_rate in rates:
        run3(error_rate)
    plotter.generate_scenario_plot()
    '''


if __name__ == "__main__":
    plotter.generate_scenario_plot()