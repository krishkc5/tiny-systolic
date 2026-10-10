# Scaffold verification — 2026-10-10

- `make check`: PASS using Verilator 5.046 and Python 3.
- Exhaustive 256 signed operand pairs through the real bring-up wrapper.
- Sixteen accumulations of (-8)*(-8), invalid/enable holds, clear priority, reset during valid, both result bytes, and bidirectional output enables checked.
- Three Python reference tests pass: identity, maximal positive dot product, invalid dimensions/ranges.
- `make synth`: PASS using installed Yosys; structural check reports no problems.

Scope: single MAC and bring-up wrapper only. No full-array, neural-model, routed timing, physical area, power, or silicon results yet.
