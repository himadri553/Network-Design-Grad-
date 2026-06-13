# Network Design Project – Phase Proposal & Design Document (Phase 4 of 5)

**Members:** | Himadri Saha | Himadri_Saha@student.uml.edu  
**GitHub Repo URL: https://github.com/himadri553/Network-Design-Grad-.git**  
**Phase:** 4 
**Submission Date: 6/8**  
**Version:** v1

## Overview of Code Architecture
### main.py
- Entry point that initializes and runs each of the five options in sequence
- Spins up sender and receiver as parallel threads using Python's threading module
- Passes a fixed window size `N` (default 10) to both sender and receiver so they operate on the same pipeline depth
- Logs [PLOT] timestamped markers around each scenario run for the plotter to consume
- Drives three experiment sweeps: the per-option error/loss rate sweep (0–95% in 5% steps, Chart 1), the window-size sweep at a fixed 10% rate (`N` = 1, 2, 5, 10, 20, 50, Chart 2), and the cross-phase comparison run at a fixed loss/bit-error rate (Chart 3)

### sender.py  
- Reads the image, splits it into fixed-size chunks, and assembles data packets with seq number, checksum, and length header
- Maintains the Go-Back-N sender state: `base` (sequence number of the oldest unacknowledged packet), `nextseqnum` (sequence number of the next packet to send), and an `sndpkt` buffer holding every packet currently in flight (sent, not yet ACKed)
- Pipelines transmission: sends a new packet whenever `(nextseqnum - base) mod 256 < N`, i.e. fewer than `N` packets are outstanding
- Runs a single countdown timer tied to `base` (`start_timer`/`stop_timer`/`timer_expired`); on timeout, retransmits every buffered packet from `base` through `nextseqnum-1` — the Go-Back-N batch retransmit — and restarts the timer
- Exposes a separate `run_tx_scN()` method per option (sc1–sc5) where the error/loss injection applied to received ACKs differs

### receiver.py
- Listens on a bound UDP socket for incoming data packets
- Tracks a single `expected_seq` counter; delivers a chunk and sends a cumulative ACK only when the incoming packet is uncorrupted **and** carries `seq == expected_seq`
- On a corrupted packet or one with `seq != expected_seq` (out-of-order), discards it and re-sends the cumulative ACK for the last correctly received packet (`(expected_seq - 1) mod 256`), without advancing `expected_seq` — this is the GBN receiver's "discard and re-ACK" default behavior
- Assembles all in-order chunks and writes the reconstructed image to disk once transmission ends
- Exposes a separate `run_rx_scN()` method per option (sc1–sc5) where the error/loss injection applied to incoming data packets differs

### plotter.py
- Parses [PLOT] tagged lines (format: `[PLOT] time, sc:N, error_rate:X, duration:Y`) from the log file
- **Chart 1**: for each of the 5 options, computes the average completion time at each loss/error rate from 0–95% (5% increments, 5 runs per point) and plots all 5 options on one chart against the same x-axis
- **Chart 2**: at a fixed 10% loss probability, computes the average completion time for window sizes `[1, 2, 5, 10, 20, 50]` and plots completion time vs. window size
- **Chart 3**: at a fixed loss/bit-error rate (10%), computes the average completion time for Phase 1–4 (same transfer image) and plots completion time vs. phase

### helper.py
- Centralizes shared configuration constants: file paths, port, packet size, buffer size, and the default window size `N = 10` used as the baseline for Chart 1 and Chart 3
- Provides the shared `main_log_print()` logging utility
- Contains `inject_error()` (random bit-flip) and `inject_loss()` (random drop) helpers used by the scenario runners — unchanged from Phase 3

### output_log.txt
Each module prefixes its lines with a tag ([MAIN], [SENDER], [RECEIVER]); [PLOT] tagged lines carry Unix timestamps that allow plotter.py to compute exact scenario durations

## Sender/receiver logic aligned with the Go-Back-N FSM
This follows the extended GBN sender/receiver FSMs (Kurose/Ross Figures 3.19–3.22).

