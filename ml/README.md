# Real ML inference on TinySystolic

The 64→16→10 ReLU network recognizes scikit-learn's 8×8 handwritten digits. The fixed stratified split has 1,437 training and 360 held-out test images. Training, weight quantization, and hidden-activation calibration use training data only; test data are used once for evaluation, with no scale tuning against labels.

- Float model: 344/360 correct (95.56%).
- INT4 model: 327/360 correct (90.83%).
- RTL: 327/360, all predictions and hidden quantized values match the integer reference.
- Every one of 6,660 matrix-tile transactions matches exactly; zero mismatches.

## What the chip does

All dense-layer multiplications/accumulations execute on the simulated chip through its external byte interface. Two images form the two array rows. The 64-input first layer is split into four K=16 chunks for each pair of output neurons. Host software combines chunk results in wider integers. It also applies floating-point bias/scales, ReLU, rounding/clipping to 0..7, and argmax. This is a host-assisted inference accelerator, not a self-contained neural-network chip. Both weights and activations fit signed INT4; nonnegative activations use 0..7.

Weight scales are per output channel. The hidden activation scale is a single maximum-range scale calibrated on the training set. The 4.72 percentage-point accuracy loss is quantization loss, not an RTL mismatch. Improving training/quantization remains possible, using a separate validation split rather than optimizing against this held-out test set.

## Reproduce

```sh
. .venv/bin/activate
pip install -r ml/requirements.txt
make ml-train
make ml-test
```

Training uses scikit-learn's bundled dataset; no external data downloads are needed. The committed JSON fixture lets normal RTL and gate-level CI test inference without installing ML training libraries. `make check` includes this inference regression. Training is deterministic with the pinned libraries, fixed seed and one BLAS thread, although numerical variation across platforms can affect model fitting.

## Timing interpretation

Each two-image batch uses 37 K=16 tile transactions: 32 for layer one and five for layer two. Each tile consumes 43 protocol clocks, so **1,591 cycles per pair** (286,380 total for 360 images). At the intended 10 MHz operating clock, that is 159.1 microseconds per pair of ideal chip-protocol time. This excludes host computation, transport latency and host idle periods; it is not a measured end-to-end or silicon performance claim.

Reports: ../reports/ml-software.json and ../reports/ml-rtl.json.
