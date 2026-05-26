# Network Design Project – Phase Proposal & Design Document (Phase 1 of 5)

> **Purpose:** This document is your team’s *proposal* for how you will implement the current phase **before** you start coding.  
> Keep it clear, concrete, and lightweight.

**Team Name:**  
**Members:** | Himadri Saha | Himadri_Saha@student.uml.edu  
**GitHub Repo URL: https://github.com/himadri553/Network-Design-Grad-.git**  
**Phase:** 1 
**Submission Date: 5/25**  
**Version:** v1

---

## 0) Executive summary
This phase implements UDP-based communication between a sender and receiver using separate threads. 

**Phase 1(a):** Basic echo protocol where the sender transmits the message "HELLO" to the receiver over UDP on `localhost:12000`. The receiver echoes the message back to the sender. This demonstrates fundamental UDP client-server communication.

**Phase 1(b):** File transfer protocol using RDT 1.0 (Reliable Data Transfer). The sender reads a BMP file in 1024-byte chunks and transmits each chunk sequentially to the receiver. The sender signals the end of transfer with an "END" message. The receiver reconstructs the file by writing each received chunk to disk. This demonstrates how to reliably transfer binary data over unreliable UDP. 

---

## 1) Phase requirements
### 1.1 Demo deliverable
You will submit a **screen recording** demonstrating the required scenarios.

- **Scenario 1(a):** Sender transmits "HELLO" message to receiver. Receiver echoes the message back to sender. Both log messages to output log.
- **Scenario 1(b):** Sender reads a BMP file (`my_cloud.bmp`) and transmits it in 1024-byte chunks to the receiver. Receiver reconstructs the file as `received.bmp`. Both files should be byte-for-byte identical.
- **Output:** Console output showing successful transmission and file reconstruction.

- **Private YouTube link:** *(fill in at submission time)*  

## 2) Phase plan (company-style, lightweight)
Think of this as a short “implementation proposal” you’d write at a company.

### 2.1 Scope: what changes/additions this phase
- **New behaviors added:**
  - UDP socket creation and binding for receiver (Phase 1a)
  - Sender-receiver communication using `sendto()` and `recvfrom()` (Phase 1a)
  - Threading to run sender and receiver concurrently (Phase 1a)
  - File I/O: reading binary files in chunks (Phase 1b)
  - Sequential packet transmission with end-of-transfer signaling (Phase 1b)
  - File reconstruction by writing chunks to output file (Phase 1b)
  - Logging to `results/output_log.txt` for Phase 1a

- **Behaviors unchanged from previous phase:**
  - N/A (this is Phase 1)

- **Out of scope (explicitly):**
  - Error correction (e.g., checksums, retransmissions due to corruption)
  - Packet sequence numbers or acknowledgments (Phase 1b uses simple "END" signal, no ACKs)
  - Handling lost packets or out-of-order delivery
  - Command-line argument parsing (hardcoded values for Phase 1)
  - Network interface configuration beyond localhost

### 2.2 Acceptance criteria (your checklist)
- [x] Phase 1a: Sender successfully transmits "HELLO" message
- [x] Phase 1a: Receiver receives and echoes message back
- [x] Phase 1a: Both processes log to output_log.txt with "[SENDER]" and "[RECEIVER]" prefixes
- [x] Phase 1a: Threads run concurrently without race conditions or hangs
- [x] Phase 1b: Sender reads BMP file and chunks it into 1024-byte pieces
- [x] Phase 1b: All chunks are transmitted to receiver
- [x] Phase 1b: "END" signal marks end of file transfer
- [x] Phase 1b: Receiver reconstructs file as `received.bmp`
- [x] Phase 1b: Reconstructed file is byte-for-byte identical to original

### 2.3 Work breakdown (high-level; Person X will work on A, Person Y will work on B...)
- **Solo work (Himadri Saha):**
  - Implement SENDER_1 class with `tx_send()`, `tx_receive()`, and logging methods
  - Implement RECEIVER_1 class with `rx_receive()`, `rx_send()`, and logging methods
  - Implement threading orchestration in `main_1a.py` for Phase 1a
  - Implement RDT1_client.py for Phase 1b (file chunking and transmission)
  - Implement RDT1_server.py for Phase 1b (file reconstruction)

