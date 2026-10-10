# TinySystolic streaming protocol (v1)

Compute C[2,2] = A[2,K] × B[K,2], signed INT4 operands and signed INT16 results, K=1..16. No saturation or quantization is performed. All supported sums fit; maximum positive result is 1024. Host software combines larger reductions and applies bias, activation and requantization.

## Pins

- `ui_in[7:0]`: input byte.
- `uo_out[7:0]`: current result byte when done; zero otherwise.
- `uio[2:0]`: command, inputs; `uio[3]`: reserved input, ignored.
- `uio[4]`: ready to accept DATA (LOAD and ena=1).
- `uio[5]`: busy (loading or draining).
- `uio[6]`: done, sticky until accepted START, ABORT, or reset.
- `uio[7]`: sticky protocol error, cleared by accepted START, ABORT, or reset.
- `uio_oe=0xf0`: the host must never drive uio[7:4].
- `clk`: clock; `rst_n`: synchronous active-low reset, independent of ena.
- `ena=0`: freezes controller, input assembly, array and read pointer. Commands are ignored. Ready goes low; other status/result values hold.

## Commands

Commands are level-sampled on **every rising edge with ena=1**, not edge detected. Holding DATA or READ high across multiple clock edges transfers multiple bytes. Drive NOP between transfers when needed. Inputs must meet clock setup/hold timing; there is no asynchronous synchronizer or independent host clock.

| Code | Command | Behavior |
|---|---|---|
| 0 | NOP | No host transfer; internal pipeline can advance |
| 1 | START | Accepted only idle/done and ui_in[7:4]=0. Low nibble encodes K−1. Clears all sums, valid bits, read index, error and prior result |
| 2 | DATA | Accepted only while ready. Alternates packed A then packed B for each k |
| 3 | READ | Only in DONE: advance result byte pointer modulo eight |
| 4 | ABORT | Immediately clear computation/result/error and return idle, from any state |
| 5–7 | Invalid | Set sticky error |

Unsupported commands in the current state set error without consuming data or changing read position. A rejected START does not destroy existing results or the active operation. Error is informational: the existing operation continues and must still receive the correct remaining bytes. A READ on the final drain edge is rejected because DONE was not asserted before that edge.

## Transfer sequence

1. Reset across a rising edge (or issue ABORT).
2. START with byte K−1.
3. For k=0..K−1, send DATA with `{A[1,k], A[0,k]}`, then DATA with `{B[k,1], B[k,0]}`. Each bracketed operand is a two's-complement nibble. NOP bubbles may occur anywhere, including between a pair of bytes.
4. After the last B byte, send NOP for two enabled rising edges. DONE asserts at the second edge. Ready drops during drain and remains low in DONE.
5. Read eight bytes: C00 low/high, C01 low/high, C10 low/high, C11 low/high. **Sample the current byte before the READ rising edge**, which advances to the next byte. Reading does not clear done; the pointer wraps after eight reads. NOP holds the current byte indefinitely.
6. START may follow immediately after the final READ, without reset. ABORT may interrupt any phase, including a half-loaded operand pair.

With no stalls: one START + 2K DATA + two drain + eight READ cycles = **2K+11 cycles** per complete transaction. From the first DATA edge through DONE inclusive is 2K+2 cycles. The core alone supports a quartet each step and completes K injections in K+2 enabled steps. These cycle counts do not include external host/software delays. Peak capacity is four MACs/cycle; byte-wide transfer prevents sustained peak at the chip interface.

Example K=1: A=[[−8],[7]], B=[[−2,3]]. START byte 0; DATA 0x78; DATA 0x3e; two NOP edges. Results are [16,−24,−14,21], bytes [0x10,0x00,0xe8,0xff,0xf2,0xff,0x15,0x00].
