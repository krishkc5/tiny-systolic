# Accumulator-width optimization

Baseline: 8f49f602017c429c50157e5656e8ad2f33f91345, successful SKY26d run 38080572847. Baseline physical summary is preserved in physical-baseline.json.

Each signed INT4 product lies in −56..64. The controller admits at most K=16 products per result, and the bound holds for every partial sum. Therefore sums lie in −896..1024. Signed 12 bits (−2048..2047) suffice; 11 bits fail for +1024. Four accumulators can lose four storage/adder bits each, with no change to the 16-bit external interface, protocol or supported workload. The reusable standalone MAC defaults to 16 bits; the array instantiates 12-bit MACs.

All existing arithmetic/protocol tests pass, including the +1024 and −896 endpoints. The real ML test additionally checks 6,660 tiles, with identical predictions. Ideal transaction cycle counts are unchanged. This optimization targets area and potentially timing/power, not algorithmic throughput. Power reduction is not claimed without switching-activity analysis.

Baseline routed standard-cell area: 13,309 µm²; worst setup slack +5.062 ns, hold +0.114 ns. The official flow actually used a 20 ns clock constraint (50 MHz) despite info.yaml's intended 10 MHz operating frequency. Floorplan from the flow is 161 × 111.52 µm for one tile. Report clock constraints explicitly; do not infer maximum frequency from one slack number. Both baseline and candidate must use identical flow/constraints for comparison.

Candidate physical build pending. Keep baseline as fallback until the optimized design passes GDS, precheck and gate-level testing. The baseline already fits one tile, so an area reduction alone will not reduce the tile purchase price.