---

## 3) Architecture + state diagrams
Your phase specs likely include a reference state diagram. **You should build on it across phases.**

### 3.1 How to evolve the provided state diagram
For each phase:
1. **Start from the current phase diagram** (sender + receiver).
2. **Mark specifics**:
   - new states,
   - new transitions,
   - updated transition conditions (timeouts, corruption checks, window slide rules).
3. Keep both:
   - **“Previous phase diagram”** (for comparison) and
   - **“Current phase diagram”** (what you will implement in more detail).

> Tip: In your PDF submission, include diagrams as images. In Markdown, you can include ASCII diagrams or link to images in `docs/figures/`.

### 3.2 Component responsibilities

#### **Phase 1a (Echo Protocol)**
- **SENDER_1 Class:**
  - `__init__(rx_name, rx_port, buffer_size)`: Initialize UDP socket (unbound client socket)
  - `tx_send(data)`: Transmit message to receiver using `sendto()`
  - `tx_receive()`: Wait for echo response with 5-second timeout
  - `log_print(message)`: Append log entries to output_log.txt with [SENDER] prefix

- **RECEIVER_1 Class:**
  - `__init__(buffer_size, port)`: Create and bind UDP socket to `localhost:port`
  - `rx_receive()`: Listen for incoming message using `recvfrom()`, store sender address
  - `rx_send(data)`: Echo data back to stored sender address
  - `log_print(message)`: Append log entries to output_log.txt with [RECEIVER] prefix

- **main_1a.py:**
  - `tx_run_1a(sender)`: Orchestrate sender thread (send → wait for echo → log)
  - `rx_run_1a(receiver)`: Orchestrate receiver thread (listen → echo → log)
  - `main()`: Clear log file, instantiate sender/receiver, spawn threads (receiver first), wait for both to complete

#### **Phase 1b (File Transfer - RDT 1.0)**
- **RDT1_client.py:**
  - Read BMP file from disk
  - Chunk file into 1024-byte pieces
  - Send each chunk via UDP to server
  - Send "END" signal to mark completion

- **RDT1_server.py:**
  - Create and bind UDP socket to `localhost:12000`
  - Listen for chunks from client
  - Write each chunk to output file (`received.bmp`)
  - Stop listening when "END" signal received

- **Shared modules/utilities:**
  - `main1_helper.py`: Contains `main_log_print()` for [MAIN] level logging
  - Chunk size: 1024 bytes
  - Buffer size: 2048 bytes
  - Log path: Computed relative to script location

### 3.3 Message flow overview

**Phase 1a (Echo):**
```
[Sender Thread]                [Receiver Thread]
     |                              |
     |--- bind to :12000 -------->  |
     |  (receiver ready)            |
     |                              |
     |--- send "HELLO" to :12000 -> |
     |                              |
     |                              | rx_receive() blocks
     |                         rx_send("HELLO")
     |<------ echo "HELLO" ---------|
     |                              |
 tx_receive() returns               |
     |                         (thread completes)
 (thread completes)                 |
```

**Phase 1b (File Transfer):**
```
[Sender/Client]                [Receiver/Server]
    |                               |
    |--- bind to :12000 --------->  |
    |  (server ready)               |
    |                               |
    |--- chunk 1 (1024B) --------->  |
    |                                |
    |                           write to file
    |<------- (no ACK) -------------|
    |                               |
    |--- chunk 2 (1024B) --------->  |
    |                                |
    |                           write to file
    | ... (repeat for all chunks)    |
    |                               |
    |--- "END" signal ------------->  |
    |                                |
    |                           close file
    | (client closes socket)    (server closes socket)
```

---

## 4) Packet format (high-level spec)
Define your on-the-wire format **unambiguously**.

### 4.1 Packet types

**Phase 1a (Echo):**
- **Data packet:** Plain UTF-8 string (e.g., "HELLO")
- **Echo packet:** Plain UTF-8 string echoed back by receiver (e.g., "HELLO")
- No structured header — message is the payload itself

