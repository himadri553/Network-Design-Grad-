"""
    Himadri Saha

    main.py
        - Main entry to this project, run this file to run the project
        - Chunk refers to picture data broken down into size helper.packet_size
        - Packet is the data sent from the sender with all the headers

    PHASE 4 TASKS:
    
        
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

def run2(error_rate=0.0):
    # Run Scenario 2 - Ack packet bit-error
    helper.main_log_print("Starting Scenario 2")
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

def run3(error_rate=0.0):
    # Run Scenario 3 - Data packet bit-error
    helper.main_log_print("Starting Scenario 3 ")
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

def run4(error_rate=0.0):
    # Run Scenario 4 
    helper.main_log_print("Starting Scenario 4 ")
    tx4 = sender()
    rx4 = receiver()
    tx_thread = threading.Thread(target=tx4.run_tx_sc4, args=(error_rate,))
    rx_thread = threading.Thread(target=rx4.run_rx_sc4)
    rx_thread.start()
    time.sleep(0.5)
    start = time.time()
    tx_thread.start()
    rx_thread.join()
    tx_thread.join()
    duration = time.time() - start
    helper.main_log_print(f"[PLOT] {time.time()}, sc:4, error_rate:{error_rate}, duration:{duration:.4f}")
    rx4.rx_socket.close()
    tx4.sender_socket.close()
    time.sleep(0.5)

def run5(error_rate=0.0):
    # Run Scenario 5 - Data packet loss
    helper.main_log_print("Starting Scenario 5")
    tx5 = sender()
    rx5 = receiver()
    tx_thread = threading.Thread(target=tx5.run_tx_sc5)
    rx_thread = threading.Thread(target=rx5.run_rx_sc5, args=(error_rate,))
    rx_thread.start()
    time.sleep(0.5)
    start = time.time()
    tx_thread.start()
    rx_thread.join()
    tx_thread.join()
    duration = time.time() - start
    helper.main_log_print(f"[PLOT] {time.time()}, sc:5, error_rate:{error_rate}, duration:{duration:.4f}")
    rx5.rx_socket.close()
    tx5.sender_socket.close()
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

    # Prompt the user to select scenario
    while True:
        user_input = input("Enter the scenario number: ")
        match user_input:
            case "1":
                run1()
                plotter.generate_scenario_plot()
                break
            case "2":
                for error_rate in rates:
                    run2(error_rate)
                plotter.generate_scenario_plot()
                break
            case "3":
                for error_rate in rates:
                    run3(error_rate)
                plotter.generate_scenario_plot()
                break
            case "4":
                for error_rate in rates:
                    run4(error_rate)
                plotter.generate_scenario_plot()
                break
            case "5":
                for error_rate in rates:
                    run5(error_rate)
                plotter.generate_scenario_plot()
                break
            case "test":
                run3()
                break
            case _: 
                print("Invalid scenario number, try again")

    
if __name__ == "__main__":
    main()