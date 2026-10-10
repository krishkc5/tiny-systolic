# TinySystolic

An INT4 systolic-array ML accelerator for Tiny Tapeout.

**Status: runnable scaffold.** The signed multiply-accumulate building block and bring-up wrapper are implemented. The four-PE array, controller, trained ML demo, physical implementation, and performance measurements are still pending.

## Quick start

Requirements: Python 3, Verilator, make, and a C++ compiler. Yosys is optional.

```sh
make check   # RTL lint, exhaustive MAC test, integer-reference tests
make synth   # generic synthesis only; not physical area/timing
```

## Project map

- `src/`: synthesizable MAC and Tiny Tapeout bring-up wrapper
- `test/`: executable hardware and Python tests
- `model/`: signed INT4 matrix reference
- `benchmarks/`: metric contract and empty results schema
- `ml/`: digit-classifier integration plan
- `docs/architecture.md`: planned accelerator and verification milestones
- `docs/info.md`: implemented bring-up interface
- `docs/tiny-tapeout.md`: dated pricing and area research
- `docs/template-provenance.md`: official template version and migration steps
- `reports/`: generated synthesis and future physical reports
- `scripts/`: future host tooling

## Next milestones

1. Add operand forwarding, valid propagation, and a tested 2x2 array.
2. Define and verify the streaming byte interface and controller.
3. Implement equivalent sequential baseline and reproducible cycle benchmarks.
4. Train and quantize the digit model; verify inference through RTL.
5. Run the SKY26d physical flow on the completed accelerator to determine tile fit.

The repository uses the official SKY130 template with SKY26d workflows. `info.yaml` requests one tile at a 10 MHz target for bring-up only; neither is a full-accelerator result. GitHub workflows build the current single-MAC scaffold; no fabrication purchase or submission has been made.

## GitHub builds

The official SKY26d workflows run RTL simulation, layout generation, precheck, gate-level simulation, documentation, and the layout viewer. The separate verification workflow runs our Verilator and integer-model tests. `test/test.py` exercises the external interface in both RTL and gate-level simulation. Physical results initially describe only the single-MAC scaffold.
