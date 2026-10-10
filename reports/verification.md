# Full RTL verification — 2026-10-10

Local results:

- Strict Verilator lint: PASS (only filename/module-name convention warning disabled).
- MAC: all 256 signed INT4 products; accumulation, invalid hold, clear priority and reset PASS.
- Array: 1,600 operations (100 per K=1..16), full-rate input, random bubbles, enable freezes, repeated clear, pipeline reset and output stability PASS. Ideal K+2 enabled-step latency checked on full-rate cases.
- Full chip: 497 arithmetic transactions (256 exhaustive repeated-pair cases, 48 extrema/zero cases, 192 seeded random cases, one identity), plus recovery tests PASS with Icarus/cocotb.
- Protocol: START validation, invalid opcodes/state commands, pauses between bytes, disabled commands, exact two-edge drain, READ rejection at drain completion, read-pointer wrap/hold, sticky error/recovery, abort and reset in each controller phase PASS.
- Every unstalled arithmetic transaction checks 2K+11 cycles from START through eight READ edges.
- Three Python matrix-reference tests PASS.
- Yosys generic synthesis and structural checks PASS. Generic cell counts are not physical area estimates.

Commands: activate .venv; `make check`; `make synth`.
Random seeds: chip tests use 20261010; core test uses the simulator's deterministic default seed.

The official SKY26d workflow runs the same package-level cocotb tests against the routed netlist. See GitHub Actions for current physical checks. No silicon tests, power figures, clock-frequency measurements, trained-model accuracy, or board-throughput results are claimed.
