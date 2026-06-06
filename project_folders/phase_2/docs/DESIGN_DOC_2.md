# Network Design Project – Phase Proposal & Design Document (Phase 2 of 5)

**Members:** | Himadri Saha | Himadri_Saha@student.uml.edu  
**GitHub Repo URL: https://github.com/himadri553/Network-Design-Grad-.git**  
**Phase:** 1 
**Submission Date: 6/6**  
**Version:** v1

## Overview of Code Architecture 
### main.py
- Entry point that initializes and runs each of the three scenarios in sequence
- Spins up sender and receiver as parallel threads using Python's threading module
- Logs [PLOT] timestamped markers around each scenario run for the plotter to consume
### sender.py
- Reads the image, splits it into fixed-size chunks, and assembles data packets with seq number, checksum, and length header
- Transmits each packet over UDP and blocks waiting for an ACK, retransmitting on timeout or on a corrupt/mismatched ACK
- Exposes a separate run_tx_scN() method per scenario where error injection behavior differs
### receiver.py
- Listens on a bound UDP socket for incoming data packets
- Validates each packet via checksum and sequence number check, then sends back an ACK carrying the appropriate seq number
- Assembles all accepted chunks in order and writes the reconstructed image to disk once transmission ends
### plotter.py
Parses [PLOT] tagged TX_START / TX_END lines from the log file, computes per-scenario completion times, and generates a matplotlib chart of completion time vs. run
### helper.py
Centralizes all shared configuration constants (file paths, port, packet size, buffer size) and provides the shared main_log_print() logging utility
### output_log.txt
Each module prefixes its lines with a tag ([MAIN], [SENDER], [RECEIVER]); [PLOT] tagged lines carry Unix timestamps that allow plotter.py to compute exact scenario durations

## Sender/receiver logic aligned with the RDT 2.2 FSM
- Sender splits the image into fixed-size chunks and initializes seq = 0
- Sender builds a data packet for the current chunk: alternates seq, computes a checksum over the header + payload, assembles [seq | checksum | length | data]
- Sender transmits the packet over UDP and begins waiting for an ACK
- Receiver receives the packet and extracts seq, checksum, length, data
- Receiver recomputes the checksum — if it doesn't match, the packet is corrupt
- If corrupt OR seq != expected_seq: Receiver sends an ACK carrying the seq number of the last correctly received packet (i.e. 1 - expected_seq), then goes back to listening — expected_seq does not change
- Sender receives the ACK, checks if it is corrupt or if its seq number doesn't match what was just sent — if either is true, sender retransmits the same packet (same seq, same data) and waits again — this duplicate ACK is RDT 2.2's substitute for a NAK
- If timeout: Sender gets no response within 5 seconds, retransmits the same packet and waits again
- If valid packet: Receiver appends the data to full_pic, sends an ACK carrying ack_seq = seq, flips expected_seq = 1 - expected_seq, and goes back to listening
- Sender receives the ACK, confirms it is not corrupt and that ack_seq matches the packet just sent — advances to the next chunk, flips seq, and repeats from the top for the next chunk
- Sender sends a sentinel/EOF packet after all chunks are transmitted to signal end of transmission
- Receiver detects the EOF or times out with no new packets, breaks out of the loop, concatenates all accepted chunks, and writes the output image to disk

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

## Error injection approach for Options 2 and 3
- After the sender receives an ACK from the receiver, before validating it, a random bit-flip is applied to the ACK bytes with a configurable probability p
- This is done by XOR-ing a random byte in the ACK packet with a non-zero mask, corrupting either the ack_seq or checksum field
- The sender then runs its normal corrupt-check — the tampered checksum will fail, causing the sender to treat the ACK as invalid and retransmit the last data packet
- This simulates the real-world case where the ACK is damaged in transit back to the sender
Recovery: the duplicate-ACK / retransmit mechanism in the RDT 2.2 sender FSM handles this with no additional logic needed

## Basic test plan and validation steps
- Image reconstruction: open the output .bmp visually and confirm no corrupted or missing pixel blocks appear. Verifies that a packet was accepted not out of order or skipped
- Drop one ACK response at the sender side and confirm the sender retransmits after the 5-second timeout without crashing. Verifies that the timeout path triggers retransmission and the protocol continues normally.