**Phase 1b (File Transfer - RDT 1.0):**
- **Data packet:** Raw binary chunk from file (up to 1024 bytes)
- **End-of-transfer marker:** Literal 3-byte sequence `b"END"`
- No structured header — RDT 1.0 assumes no corruption or loss on the channel

### 4.2 Header fields / Packet structure

**Phase 1a (Echo Protocol):**
| Component | Format | Description |
|---|---|---|
| Payload | UTF-8 string | Plain text message (e.g., "HELLO") |
| Length | Implicit | Determined by `encode()` / `decode()` |

**Phase 1b (File Transfer - RDT 1.0):**
| Component | Format | Description | Constraints |
|---|---|---|---|
| Data packet | Raw binary bytes | File chunk read from disk | Max 1024 bytes per chunk |
| End marker | `b"END"` (3 bytes) | Signals completion of transfer | Exact literal bytes |
| No sequence numbers | — | Assumes in-order, reliable delivery | RDT 1.0 assumption |
| No checksums | — | Assumes no corruption | RDT 1.0 assumption |
| No ACKs | — | Sender transmits all chunks, no flow control | Stop-and-wait not implemented |

### 4.3 Rationale

**Phase 1a:**
- Simplest possible format: text message
- Demonstrates basic UDP send/receive

**Phase 1b:**
- RDT 1.0 is the simplest reliable data transfer protocol
- Assumes reliable channel (no corruption, no loss)
- Therefore: no checksums, sequence numbers, or ACKs needed
- Practical implementation: send all chunks sequentially, then signal "END"
- 1024-byte chunks chosen for reasonable file transfer granularity (standard network MTU consideration)

---

## 5) Data structures + module map

### 5.1 Key data structures

**Phase 1a:**
- **No custom data structures:** Uses only built-in Python types
  - `str`: Message payload ("HELLO", echo response)
  - `tuple`: Socket address `(host, port)` returned by `recvfrom()`

**Phase 1b:**
- **No custom data structures:** Uses only built-in Python types
  - `bytes`: File chunks read from disk (binary data)
  - `int`: Chunk counter for loop tracking
  - File pointers: `open()` file handles for reading/writing

### 5.2 Module map + dependencies

**Phase 1a modules:**
```
main_1a.py                  # Entry point, threading orchestration
├── sender_1.py            # SENDER_1 class: UDP client logic
├── receiver_1.py          # RECEIVER_1 class: UDP server logic
└── main1_helper.py        # main_log_print() utility
```

**Phase 1b modules:**
```
RDT1_client.py            # Sender: file chunking + transmission
├── os                     # Path manipulation (file_path construction)
└── socket                 # UDP client socket

RDT1_server.py            # Receiver: file reconstruction
├── socket                 # UDP server socket
├── os                     # Path manipulation (file_path construction)
└── PIL.Image             # (Optional) image verification
```

**Dependencies:**
- `sender_1.py` → `socket`, `os`
- `receiver_1.py` → `socket`, `threading`, `os`
- `main_1a.py` → `threading`, `socket`, `os`, `sender_1`, `receiver_1`, `main1_helper`
- `RDT1_client.py` → `socket`, `os`
- `RDT1_server.py` → `socket`, `os`, `PIL` (optional)

---

## 6) Protocol logic (high-level spec before implementation)
This section is your “engineering spec” that you implement against. Keep it precise but not code-heavy.

### 6.1 Phase 1a: Sender behavior

**Sender state machine:**
```text
READY
  ├─> send "HELLO" to receiver:12000
  ├─> WAITING_FOR_ECHO
         └─> (timeout 5s) if no echo: log error, exit
         └─> if echo received: log echo, exit
```

**Sender pseudocode:**
```text
log_print("Sender is up and running")
tx_send("HELLO")  // sendto() to receiver
log_print("sent message, waiting for ECHO message from receiver...")
echo = tx_receive()  // recvfrom() with 5s timeout
if echo:
  log_print(f"Echo Message: {echo}")
else:
  log_print("Error: no response from receiver (timed out)")
```

