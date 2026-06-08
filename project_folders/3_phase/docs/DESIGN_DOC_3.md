# Network Design Project – Phase Proposal & Design Document (Phase 3 of 5)

**Members:** | Himadri Saha | Himadri_Saha@student.uml.edu  
**GitHub Repo URL: https://github.com/himadri553/Network-Design-Grad-.git**  
**Phase:** 3 
**Submission Date: 6/8**  
**Version:** v1

## Overview of Code Architecture 
### main.py
- Entry point that initializes and runs each of the five options in sequence
- Spins up sender and receiver as parallel threads using Python's threading module
- Logs [PLOT] timestamped markers around each scenario run for the plotter to consume
### sender.py
- Reads the image, splits it into fixed-size chunks, and assembles data packets with seq number, checksum, and length header
- Transmits each packet over UDP and waits for an ACK using an explicit countdown timer (start_timer/stop_timer/timer_expired); retransmits on timeout or corrupt/mismatched ACK, up to a max_retries cap
- Exposes a separate run_tx_scN() method per option (sc1–sc5) where error injection behavior differs
### receiver.py
- Listens on a bound UDP socket for incoming data packets
- Validates each packet via checksum and sequence number check, then sends back an ACK carrying the appropriate seq number
- Assembles all accepted chunks in order and writes the reconstructed image to disk once transmission ends
### plotter.py
Parses [PLOT] tagged lines (format: `[PLOT] time, sc:N, error_rate:X, duration:Y`) from the log file, computes per-option average completion times, and generates a matplotlib chart of completion time vs. error rate
### helper.py
Centralizes all shared configuration constants (file paths, port, packet size, buffer size) and provides the shared main_log_print() logging utility; also contains inject_error() (random bit-flip) and inject_loss() (random drop) helpers used by the scenario runners
### output_log.txt
Each module prefixes its lines with a tag ([MAIN], [SENDER], [RECEIVER]); [PLOT] tagged lines carry Unix timestamps that allow plotter.py to compute exact scenario durations

## Sender/receiver logic aligned with the RDT 3.0 FSM
- Sender splits the image into fixed-size chunks and initializes seq = 0
- Sender builds a data packet for the current chunk: alternates seq, computes a checksum over the header + payload, assembles [seq | checksum | length | data]
- Sender transmits the packet over UDP and begins waiting for an ACK
- Receiver receives the packet and extracts seq, checksum, length, data
- Receiver recomputes the checksum — if it doesn't match, the packet is corrupt
- If corrupt OR seq != expected_seq: Receiver sends an ACK carrying the seq number of the last correctly received packet (i.e. 1 - expected_seq), then goes back to listening — expected_seq does not change
- Sender receives the ACK, checks if it is corrupt or if its seq number doesn't match what was just sent — if either is true, sender retransmits the same packet (same seq, same data) and waits again
- If timeout: Sender's countdown timer expires after 5 seconds with no valid ACK, retransmits the same packet and restarts the timer (RDT 3.0 loss recovery); gives up after max_retries consecutive timeouts
- If valid packet: Receiver appends the data to full_pic, sends an ACK carrying ack_seq = seq, flips expected_seq = 1 - expected_seq, and goes back to listening
- Sender receives the ACK, confirms it is not corrupt and that ack_seq matches the packet just sent — advances to the next chunk, flips seq, and repeats from the top for the next chunk
- Once all chunks are transmitted the sender thread exits; the receiver times out after 5 seconds of silence, breaks out of the loop, concatenates all accepted chunks, and writes the output image to disk

## Packet format (seq number, checksum, payload, ACK format)
### Data Packet
| Field | Size | Position | Description |
|---|---|---|---|
| `seq` | 1 byte | `[0]` | Alternating sequence number — `0` or `1` |
| `checksum` | 1 byte | `[1]` | Sum of all header bytes (excluding checksum) + all payload bytes, mod 256 |
| `length` | 4 bytes | `[2:6]` | Payload size in bytes, big-endian |
| `data` | variable | `[6:6+length]` | Raw image chunk payload |

### ACK Packet
| Field | Size | Position | Description |
|---|---|---|---|
| `ack_seq` | 1 byte | `[0]` | Seq number of the last correctly received data packet |
| `checksum` | 1 byte | `[1]` | Sum of `ack_seq` byte, mod 256 |

## Error injection approach for Options 2–5
- **Option 2 (ACK bit-error):** After the sender receives an ACK, before validating it, inject_error() applies a random bit-flip with probability p — XOR-ing a random byte in the ACK packet, corrupting either ack_seq or checksum. The sender's corrupt-check fails and it retransmits.
- **Option 3 (data bit-error):** The receiver applies inject_error() to the incoming data packet before validation. A corrupted checksum causes the receiver to send a NAK (duplicate ACK), and the sender retransmits.
- **Option 4 (ACK loss):** After the sender receives an ACK, inject_loss() drops it entirely with probability p (returns None). The sender sees no valid ACK, the countdown timer expires, and it retransmits.
- **Option 5 (data loss):** The receiver applies inject_loss() to the incoming data packet. If dropped, no ACK is sent; the sender's countdown timer expires and it retransmits.
Recovery: the countdown-timer / retransmit mechanism in the RDT 3.0 sender FSM handles all four cases with no additional logic needed

## Basic test plan and validation steps
- Image reconstruction: open the output image visually and confirm no corrupted or missing pixel blocks appear. Verifies that packets were accepted in order and not skipped
- Run each of the five options across error/loss rates 0–95% and confirm each run terminates and logs a [PLOT] line. Verifies that the timeout/retransmit path and max_retries cap prevent hangs at all rates
- Drop one ACK response at the sender side and confirm the sender retransmits after the 5-second countdown timer expires without crashing. Verifies that the timeout path triggers retransmission and the protocol continues normally.
