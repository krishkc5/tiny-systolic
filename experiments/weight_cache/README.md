# Weight-cache experiment

This alternative top-level wrapper is an experiment, not the submission RTL.
The production source remains in src/project.v until physical results justify adoption.

A 128-bit rotating bank captures B operands during a normal K=16 transaction.
Command 5 (REUSE), with ui_in=0x0f in IDLE or DONE and a valid bank, starts another
K=16 calculation with those same B values. Send 16 A bytes, wait two drain edges,
and read eight result bytes: 27 cycles instead of 43. Command 5 is rejected when
no cache is valid. Short normal START, reset and ABORT invalidate the bank.
Unsupported commands and enable freezes do not rotate it. A complete REUSE
rotates exactly 16 times, restoring original weight order.

Storage bits deliberately have no reset; the reset valid bit blocks their use
until all 16 bytes have been captured. The existing protocol remains valid.

The cache workload iterates over weights first, then all 180 image pairs. This
requires host storage for intermediate results. It is a full-dataset throughput
experiment, not a single-image latency claim. Analytical cycle count:
37 * 43 + (6660 - 37) * 27 = 180412, versus baseline 286380.
All tiles, hidden activations and predictions are checked against independent
software references by test_reuse.py; physical fit is a separate acceptance gate.