**Key points:**
- One-shot send and receive
- 5-second timeout prevents hanging
- No retransmission (fails if receiver not ready)

### 6.2 Phase 1a: Receiver behavior

**Receiver state machine:**
```text
READY (bound to :12000)
  ├─> rx_receive() blocks on recvfrom()
  ├─> WAITING_FOR_MESSAGE
         └─> packet arrives
         ├─> rx_send(same_data) back to sender address
         └─> exit
```

**Receiver pseudocode:**
```text
bind socket to ('localhost', 12000)
log_print("Receiver is up and running")
received_message = rx_receive()  // blocks here
log_print(f"received a message: {received_message}")
rx_send(received_message)  // sendto() back to sender_address from recvfrom()
```

**Key points:**
- Blocks indefinitely on `recvfrom()` waiting for sender
- Captures sender address automatically from `recvfrom()` return
- Echoes exact same data back to that address

### 6.3 Phase 1b: Sender (Client) behavior

**Sender state machine:**
```text
READY
  ├─> open file ("my_cloud.bmp")
  ├─> SENDING_CHUNKS
         └─> for each 1024-byte chunk:
              ├─> sendto(chunk, server:12000)
              └─> no ACK wait
  ├─> SENDING_END_MARKER
         ├─> sendto(b"END", server:12000)
         └─> close socket, exit
```

**Sender pseudocode:**
```text
open file (binary read mode)
chunk_size = 1024
for each 1024-byte chunk in file:
  client_socket.sendto(chunk, (server_name, server_port))
client_socket.sendto(b"END", (server_name, server_port))
close file
close socket
```

**Key points:**
- No acknowledgments (RDT 1.0 assumes reliable channel)
- Sends all chunks sequentially
- Final "END" marker signals transfer complete
- No retransmission

### 6.4 Phase 1b: Receiver (Server) behavior

**Receiver state machine:**
```text
READY (bound to :12000)
  ├─> open output file ("received.bmp", write binary)
  ├─> RECEIVING_CHUNKS
         └─> while True:
              ├─> recvfrom() blocks for packet
              ├─> if packet == b"END": break
              ├─> else: write(packet) to file
  ├─> DONE
         └─> close file, close socket, exit
```

**Receiver pseudocode:**
```text
bind socket to ('', 12000)  // all interfaces
open output file ("received.bmp", "wb")
while True:
  packet, client_address = server_socket.recvfrom(2048)
  if packet == b"END":
    print("File transfer done")
    break
  file.write(packet)
close file
close socket
```

**Key points:**
- Listens on all interfaces (0.0.0.0)
- Writes each chunk sequentially to file in order
- "END" marker terminates transfer
- No checksums or validation (RDT 1.0 assumption)

### 6.5 Error/loss injection spec
**Phase 1a & 1b (Not required):**
- No error injection implemented for Phase 1
- Assumes reliable UDP channel (same host)
- Future phases will add loss/corruption injection

---

## 8) Edge cases + test plan
This replaces “risks” with what actually matters for correctness.

### 8.1 Edge cases you expect

**Phase 1a (Echo):**
| Edge case | Why it matters | Expected behavior |
|---|---|---|
| Sender timeout (receiver not ready) | robustness | Sender logs timeout error and exits cleanly |
| Receiver starts after sender sends | synchronization | Sender times out; receiver never starts listening |
| Message encoding/decoding | UTF-8 safety | "HELLO" transmitted and echoed correctly |
| Threading race conditions | determinism | Receiver always starts first, no deadlocks |

**Phase 1b (File Transfer):**
| Edge case | Why it matters | Expected behavior |
|---|---|---|
| Last chunk < 1024 bytes | file reconstruction accuracy | Receiver writes exact final chunk size |
| File size exactly divisible by 1024 | boundary condition | No partial final chunk, just "END" signal |
| Large BMP file (> 1MB) | scalability | All chunks transmitted in order |
| "END" marker vs data collision | protocol correctness | Exact byte comparison: `== b"END"` (not substring) |
| Out-of-order packet arrival | RDT 1.0 assumption | Should not occur on localhost; would corrupt file |

