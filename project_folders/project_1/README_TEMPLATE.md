# Network Design Project Phase 1 – Team 

<!-- ![language](https://img.shields.io/badge/language-python-blue) -->

## Overview
This phase implements a RDT 1.0 protocol

## Team
| Himadri Saha | Himadri_Saha@student.uml.edu | Team Lead |
|---|---|---|
|  |  |  |
|  |  |  |

## Demo Video (submission)
- **Private YouTube link:** *(submit via Blackboard)*  
- **Timestamped outline:** *(mm:ss → scenario)*

---

## Repository Structure
```
src/              # sender, receiver, protocol utilities
scripts/          # experiment runner, plotting utilities
docs/             # design documents and diagrams
results/          # CSV + plots generated from experiments
requirements.txt/ # Python Dependencies, run `pip install -r requirements.txt`
README.md

Optional (recommended):
- `tests/`
- `data/`
```

## Requirements
- Language/runtime: (Python 3.13.12)
- OS tested: Windows 11
- Dependencies:
  - Python: `pip install -r requirements.txt`

---

## Standard CLI Interface (required)
Your program must support these standardized flags so the TA can run and grade consistently.

### Receiver (required flags)
- `--port <int>`: UDP port to bind
- `--out <path>`: output file path to write received bytes
- `--seed <int>`: RNG seed (default: 0)
- `--log-level <debug|info|warning|error>` (default: info)

### Sender (required flags)
- `--host <ip/hostname>`: receiver host
- `--port <int>`: receiver port
- `--file <path>`: input file to send
- `--seed <int>`: RNG seed (default: 0)
- `--log-level <debug|info|warning|error>` (default: info)

### Injection flags (if required by phase)
- `--data-error-rate <float 0..1>` (default: 0)
- `--ack-error-rate <float 0..1>` (default: 0)
- `--data-loss-rate <float 0..1>` (default: 0)
- `--ack-loss-rate <float 0..1>` (default: 0)

### Timing / windowing flags (if required by phase)
- `--timeout-ms <int>` (default: 40)
- `--window-size <int>` (default: 10)

**Notes**
- “Rates” are probabilities per packet/ACK.
- Timing experiments must disable verbose logging (use `--log-level warning` or `error`).

---

## Quick Start (Run Locally)
### Select Scenario Configuration
```bash
python src/receiver.py --port 9000 --out results/received.bin --seed 0
```
### Start Scenario
```bash
python src/receiver.py --port 9000 --out results/received.bin --seed 0
```
---

## Required Demo Scenarios (Current Phase)
Provide the exact commands used to demonstrate each required scenario.

### Scenario 1: __________
Receiver:
```bash
...
```
Sender:
```bash
...
```
Expected behavior:
- ...

### Scenario 2: __________
...

---

## Figures / Plots (if required by phase)
### Reproduce experiment runs
Your repo must include a script that can reproduce required sweeps and output CSV.

Example:
```bash
python scripts/run_experiments.py --phase 4 --out results/phase4.csv
```

### Generate plots
Example:
```bash
python scripts/plot_results.py --in results/phase4.csv --out results/phase4.png
```

### Results files
- `results/phaseX.csv`
- `results/phaseX.png`

---

## Known Issues / Limitations
List any limitations honestly.

---

## Academic Integrity / External Tools
Debugging tools (IDE debugger, logging) and LLMs may be used for learning and troubleshooting. Final implementation decisions and understanding are our own.
