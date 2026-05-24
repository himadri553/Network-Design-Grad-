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
In this phase, UDP sockets will be implemented with sender adn receiver threads to separate logic. Phase 1(a) will be a scenario where the sender transmits "HELLO" to the server, which echos it back. The ports will be different but use the same host. 

---

## 1) Phase requirements
### 1.1 Demo deliverable
You will submit a **screen recording** demonstrating the required scenarios.

- **Private YouTube link:** *(fill in at submission time)*  

## 2) Phase plan (company-style, lightweight)
Think of this as a short “implementation proposal” you’d write at a company.

### 2.1 Scope: what changes/additions this phase
- **New behaviors added:**
- **Behaviors unchanged from previous phase:**
- **Out of scope (explicitly):**

### 2.2 Acceptance criteria (your checklist)
List 5–10 measurable checks that mean you’re done (examples below).

- [ ] Sender/receiver run with standard CLI flags
- [ ] All required scenarios demonstrated in the video
- [ ] Output file matches input file (byte-for-byte)
- [ ] Figures/plots generated and saved under `results/`
- [ ] Re-run is reproducible using the same seed

### 2.3 Work breakdown (high-level; Person X will work on A, Person Y will work on B...)
- Workstream A:

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
- **Sender**
  - responsibilities:
- **Receiver**
  - responsibilities:
- **Shared modules/utilities**
  - packet encode/decode:
  - checksum:
  - logging/timing:
  - CLI/config parsing:

### 3.3 Message flow overview
Add a simple diagram (box + arrows is fine, you're also welcome to use software with screenshots).

Example:
```
[file] -> Sender -> UDP -> Receiver -> [output file]
              ^             |
              |---- ACK ----|
```

---

## 4) Packet format (high-level spec)
Define your on-the-wire format **unambiguously**.

### 4.1 Packet types
List the packet types you will send:
- Data packet
- ACK packet
- (Optional) end-of-transfer marker / metadata packet

### 4.2 Header fields (this is the “field table”)
**What this means:** you must specify the *exact* fields in each packet header and their meaning.  
This ensures everyone can encode/decode packets consistently.

| Field | Size (bytes/bits) | Type | Description | Notes |
|---|---:|---|---|---|
| type |  |  | data vs ack |  |
| seq |  |  | sequence number |  |
| ack |  |  | ack number / flag |  |
| len |  |  | payload length | last packet may be smaller |
| checksum |  |  | checksum value | what it covers (header/payload) |
| payload | ≤ ~1024B | bytes | file chunk | binary-safe |

---

## 5) Data structures + module map

### 5.1 Key data structures

### 5.2 Module map + dependencies
Show how modules connect.

Minimum expected modules (names may vary):
- `src/sender.*`
- `src/receiver.*`
- `src/packet.*` (encode/decode)
- `src/checksum.*`
- `scripts/run_experiments.*` (if applicable)
- `scripts/plot_results.*` (if applicable)

Provide a simple dependency sketch:

```
sender -> packet, checksum, utils
receiver -> packet, checksum, utils
scripts -> sender/receiver CLI, results CSV, plotting
```

---

## 6) Protocol logic (high-level spec before implementation)
This section is your “engineering spec” that you implement against. Keep it precise but not code-heavy.

### 6.1 Sender behavior
Describe behavior as steps or a state machine:
- when packets are sent
- when ACKs are processed
- retransmission rules
- termination conditions
- (if applicable) window advance rules

**Sender pseudocode (recommended):**
```text
initialize state
while not done:
  send/queue packets according to phase rules
  wait for ACK/event
  if ACK received:
    validate (checksum/seq)
    update state (advance, ignore duplicate, etc.)
  if timeout/event:
    retransmit according to phase rules
```

### 6.2 Receiver behavior
Describe receiver rules:
- accept/discard conditions
- ACK rules
- duplicate/out-of-order handling
- file write rules (safe and deterministic)

**Receiver pseudocode (recommended):**
```text
on packet receive:
  if corrupt: discard; respond according to phase rules
  else if expected: accept; write/buffer; ACK
  else: handle duplicate/out-of-order according to phase rules
```

### 6.3 Error/loss injection spec (if required by phase)
If the phase requires injection, state:
- where injection occurs in the pipeline (exact point)
- probability model and RNG seed usage
- what is injected (bit flip vs drop)
- how you ensure repeatability

---

## 8) Edge cases + test plan
This replaces “risks” with what actually matters for correctness.

### 8.1 Edge cases you expect
List the top edge cases you will explicitly test.

| Edge case | Why it matters | Expected behavior |
|---|---|---|
| last packet smaller than payload size | correct file reconstruction | receiver writes exact bytes |
| duplicate packets/ACKs | protocol correctness | ignored or re-ACKed |
| corrupted header | checksum coverage | drop / request retransmit |
| termination marker handling | clean shutdown | no deadlocks |

### 8.2 Tests you will write because of these edge cases
List concrete tests (unit/integration) that map to the edge cases.

- Unit tests (examples):
  - checksum correctness on known inputs
  - packet encode/decode round-trip
- Integration tests (examples):
  - send file and verify output hash matches input
  - run scenario injection and confirm behavior

### 8.3 Test artifacts
State what artifacts you will produce:
- console logs (minimal)
- where tests live (`tests/` optional, or `scripts/`)

---

## 9) Repo structure + reproducibility
Your repo must contain at minimum:

```
src/
scripts/
docs/
results/
README.md
```

State where phase artifacts live:
- Design docs: `docs/`
- Figures/plots + CSV: `results/`
- Any helper scripts: `scripts/`

---

## 10) Team plan, ownership, and milestones
### 10.1 Task ownership
| Task | Owner | Target date | Definition of done |
|---|---|---|---|
| Packet format + encode/decode |  |  |  |
| Sender logic |  |  |  |
| Receiver logic |  |  |  |
| Injection (if required) |  |  |  |
| Figures/plots (if required) |  |  |  |
| README + reproducibility |  |  |  |

### 10.2 Milestones (keep it realistic)
- Milestone 1:
- Milestone 2:
- Milestone 3:

---

## Appendix (optional)
