# Accumulator-width optimization

Baseline: 8f49f602017c429c50157e5656e8ad2f33f91345, successful SKY26d run 38080572847. Baseline physical summary is preserved in physical-baseline.json.

Each signed INT4 product lies in −56..64. The controller admits at most K=16 products per result, and the bound holds for every partial sum. Therefore sums lie in −896..1024. Signed 12 bits (−2048..2047) suffice; 11 bits fail for +1024. Four accumulators can lose four storage/adder bits each, with no change to the 16-bit external interface, protocol or supported workload. The reusable standalone MAC defaults to 16 bits; the array instantiates 12-bit MACs.

All existing arithmetic/protocol tests pass, including the +1024 and −896 endpoints. The real ML test additionally checks 6,660 tiles, with identical predictions. Ideal transaction cycle counts are unchanged. This optimization targets area and potentially timing/power, not algorithmic throughput. Power reduction is not claimed without switching-activity analysis.

Baseline routed standard-cell area: 13,309 µm²; worst setup slack +5.062 ns, hold +0.114 ns. The official flow actually used a 20 ns clock constraint (50 MHz) despite info.yaml's intended 10 MHz operating frequency. Floorplan from the flow is 161 × 111.52 µm for one tile. Report clock constraints explicitly; do not infer maximum frequency from one slack number. Both baseline and candidate must use identical flow/constraints for comparison.

Candidate f5fd8804b6859e741a871e7ea7580a31b0cb1a06, physical run 38081509655. All checks passed: GDS, precheck, gate-level simulation (including the full ML fixture), viewer, RTL regressions and docs. Physical workflow completed in 7m48s. The baseline already fits one tile, so an area reduction alone will not reduce the tile purchase price.

## Routed comparison

Same SKY26d template/flow and 20 ns constraint; same one-tile floorplan.

| Metric | 16-bit baseline | 12-bit candidate |
|---|---:|---:|
| Standard-cell area (µm²) | 13,309.0 | 11,649.9 |
| Standard-cell utilization | 80.69% | 70.63% |
| Sequential cells | 112 | 96 |
| Worst setup slack (ns) | +5.062 | +6.255 |
| Worst hold slack (ns) | +0.114 | +0.115 |
| Final Magic DRC errors | 0 | 0 |
| LVS errors | 0 | 0 |
| K=16 full transaction cycles | 43 | 43 |
| Digit-model accuracy | 327/360 | 327/360 |

**Area reduction: 12.466%.** Setup margin improves by 1.192 ns at the same constraint. This is a routed tool result, not silicon frequency measurement. There is no demonstrated throughput or energy increase. Both designs' archived source passed the identical package-level arithmetic, protocol and 360-image inference regression locally. Every model tile matched the software reference for both designs.

Source artifacts: GDS_logs/runs/wokwi/final/metrics.json and src/config_merged.json from the two recorded runs. Their compact summaries are stored in physical-baseline.json and physical-optimized.json. Generic Yosys counts fell from 1,284 to 1,148, but physical area is the relevant comparison above.
