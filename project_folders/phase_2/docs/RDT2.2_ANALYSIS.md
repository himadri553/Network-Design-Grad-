# Phase 2: RDT 2.2 Protocol Analysis

## CURRENT IMPLEMENTATION (Scenario 1: No Loss/Bit-Errors)

### Operational Flow - Current System

**Step 1:** SENDER - Load image file
- `pic_to_chunks()` reads the .bmp file and splits it into 1024-byte chunks
- Chunks are stored in `self.all_chunks[]`

**Step 2:** SENDER - Send first chunk
- `create_data_packet()` creates packet with:
  - Sequence number (starts at 0, alternates: 0→1→0→1...)
  - Checksum (sum of header + data mod 256)
  - Length (4 bytes, big-endian)
  - Data payload
- Packet format: `[seq(1B)][checksum(1B)][length(4B)][data(1024B)]` = 1030 bytes total
- `tx_send()` transmits via UDP to receiver

**Step 3:** RECEIVER - Receive first chunk
- `rx_receive()` waits for UDP packet
- `extract()` parses the packet into seq, checksum, length, data
- Stores data in `self.full_pic[]`
- Updates expected sequence number: `expected_seq = 1 - expected_seq`
- **NOTE:** Currently commented out - validation logic exists but is disabled

**Step 4:** SENDER - Send second chunk (repeat Step 2 for next chunk)
- Sequence number alternates to 1
- Process repeats for all chunks
- **NO ACK WAITING** - Sender immediately sends next packet

**Step 5:** RECEIVER - Receive remaining chunks (repeat Step 3)
- Continues receiving until timeout (5 seconds of no packets)
- Reconstructs image by concatenating all chunks in order

**Step 6:** RECEIVER - Reconstruct image
- `reconstruct_image()` joins all chunks together
- Writes to `output_pic.bmp`

---

## REQUIRED ADDITIONS FOR RDT 2.2 PROTOCOL

### What RDT 2.2 Adds to the Current System

The RDT 2.2 protocol is a **bidirectional handshake protocol** that adds:

#### 1. **Acknowledgment (ACK) Packets**
- **Currently Missing:** Receiver does NOT send ACKs
- **Must Add:** After receiver accepts a valid chunk, must send ACK packet back to sender
- ACK Packet Format: `[seq_ack(1B)][checksum(1B)][reserved(4B)]` = 6 bytes
  - `seq_ack` = sequence number being acknowledged
  - Checksum covers the ACK header

#### 2. **Sender Waits for ACK Before Next Transmission**
- **Currently Missing:** Sender sends all chunks immediately without waiting
- **Must Add:** After sending a chunk:
  - `tx_receive()` waits for ACK from receiver (with timeout)
  - Only proceeds to next chunk when valid ACK received
  - If timeout or corrupt ACK → retransmit same packet
  - Includes timeout logic for handling lost/delayed packets

#### 3. **ACK Validation/Error Handling**
- **Currently Missing:** No error handling for ACK packets
- **Must Add:** Sender must validate received ACK:
  - Check ACK checksum is valid
  - Check ACK sequence matches expected acknowledgment
  - If ACK corrupted or wrong sequence → ignore and retransmit data

#### 4. **Retransmission on Timeout**
- **Currently Missing:** No retransmission logic
- **Must Add:** 
  - Sender maintains current packet being sent
  - If no valid ACK within timeout period (e.g., 5 seconds)
  - Retransmit the same packet
  - Limit retransmissions to avoid infinite loops

#### 5. **Receiver ACK Creation**
- **Currently Missing:** `create_ack_packet()` is empty/not implemented
- **Must Add:** Build ACK packet that includes:
  - Sequence number of last correctly received packet
  - Checksum over ACK header

---

## DETAILED OPERATIONAL FLOW - RDT 2.2 PROTOCOL

### Complete Transaction for .bmp File Transfer

**Step 1:** SENDER - Initialize and prepare
- Load image, split into chunks (1024 bytes each)
- Set `seq = 0`, `ack_received = False`
- Set timeout timer to 5 seconds

