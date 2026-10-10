# TinySystolic technical report and evidence

Evidence cutoff: 2026-10-10. Report: 22 pages, with 11 numbered figures.

- [Readable report](TinySystolic_Technical_Report.md)
- [Editable Word report](deliverables/TinySystolic_Technical_Report.docx)
- `evidence/`: compact original metrics, configs, timing reports, run metadata, test logs, result XML, layout renders, source snapshot and captured trace.
- `figures/`: vector and raster diagrams/charts; the confusion matrix is calculated from the committed fixture.
- `analysis/`: report/figure generation and trace bench. Generated diagrams are conceptual where labelled; layout renders and trace values are observed artifacts.
- `SHA256SUMS`: integrity hashes for the compact report package, excluding itself and large ZIP outputs.

## Evidence provenance

The optimized source is f5fd8804b6859e741a871e7ea7580a31b0cb1a06, physical run 38081509655. The baseline is 8f49f602017c429c50157e5656e8ad2f33f91345, physical run 38080572847. Report sections 20–21 map evidence identifiers E1–E11 to their source files, workflows and reproduction steps. The source archive includes the dataset notice and exact model fixture; the source code license does not replace the dataset license.

Workflow JSON retains job results and timestamps. The copied Actions log removes ANSI formatting and ephemeral URL query strings; technical result lines are retained. Other compact metrics/check reports are copied from the archived artifacts. JSON metrics retain the flow's non-finite Infinity sentinel; consumers requiring strict JSON must handle it explicitly.

The local `deliverables/TinySystolic_Evidence.zip` additionally preserves the full downloaded baseline and optimized physical artifact trees and optimized gate-level results/waveform. Its `MANIFEST.sha256` hashes every payload file. The large ZIP is deliberately excluded from Git; preserve it separately. These records capture available evidence, not reconstructed logs of overwritten or unrecorded runs.

## Signoff status

RTL and functional gate-level regressions pass, with all 6,660 ML tiles matching the software reference. Area improves by 12.466%. Detailed STA nevertheless reports 183 worst-corner transition violations and one clock-buffer fanout violation. Register-to-register setup summary semantics and 17 unannotated drivers need review. No waiver or repair is asserted. Passing workflows are not complete electrical signoff.

## Report generation and validation

The report uses Python with python-docx and reportlab; SVG rasterization uses Node and sharp. Generation order: `analysis/make_figures.py`, `analysis/rasterize.cjs`, then `analysis/build_report.py`. The fixed fixture and evidence inputs must remain available. The DOCX was rendered and every page visually reviewed; numerical tables retain original evidence alongside rounded display values. No RTL was modified for this report.

## LaTeX edition

[LaTeX source](TinySystolic_Technical_Report.tex) and [compilation instructions](LATEX_README.md). The local deliverables/TinySystolic_LaTeX.zip includes all companion figures for Overleaf. The standalone desktop preview compiles with labelled image placeholders because companion files are unsupported. The original SHA256SUMS and evidence ZIP document the earlier Word-report snapshot; these LaTeX additions do not alter it.
