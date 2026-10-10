# TinySystolic

A 2×2 signed INT4 systolic-array matrix accelerator for Tiny Tapeout SKY26d.

**Complete RTL and local verification.** Four processing elements compute C[2,2] = A[2,K] × B[K,2] for K=1..16 with 12-bit internal accumulators and 16-bit results. The byte-wide streaming controller provides start, operand transfer, result readback, abort, ready/busy/done and sticky error status. The host applies ML quantization, bias, activation, and larger-matrix tiling.

## Quick start

Requirements: Python 3.11, Icarus Verilog, Verilator, make, C++ compiler; Yosys for generic synthesis.

```sh
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r test/requirements.txt
make check
make synth
```

`make check` runs strict RTL lint, exhaustive MAC tests, 1,600 array tests, Python reference tests, and full-chip cocotb tests, including 360 digit-classifier images. Cocotb tests use package-level signals and are reused by the official gate-level workflow. Run `make chip-test` for only the full-chip suite.

## Architecture

A moves right, B moves down, and each PE keeps a local partial sum. Internal row/column skew aligns operands; separate valid bits prevent bubbles from accumulating stale data. The core supports a full quartet per clock. The chip receives two bytes per quartet and drains two enabled clocks after the last byte. No large operand memory is needed.

See [the protocol](docs/protocol.md) for the complete pin map, command semantics, result ordering, error handling, and cycle counts. Note that uio[7:4] are chip outputs: do not drive these from the host.

## Project map

- `src/mac_pe.v`: signed multiplier/accumulator
- `src/systolic_pe.v`: registered operand/valid forwarding
- `src/systolic_array.v`: four PEs and boundary skew
- `src/project.v`: streaming controller and Tiny Tapeout wrapper
- `test/`: MAC, core and pin-level chip tests
- `model/`: independent integer matrix reference
- `docs/`: architecture, protocol, submission metadata and pricing research
- `reports/`: test evidence and synthesis reports
- `benchmarks/`: performance metric definitions; no physical measurements yet
- `ml/`: trained INT4 digit classifier and reproducible training script

## Physical flow

Official SKY26d actions run RTL tests, GDS generation, precheck, gate-level simulation, docs, and the layout viewer. `info.yaml` requests one tile and a 10 MHz clock. The optimized design passes GDS, precheck, gate-level simulation (including ML), RTL tests and docs, with 12.5% lower routed standard-cell area. See reports/optimization.md for the exact validated revision. The flow uses a 20 ns timing constraint; 10 MHz is the intended operating clock. Generic synthesis is not a measurement of physical area or timing. No fabrication purchase or submission has been made.

## Remaining portfolio work

Improve INT4 accuracy if needed; add a board transport driver, a sequential scheduled baseline and performance plots; validate final physical results and eventually test silicon. The chip's RTL does not depend on completing those host-side tasks.

## ML result

The host-assisted digit classifier scores 90.83% on 360 held-out images versus 95.56% for the floating-point model. RTL exactly matches the quantized model across 6,660 matrix tiles. See [ML details](ml/README.md) for host/chip responsibilities and [optimization notes](reports/optimization.md) for the accumulator-width change.

## Technical report and evidence

The [22-page technical report](reports/technical/TinySystolic_Technical_Report.md) compiles design decisions, RTL and gate-level tests, ML validation, workflow history, layout images, and physical comparisons. The [editable Word report](reports/technical/deliverables/TinySystolic_Technical_Report.docx) and [evidence index](reports/technical/README.md) are preserved with the project.

**Electrical review remains open:** detailed STA reports show 183 worst-corner transition violations and one clock-buffer fanout violation despite passing workflows. Timing coverage also needs review. These findings must be resolved or explicitly accepted before final fabrication signoff.