- Sender splits the image into fixed-size chunks and initializes `base = 0`, `nextseqnum = 0`
- While `(nextseqnum - base) mod 256 < N` (window not full), sender builds a data packet for chunk `nextseqnum` (seq, checksum over header+payload, length, payload), stores it in `sndpkt[nextseqnum]`, transmits it over UDP, and increments `nextseqnum = (nextseqnum + 1) mod 256`; the first transmission into an empty window (`base == nextseqnum` before sending) starts the countdown timer — this repeats back-to-back until up to `N` packets are in flight, with no need to wait for an ACK in between
- Once the window is full (`(nextseqnum - base) mod 256 == N`), the sender holds off sending further packets until an ACK frees up space
- Receiver receives a packet and extracts seq, checksum, length, data, then recomputes the checksum to check for corruption
- If the packet is corrupt OR `seq != expected_seq` (out-of-order/duplicate): Receiver discards it and sends an ACK carrying `ack_seq = (expected_seq - 1) mod 256` — a duplicate cumulative ACK for the last in-order packet it actually delivered — then goes back to listening; `expected_seq` does not change
- If the packet is uncorrupted and in-order (`seq == expected_seq`): Receiver appends the data to `full_pic`, sends an ACK carrying `ack_seq = expected_seq`, increments `expected_seq = (expected_seq + 1) mod 256`, and goes back to listening
- Sender receives an ACK and checks if it is corrupt — if corrupt, ignores it (Λ transition) and keeps waiting with no state change
- If the ACK is uncorrupted: sender reads the cumulative `ack_seq` and sets `base = (ack_seq + 1) mod 256`, freeing up window space so the sending step above can produce more packets; if `base == nextseqnum` (window now empty) the timer is stopped, otherwise the timer is restarted for the new oldest unacked packet
- If timeout: sender's countdown timer expires after `timeout_interval` seconds with no cumulative ACK advancing `base` — sender retransmits every buffered packet `sndpkt[base] … sndpkt[nextseqnum-1]` in order (Go-Back-N batch retransmit) and restarts the timer
- Once the sender has transmitted every chunk and every cumulative ACK has caught up (`base == nextseqnum`), the sender thread exits; the receiver times out after 5 seconds of silence, breaks out of its loop, concatenates `full_pic` in order, and writes the reconstructed image to disk

## Packet format (seq number, checksum, payload, ACK format)
### Data Packet
| Field | Size | Position | Description |
|---|---|---|---|
| `seq` | 1 byte | `[0]` | Sequence number, `0–255`, increments and wraps modulo 256 |
| `checksum` | 1 byte | `[1]` | Sum of all header bytes (excluding checksum) + all payload bytes, mod 256 |
| `length` | 4 bytes | `[2:6]` | Payload size in bytes, big-endian |
| `data` | variable | `[6:6+length]` | Raw image chunk payload |

A 1-byte sequence field gives a 256-value sequence space, which satisfies the GBN requirement of `seq space ≥ N + 1` for every window size in the Chart 2 sweep (`N ≤ 50`).

### ACK Packet
| Field | Size | Position | Description |
|---|---|---|---|
| `ack_seq` | 1 byte | `[0]` | **Cumulative** ACK — sequence number of the highest-numbered packet received correctly and in-order so far |
| `checksum` | 1 byte | `[1]` | Sum of `ack_seq` byte, mod 256 |

Unlike Phase 3's alternating 0/1 ACK, `ack_seq` here acknowledges *all* packets up through and including `ack_seq`, allowing the sender to advance `base` past multiple packets on a single ACK.

## Window management / buffering strategy
- The sender's window is the half-open range of sequence numbers `[base, base + N)` (mod 256), split into two regions:
  - `[base, nextseqnum)` — packets already sent, buffered in `sndpkt`, awaiting ACK
  - `[nextseqnum, base + N)` — usable space, not yet sent
- `sndpkt` is a dict/list keyed by sequence number, populated when a packet is first transmitted and pruned (entries with seq `< base`, mod-aware) whenever `base` advances on a cumulative ACK
- Because `seq` wraps at 256 and `N ≤ 50`, all window-membership and "is this seq within the window" checks are done with modular arithmetic (`(x - base) mod 256`) rather than plain integer comparison
- The receiver does not buffer out-of-order packets — it only tracks `expected_seq` and discards anything that doesn't match, consistent with the basic GBN receiver (no receiver-side reordering buffer)
- `N` is read once from `helper.py` at startup and held fixed for the duration of a run; the window-size sweep (Chart 2) re-runs the whole transfer once per `N` value with a fresh sender/receiver pair

## Timeout and retransmission design
- A single countdown timer is associated with `base` (the oldest unacknowledged packet), implemented with the same `start_timer`/`stop_timer`/`timer_expired` pattern as Phase 3 (`timeout_interval` seconds, polled via a short-timeout `recvfrom`)
- Timer transitions:
  - **Start**: when a packet is sent and the window was previously empty (`base == nextseqnum` before sending)
  - **Restart**: on any valid cumulative ACK that advances `base` but leaves packets still outstanding (`base != nextseqnum` after the update)
  - **Stop**: on a valid cumulative ACK that brings `base == nextseqnum` (window fully drained)
  - **Expire**: if no valid, non-corrupt cumulative ACK advances `base` within `timeout_interval` seconds — the sender retransmits the *entire* outstanding window `sndpkt[base] … sndpkt[nextseqnum-1]` and restarts the timer
- Per the assignment note ("don't set your timeout too high"), `timeout_interval` is kept short relative to the round-trip time so that pipelining benefits aren't masked by long stalls; the exact value is tuned empirically and is one of the observations called for in the window-size/timeout analysis (R20)
- A `scenario_timeout` deadline (overall wall-clock cap per scenario run) is retained from Phase 3 to guarantee every run terminates and logs a `[PLOT]` line even at very high loss/error rates, satisfying the "no hangs at 0–95%" requirement

