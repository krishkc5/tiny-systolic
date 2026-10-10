# Tiny Tapeout INT4 systolic ML accelerator

Status: architecture proposal; no RTL or measured hardware results yet.

## Portfolio objective

Design, verify, and physically implement a small matrix-multiplication accelerator. Explain its dataflow and measure when parallel compute helps and when external data transfer dominates. Target Tiny Tapeout; shuttle, tile allocation, and timing target remain undecided.

## Initial architecture

- Four processing elements in a 2 × 2 output-stationary systolic array.
- Signed INT4 operands (−8 through 7), signed 16-bit accumulators.
- Compute C[2,2] = A[2,K] × B[K,2], with K from 1 through 16 initially.
- A moves right, B moves down; every element keeps its own partial sum.
- Inputs enter the top and left edges with row/column skew. Valid bits travel with operands; bubbles must never accumulate stale values.
- Accumulators clear at the start of each operation. Outputs remain stable until explicitly cleared or overwritten by the next operation.
- The maximum positive sum for K ≤ 16 is 16 × 64 = 1024, safely within signed 16-bit range.
- Larger matrices use software tiling; software combines partial results when splitting the reduction dimension.

## Interface and bandwidth decision

Keep the arithmetic core independent of its Tiny Tapeout wrapper. The proposed wrapper uses an 8-bit data input and 8-bit data output plus control/status on bidirectional pins configured to fixed directions. Verify final pin assignments against the selected shuttle template.

One full array injection needs four INT4 values, or 16 bits, per cycle. An 8-bit input cannot sustain that rate without preloading, a wider interface, or input bubbles. Start with two input-transfer cycles per injection and explicit valid propagation. Compare this streaming implementation against a preloaded simulation harness to quantify bandwidth loss. Do not add a large operand buffer before measuring its area cost.

Read four 16-bit results as eight output bytes. Define exact command acceptance, busy behavior, reset behavior, and result ordering before writing the wrapper. All control is synchronous to the supplied clock; host signals must satisfy its timing requirements.

## Performance experiments

Use the same signed arithmetic and workloads for a sequential one-MAC baseline and the four-MAC array. Include K = 1, 2, 4, 8, 16, and tiled larger matrix examples.

Report separately:

| Metric | Method |
|---|---|
| Correctness | Bit-exact comparison against an integer software model |
| Compute latency | Count cycles from first accepted core injection through final accumulation |
| End-to-end latency | Count command, input transfer, computation, and output transfer cycles |
| Useful throughput | 4K useful MACs divided by elapsed cycles, then multiply by validated clock frequency |
| PE utilization | Useful MACs / (4 × measured compute cycles) |
| Speedup | Baseline elapsed time / array elapsed time under identical interface assumptions |
| Area | Standard-cell area plus allocated tile footprint; report both |
| Timing | Post-route timing at the specified process corner and constraints |
| Efficiency | Useful MAC/s divided by standard-cell area |

Ideal core reference: with one fully populated injection per cycle, no arithmetic pipeline beyond the PE register, and properly skewed inputs, the final PE finishes after K + 2 cycles counting the first injection as cycle 1. Thus utilization is K/(K+2). This is an analytical reference, not a measurement of the proposed byte-wide wrapper.

Peak arithmetic capacity is four MACs per cycle. If reporting operations/s with a multiply and add counted separately, state the convention explicitly: eight operations per cycle. Never present that peak as end-to-end throughput.

Power and energy are optional extensions requiring a stated estimation flow, library corner, and switching activity. Do not infer energy savings from area or cycle counts alone. Distinguish simulated, post-route, and measured-silicon results throughout.

## Verification gates

1. Exhaustively check all 256 signed INT4 operand pairs in one processing element.
2. Test zeros, extreme values, alternating signs, identity examples, and reproducibly seeded random matrices against the software model.
3. Test every supported K, skew timing, input bubbles, back-to-back operations, reset during work, and stable completed results.
4. Exercise the actual byte-wide wrapper and count accepted transfers so host overhead appears in benchmarks.
5. Run synthesis checks for unintended latches and verify timing constraints, routed implementation checks, and gate-level tests required by the selected template.

## Deliverables and milestones

1. Core RTL, software reference, automated tests, and cycle traces.
2. Sequential baseline, reproducible benchmarks, and plots of utilization and latency versus K.
3. Tiny Tapeout wrapper, protocol documentation, and demo host script.
4. Physical implementation, area/timing report, and documented tradeoffs.
5. Portfolio write-up and demo showing a small quantized dense layer. Keep bias, activation, and quantization on the host initially, and describe this boundary accurately.

Start with the 2 × 2 INT4 configuration. Explore INT8 or a larger array only after establishing correctness and measuring area. No claim of one-tile fit is made.

## Official starting points

- Templates: https://www.tinytapeout.com/hdl/templates/
- SKY template: https://github.com/TinyTapeout/ttsky-verilog-template
- Submission: https://www.tinytapeout.com/guides/advanced-workshop/submit-your-design/

Templates differ by process. Use the selected shuttle's current official template before physical implementation.
