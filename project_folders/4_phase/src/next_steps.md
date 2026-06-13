# Phase 4 Implementation Checklist

Tracks the gap between `DESIGN_DOC_4.md` and the current code (still a Phase 3
stop-and-wait / alternating-bit copy). Ordered roughly by dependency.

## 3. sender.py - rewrite for GBN  ✅ DONE (scenario 1 verified)
- [x] Replace single-packet `wait_for_valid_ack` (stop-and-wait) with pipelined `gbn_send_loop`
- [x] State vars: `base = 0`, `nextseqnum = 0`, `sndpkt = {}` (absolute indices; seq byte = idx % 256)
- [x] Sending step: while `(nextseqnum - base) < N`, build/send/buffer packet for
      `nextseqnum`, start timer if `base == nextseqnum` before send, then `nextseqnum += 1`
- [x] Receive-ACK step: if ACK uncorrupted, advance `base` past acked index;
      `stop_timer()` if `base == nextseqnum`, else restart timer (`ack_to_abs` maps ACK byte -> abs idx)
- [x] Corrupt ACK -> `valid_ack` returns None -> ignore (Λ transition), no state change
- [x] Timeout step: retransmit `sndpkt[base] ... sndpkt[nextseqnum-1]` in order, restart timer
- [x] Prune `sndpkt` entries `< base` once `base` advances
- [x] `run_tx_sc1`: no injection
- [x] `run_tx_sc2`: `inject_error()` on every received ACK before corrupt-check
- [x] `run_tx_sc3`: identical to sc1 (injection happens receiver-side)
- [x] `run_tx_sc4`: `inject_loss()` on every received ACK (drop -> None)
- [x] `run_tx_sc5`: identical to sc1 (injection happens receiver-side)
- [x] Keep `scenario_timeout` wall-clock cap so every run terminates and logs `[PLOT]`

## 4. receiver.py - rewrite for GBN  ✅ DONE (scenario 1 verified)
- [x] Replace alternating `expected_seq` (0/1) with mod-256 `expected_seq`
- [x] On packet: extract seq/checksum/length/data, recompute checksum
- [x] If corrupt OR `seq != expected_seq`: discard, send ACK with
      `ack_seq = (expected_seq - 1) mod 256`, no state change (default branch)
- [x] If uncorrupted and `seq == expected_seq`: append to `full_pic`, send ACK with
      `ack_seq = expected_seq`, `expected_seq = (expected_seq + 1) mod 256`
- [x] No receiver-side reordering buffer (matches basic GBN receiver)
- [x] `run_rx_sc1`: no injection
- [x] `run_rx_sc2`: identical to sc1 (injection happens sender-side)
- [x] `run_rx_sc3`: `inject_error()` on every incoming data packet before validation
- [x] `run_rx_sc4`: identical to sc1 (injection happens sender-side)
- [x] `run_rx_sc5`: `inject_loss()` on every incoming data packet (drop -> no ACK sent)
- [x] On overall idle timeout (5s), break loop, reconstruct image from `full_pic`

## 5. main.py - rewrite scenario runners + sweeps
- [x] Pass `N` into both sender and receiver at construction
- [ ] Chart 1: for each option 1-5, for each rate in `rates` (0-95%, step 5%), run 5x,
      log `[PLOT] time, sc:N, error_rate:X, duration:Y`
      - Option 1 always 0% (flat baseline across all rate buckets)
- [ ] Chart 2: pick one option (data-loss, Option 5) at fixed 10% loss, sweep
      `N` over `[1, 2, 5, 10, 20, 50]`, 5 runs each, fresh sender/receiver pair per N
- [ ] Chart 3: re-run Phase 1-4 transfer of same image at fixed 10% loss/bit-error,
      5 runs each (Phase 1-3 may need their own runner scripts/imports)
- [x] Set `verbose_packet_logs = False` during all timing sweeps (R17) - `log_print`
      now honors the flag; main() forces it False before sweeps
- [x] Add a "with/without recovery" demo path (rate = 0 vs rate > 0) for R13 -
      `run_recovery_demo()` + "demo" menu case (Option 5 at 0% then 30%)

## 6. plotter.py - implement Chart 1/2/3
- [ ] Replace Phase 3 "RDT 3.0" per-scenario plots with the 3 required charts
- [ ] Chart 1: parse `[PLOT]` lines, average 5 runs per (option, rate), plot all
      5 options as separate lines vs. `rates` x-axis
- [ ] Chart 2: average 5 runs per window size, plot vs. `window_sizes` x-axis
- [ ] Chart 3: average 5 runs per phase, plot vs. `["Phase 1","Phase 2","Phase 3","Phase 4"]`
- [ ] Implement `generate_combined_plot()` / `run_plotter()` (currently empty stubs)
- [ ] Store raw per-run times in matrices (`times_option[r][k]`, etc.) for R16 evidence

## 7. Validation (from design doc test plan)
- [ ] Image reconstruction: visually confirm output picture matches input, no corruption
- [ ] Pipelining check (R3): confirm `nextseqnum` runs ahead of `base` by >1 before first ACK
- [ ] Cumulative ACK check (R5): Option 4 low loss - one dropped ACK recovered by a later
      cumulative ACK without retransmission
- [ ] GBN retransmit check (R6/R7): forced timeout retransmits every packet `base..nextseqnum-1`
- [ ] Termination across 0-95% rates for all 5 options, no hangs (R15/R16)
- [ ] Window-size sweep shows completion time trend vs. N (R18/R20)
- [ ] With/without recovery demo at rate=0 vs rate>0 (R13)

## 8. Docs / deliverables
- [ ] Update README.md (currently still points at `phase_2` paths) with run instructions
      for all 5 options, window-size sweep, and plot reproduction (R22)
- [ ] Confirm DESIGN_DOC_4.md matches final implementation once done (R21)
- [ ] Generate and save all 3 charts + raw timing data (R23)
- [ ] contribution.txt (R24)
- [ ] Record demo video showing Phase 4 working + plots (R25)