## Error and loss injection approach for Options 2–5
- **Option 2 (ACK packet bit-error):** Every ACK the sender receives is passed through `inject_error()` before the corrupt-check, with probability `p` XOR-ing a random byte (`ack_seq` or `checksum`). A corrupted ACK fails `notcorrupt()` and is dropped via the Λ transition — `base` does not advance for that ACK. Recovery comes from either a later, uncorrupted cumulative ACK for the same or a higher `seq` getting through, or — if every ACK in the window is corrupted — the countdown timer expiring and the sender retransmitting the full outstanding window.
- **Option 3 (Data packet bit-error):** The receiver applies `inject_error()` to each incoming data packet before validation. A corrupted checksum sends the receiver down the `default` branch: it discards the packet and re-sends the cumulative ACK for `expected_seq - 1`. The sender treats this as a duplicate ACK (it doesn't advance `base`) and, after `timeout_interval`, retransmits `sndpkt[base] … sndpkt[nextseqnum-1]` — the corrupted packet (and everything sent after it) is resent.
- **Option 4 (ACK packet loss):** After the sender receives an ACK, `inject_loss()` drops it entirely with probability `p` (returns `None`). With no ACK delivered, `base` cannot advance from that packet's ACK; recovery is identical to Option 2 — either a subsequent cumulative ACK covers the gap, or the timer expires and the full window is retransmitted.
- **Option 5 (Data packet loss):** The receiver applies `inject_loss()` to each incoming data packet (drop with probability `p`, no ACK sent at all for that packet). Any later, out-of-order packets that do arrive hit the receiver's `default` branch (duplicate ACK for `expected_seq - 1`), and the sender's countdown timer eventually expires, triggering a Go-Back-N retransmission of the whole outstanding window starting from the dropped packet.

**Recovery (common to all four options):** `base` only ever advances on an uncorrupted, in-order cumulative ACK. Every failure mode — corrupted ACK, lost ACK, corrupted data, lost data — collapses to the same recovery path: the single timer on `base` expires and the sender resends every packet from `base` to `nextseqnum-1`. No per-scenario recovery logic is needed beyond the shared GBN timeout/retransmit mechanism.

## Basic test plan and validation steps
- **Image reconstruction:** open the output image visually and confirm no corrupted or missing pixel blocks appear. Verifies that `expected_seq`-gated delivery on the receiver only accepts in-order data and that Go-Back-N retransmission eventually fills every gap.
- **Pipelining check (R3):** with `N > 1` and 0% error/loss, inspect the `[SENDER]` log and confirm `nextseqnum` advances past `base` by more than one packet before the first ACK is received — i.e. multiple packets are genuinely in flight at once.
- **Cumulative ACK check (R5):** at a low Option 4 loss rate, confirm that when an individual ACK is dropped, a later cumulative ACK for a higher `seq` advances `base` past the missing one without a retransmission being needed for that packet.
- **Go-Back-N retransmission check (R6/R7):** force a timeout (e.g., a high-loss Option 5 run) and confirm in the `[SENDER]` log that *every* packet from `base` through `nextseqnum-1` is retransmitted on timeout, not just `sndpkt[base]`.
- **Termination across rates (R15/R16):** run each of the five options across error/loss rates 0–95% (5% steps, 5 runs per point) and confirm each run terminates and logs a `[PLOT]` line. Verifies the timeout/retransmit path and `scenario_timeout` cap prevent hangs at all rates.
- **Window-size sweep (R18/R20):** run a fixed-rate (10% loss) transfer at `N = 1, 2, 5, 10, 20, 50` and confirm completion time decreases as `N` grows from 1, then plateaus or increases at very large `N` — used to identify an empirically "optimal" window size and timeout value.
- **With/without recovery demo (R13):** run once with error/loss injection disabled (`rate = 0`) and once with it enabled at a clearly visible rate (e.g. 30%), confirming both complete successfully and reconstruct the same image, to demonstrate Phase 4 working both with and without loss recovery active.

## Performance evaluation plan
- **Chart 1** — x-axis: loss/error rate `[0, 5, 10, ..., 95]` (%); y-axis: average completion time (s); one line per option (1–5), all on the same chart, window size held at the default `N = 10`.
- **Chart 2** — x-axis: window size `[1, 2, 5, 10, 20, 50]`; y-axis: average completion time (s) at a fixed 10% loss probability (Option chosen for the sweep is run with both bit-error and loss injection disabled beyond the fixed 10% data-loss rate).
- **Chart 3** — x-axis: `["Phase 1", "Phase 2", "Phase 3", "Phase 4"]`; y-axis: average completion time (s) transferring the same image at a fixed 10% loss/bit-error rate, with Phase 4 using the default window size `N = 10`.
- All charts average at least 5 runs per data point (raw per-run times stored as a matrix, e.g. `times_option[r][k]`), and `verbose_packet_logs` is disabled during timing runs so per-packet debug prints don't skew completion times (R17).
