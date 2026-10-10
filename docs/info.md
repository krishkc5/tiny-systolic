# How it works

TinySystolic is a 2x2 output-stationary systolic matrix accelerator. Four signed INT4 multipliers and 12-bit internal accumulators with INT16 readback compute C[2,2] = A[2,K] times B[K,2], K=1..16. Operands move right/down with registered valid bits and one-cycle boundary skew. A synchronous byte-wide controller assembles input pairs and drains the pipeline. No model weights or firmware are stored on the chip.

# How to test

Run `make check` with the dependencies in README.md. Reset by holding rst_n low across a rising edge. Drive uio[2:0] with command 1 and ui_in=K-1 to start. For each k, issue command 2 twice: first ui_in={A[1,k],A[0,k]}, then {B[k,1],B[k,0]}, with signed two's-complement nibbles. Issue command 0 during idle clocks. After the last B transfer, wait two enabled clock edges for uio[6] done. Read uo_out before each command-3 rising edge: C00 low/high, C01 low/high, C10 low/high, C11 low/high. The read pointer wraps modulo eight. Command 4 aborts and clears the operation. A valid new start is accepted in idle/done and clears prior results.

uio[4] is DATA-ready, uio[5] busy, uio[6] done, uio[7] sticky error. uio[3] is ignored. The host must only drive uio[3:0]. Invalid commands set error but do not consume data or restart computation. Valid START, ABORT, or reset clears error. ena=0 freezes computation and command handling; reset still works. Commands are sampled every enabled rising edge, including repeated command values.

Example K=1: START 0, DATA 0x78, DATA 0x3e, two NOP edges. Results are 16, -24, -14, 21. The eight bytes are 10 00 e8 ff f2 ff 15 00 (hex).

See docs/protocol.md in the repository for the complete protocol. Tests cover exhaustive INT4 multiplication, K=1..16, random matrices, bubbles, enable pauses, malformed commands, abort/reset in every phase, and repeated operations. Ideal complete transaction latency is 2K+11 cycles including command/input/output transfers.

# External hardware

A compatible Tiny Tapeout devkit and synchronous host interface are needed for silicon testing. The host performs ML model preparation, bias, activation, scaling and larger-matrix tiling. The repository includes a trained INT4 digit model tested through RTL; the board transport driver is future work. No external hardware is needed for simulation.