**Step 2:** SENDER - Create and send first data packet
- `create_data_packet()` with seq=0
- Format: `[0][checksum][length][1024 bytes of data]`
- Call `tx_send(packet)` → UDP send to receiver
- Log: "Sending chunk 0, seq=0"

**Step 3:** RECEIVER - Receive data packet
- `rx_receive()` waits for packet (timeout 5 sec)
- `extract()` parses: seq=0, checksum, length, data
- Log: "Received packet seq=0"

**Step 4:** RECEIVER - Validate data packet
- **Validation 1:** Call `corrupt(packet)` → verify checksum
  - Recalculate checksum from header + data
  - If mismatch: packet is corrupted, discard it, go back to Step 3
  - Log: "Packet corrupted, discarding"
- **Validation 2:** Check sequence number
  - If seq ≠ expected_seq: packet out of order, discard
  - Log: "Out of order packet, discarding"
- If both validations pass: packet is valid, proceed

**Step 5:** RECEIVER - Store data and send ACK
- Append data to `self.full_pic[]`
- Update expected_seq: `expected_seq = 1 - expected_seq` (0 → 1)
- Call `create_ack_packet()` with seq_ack=0
- Format: `[0][checksum][0000(reserved)]` = 6 bytes
- Call `rx_send(ack_packet)` → UDP send back to sender
- Log: "Valid packet received seq=0, sending ACK seq=0"

**Step 6:** SENDER - Wait for and validate ACK
- `tx_receive()` waits for response (timeout 5 sec)
- If timeout: go to Step 7 (retransmit)
- If received data: `extract_ack()` parses ACK packet
- **ACK Validation 1:** Check ACK checksum
  - If checksum invalid: corrupt ACK, ignore and go to Step 7
  - Log: "ACK checksum corrupted, retransmitting"
- **ACK Validation 2:** Check ACK sequence number
  - Expected ACK seq should be 0 (echoing what we sent)
  - If ACK seq ≠ 0: wrong ACK, ignore and go to Step 7
  - Log: "Wrong ACK sequence received"
- If valid ACK received: proceed to Step 8

**Step 7:** SENDER - Timeout or Invalid ACK Handler
- Retransmission counter incremented
- If retransmit_count < MAX_RETRIES (e.g., 5):
  - Go back to Step 2 (retransmit same packet)
  - Log: "Timeout or invalid ACK, retransmitting (attempt N)"
- Else:
  - Connection failed
  - Log: "Max retransmissions exceeded for chunk 0"

**Step 8:** SENDER - Advance to next chunk
- Received valid ACK for chunk 0
- Toggle sequence number: seq = 1 - seq (0 → 1)
- Move to next chunk in array (chunk 1)
- Log: "ACK received for seq=0, advancing to next chunk"
- Go back to Step 2 with chunk 1 and seq=1

**Step 9:** RECEIVER - Receive chunk 1 (Repeat Steps 3-5 with seq=1)**
- Receives packet with seq=1
- Validates and stores
- expected_seq now 0 (was toggled to 1 in last iteration)
- Sends ACK with seq_ack=1

**Step 10:** SENDER - Receive ACK for chunk 1 (Repeat Step 6)**
- Receives valid ACK with seq_ack=1
- Matches expectation
- Advances to chunk 2 with seq=0

**(Continue Steps 2-10 pattern for all remaining chunks)**

**Final Step - After all chunks sent/received:**
- SENDER: Received ACK for last chunk, closes connection
  - Log: "All chunks transmitted successfully"
