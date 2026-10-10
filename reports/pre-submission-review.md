# Pre-submission design review — 2026-10-10

Scope: TinySystolic fixed 2x2 signed INT4 accelerator, K=1..16; candidate f5fd8804b6859e741a871e7ea7580a31b0cb1a06.

## Reviewed

- Numeric bounds: product range −56..64; every accumulation prefix of length <=16 fits −896..1024. Twelve signed internal bits are exact; readback sign-extends to 16 bits. Tests cover endpoints. If K is increased later, revisit the bound.
- Dataflow: A moves right, B down; one-cycle skew and per-operand valid bits preserve pairing under bubbles and enable freezes. Tests compare all four outputs with independent matrix arithmetic.
- Controller: each accepted START sets the input quota; every second DATA byte injects a quartet. Final injection enters two-edge drain; no additional DATA is accepted in drain/done. Invalid commands set error without consuming bytes.
- Reset/abort: both clear all pipeline valids and sums. Reset works even with ena low. Abort is an enabled command. Recovery tests exercise idle, both input phases, both drain phases and completed output.
- Electrical interface: uio[3:0] are inputs, uio[7:4] outputs; host must not drive status pins. All output pins are assigned. The host must use the chip clock synchronously; asynchronous host signals are not supported directly.
- Readback: current byte must be sampled before READ edge; eight reads wrap pointer without destroying results. New accepted START discards prior results. This behavior is documented and tested.
- Actual ML workload: all 360 held-out images pass through the external RTL interface; 6,660 exact tile matches, hidden-activation and prediction matches. Host-assisted computation boundaries are documented.
- Area/timing comparison: preserve the earlier passing design as baseline; use identical official SKY26d process, one tile, and 20 ns physical timing constraint. Routed candidate area is 12.466% lower with better setup margin and zero reported DRC/LVS errors; final gate-level/precheck statuses are recorded in optimization.md.

## Before paying/submitting

Candidate GDS, precheck, gate-level tests and docs have passed. Successful source revision: f5fd8804b6859e741a871e7ea7580a31b0cb1a06 (run 38081509655). Confirm final author, pin documentation, shuttle availability, tile order and matching devkit. The user makes the purchase/submission decision. No purchase or fabrication submission has been performed.

## Explicit limitations

The tests and physical checks are substantial verification, not a proof against every possible silicon failure. No actual silicon measurements yet. Host transport software, power estimation and a scheduled one-MAC performance baseline remain portfolio work; they do not change the verified RTL interface. Model accuracy is 90.83% on this held-out digits split, not a guarantee on arbitrary drawings.