### 8.2 Tests you will write because of these edge cases

**Phase 1a Manual Tests:**
- ✓ Test 1a-1: Run sender → receiver → verify "HELLO" echoed in log
- ✓ Test 1a-2: Kill receiver mid-test → verify sender timeout after 5s
- ✓ Test 1a-3: Restart test 3 times → verify consistent behavior

**Phase 1b Manual Tests:**
- ✓ Test 1b-1: Transfer `my_cloud.bmp` → verify `received.bmp` is identical
  - Command: `cmp my_cloud.bmp received.bmp` (byte-for-byte comparison)
- ✓ Test 1b-2: Verify chunk count = ceil(file_size / 1024) + 1 (for END)
- ✓ Test 1b-3: Verify last chunk is < 1024 bytes if file_size % 1024 != 0

### 8.3 Test artifacts

- **Logs:** `results/output_log.txt` (Phase 1a)
- **Output files:** `received.bmp` in `RDT1_server.py` output directory
- **Console output:** Captured during screen recording
- **Test results:** Manual verification (no automated test suite for Phase 1)

---

## 9) Repo structure + reproducibility

**Actual Phase 1 Repo Structure:**
```
project_folders/
  project_1/
    README_TEMPLATE.md          # Project description
    requirements.txt            # Python dependencies
    docs/
      DESIGN_DOC_TEMPLATE.md    # This document
      from_class/
        Phase 1-1.pdf           # Phase requirements
    results/
      output_log.txt            # Phase 1a logging (cleared on each run)
      phaseX.csv               # (Optional) future data files
    src_1a/                     # Phase 1(a): Echo protocol
      main_1a.py               # Main entry point (threading orchestration)
      sender_1.py              # SENDER_1 class (UDP client)
      receiver_1.py            # RECEIVER_1 class (UDP server)
      main1_helper.py          # Helper functions (logging)
    src_1b/                     # Phase 1(b): File transfer (RDT 1.0)
      RDT1_client.py           # Sender: chunks + transmits BMP file
      RDT1_server.py           # Receiver: reconstructs BMP file
```

**How to run:**
- **Phase 1a:** `python src_1a/main_1a.py` (starts both threads)
- **Phase 1b:** 
  - Terminal 1: `python src_1b/RDT1_server.py` (receiver waits)
  - Terminal 2: `python src_1b/RDT1_client.py` (sender transmits)

**Reproducibility:**
- Phase 1a uses `threading.sleep(0.5)` to ensure receiver starts first (deterministic)
- Phase 1b sends file in fixed 1024-byte chunks with hardcoded paths
- Both phases use `localhost` network (no routing variability)
- Output log (`results/output_log.txt`) is cleared at start of Phase 1a for clean output
- File transfer verified with byte comparison: `cmp my_cloud.bmp received.bmp`

---

## 10) Team plan, ownership, and milestones

### 10.1 Task ownership
| Task | Owner | Target date | Status |
|---|---|---|---|
| Phase 1a: Echo protocol (sender + receiver classes) | Himadri Saha | 5/25/2026 | ✓ Completed |
| Phase 1a: Main orchestration (threading) | Himadri Saha | 5/25/2026 | ✓ Completed |
| Phase 1b: RDT 1.0 client (file chunking) | Himadri Saha | 5/25/2026 | ✓ Completed |
| Phase 1b: RDT 1.0 server (file reconstruction) | Himadri Saha | 5/25/2026 | ✓ Completed |
| Design document + edge cases | Himadri Saha | 5/25/2026 | ✓ Completed |
| Screen recording demo | Himadri Saha | 5/25/2026 | Pending |
| YouTube upload | Himadri Saha | 5/25/2026 | Pending |

### 10.2 Milestones (Keep it realistic)
- **Milestone 1 (5/24):** Phase 1a complete — echo protocol working
- **Milestone 2 (5/25):** Phase 1b complete — file transfer working
- **Milestone 3 (5/25):** Design doc + video demo ready for submission

---

## Appendix (optional)