- RECEIVER: Timeout while waiting for next packet after receiving all chunks
  - Knows all data received (expected # of packets reached)
  - Call `reconstruct_image()` to join chunks and write output.bmp
  - Log: "All chunks received, image reconstructed"

---

## SCENARIO IMPLEMENTATIONS

### Scenario 1 (CURRENT): No Loss / No Bit-Errors
- Clean channel: all packets and ACKs arrive intact
- Should work smoothly with RDT 2.2 logic
- Sender doesn't experience timeouts
- Receiver doesn't receive corrupted packets

### Scenario 2 (TODO): ACK Bit-Error
**Error Injection Point:** Receiver creates ACK, checksum is corrupted
- Receiver sends ACK with wrong checksum
- Sender receives ACK but fails checksum validation
- Sender doesn't recognize it as valid ACK
- Sender timeout occurs → retransmits data packet
- Receiver receives duplicate (same seq number)
- Receiver already has this chunk (expected_seq already advanced)
- Receiver ignores duplicate, sends ACK again
- Eventually sender receives valid ACK (after some retries)

**Key Addition:** Receiver must detect and ignore duplicate packets based on seq number

### Scenario 3 (TODO): Data Bit-Error
**Error Injection Point:** Sender creates data packet, checksum is corrupted
- Sender sends packet with wrong checksum
- Receiver receives packet but fails checksum validation
- Receiver discards corrupted packet
- Receiver does NOT send ACK (or could send NAK, but RDT 2.2 uses only ACKs)
- Sender timeout occurs (no ACK received)
- Sender retransmits data packet
- Receiver receives retransmitted packet (hopefully uncorrupted)
- Receiver sends valid ACK
- Transfer continues

---

## CODING CHANGES REQUIRED

### SENDER_2.py Changes

1. **Implement `create_ack_packet()`** (currently empty)
   - Build ACK packet with sequence acknowledgment
   - Calculate checksum

2. **Modify `tx_receive()`**
   - Add ACK validation logic
   - Check checksum and sequence number
   - Return whether ACK was valid

3. **Add `validate_ack()` method**
   - Extract ACK packet fields
   - Verify checksum
   - Verify sequence number
   - Return boolean (valid/invalid)

4. **Modify `run_tx_sc1()`**
   - **Before:** Loop sends all chunks immediately
   - **After:** Loop for each chunk:
     1. Create and send data packet
     2. Wait for ACK with timeout
     3. If valid ACK: proceed to next chunk
     4. If timeout/invalid: retransmit (up to MAX_RETRIES times)

5. **Add retransmission tracking**
   - Track current chunk and sequence number
   - Maintain retry counter

### RECEIVER_2.py Changes

1. **Implement `create_ack_packet()`**
   - Build ACK with correct sequence acknowledgment
   - Calculate checksum over ACK header

2. **Add `extract_ack()` method**
   - Parse ACK packet structure (if used for future scenarios)

3. **Enable packet validation in `run_rx_sc1()`**
   - Currently commented out - uncomment:
     - Checksum validation
     - Sequence number validation
   - Send ACK after valid packet received
   - Discard/ignore corrupted or out-of-order packets

4. **Track received sequence numbers**
   - Detect duplicate packets (same seq number)
   - Ignore duplicates based on expected_seq
   - Continue sending ACK for duplicates (for Scenario 2)

5. **Modify timeout handling**
   - After receiving all expected chunks, should know total count
   - Only timeout after reasonable wait for next packet
   - Or implement explicit "end of transmission" signal

---

## SUMMARY OF CURRENT vs RDT 2.2

| Feature | Current (Scenario 1) | RDT 2.2 Required |
|---------|----------------------|------------------|
| Sequence Numbers | ✓ Yes (0/1 alternating) | ✓ Same |
| Checksums | ✓ Yes (on data) | ✓ Yes (on both data and ACKs) |
| ACK Packets | ✗ NO | ✓ YES (must implement) |
| Sender Waits for ACK | ✗ NO | ✓ YES (must add) |
| ACK Validation | ✗ NO | ✓ YES (must add) |
| Retransmission | ✗ NO | ✓ YES (with timeout) |
| Duplicate Detection | ✗ NO | ✓ YES (ignore based on seq) |
| Error Recovery | ✗ NO | ✓ YES (retry logic) |

The key insight: **Current system is "fire and forget" (unacknowledged), RDT 2.2 is a bidirectional handshake with error recovery.**
