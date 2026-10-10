# Tiny Tapeout pricing and area

Checked 2026-10-10 against the live official calculator and current official HDL templates.

## Price snapshot (EUR)

Calculator settings: Individual, Digital (where offered), one PCB/devkit, worldwide economy shipping. SKY130, IHP, and GF180 each displayed EUR 70 for one tile, EUR 100 discounted devkit (EUR 300 full price), and EUR 15 shipping: EUR 185 total. This is a calculator estimate, not a reservation or checkout quote. Taxes/import duties were not separately explained on the viewed screen and are not assumed covered. Shuttle availability must be checked when submitting; presence in the calculator does not guarantee an open run.

SKY130 prices directly checked:

| Tiles | Tile cost | Discounted devkit | Shipping | Individual total | Full-price total |
|---|---:|---:|---:|---:|---:|
| 1 | 70 | 100 | 15 | 185 | 385 |
| 2 | 140 | 100 | 15 | 255 | 455 |
| 4 | 280 | 100 | 15 | 395 | 595 |

The calculator warns that reduced individual pricing is limited and may run out. Full-price totals use the EUR 300 devkit. The one-tile full-price total was also checked in Academic/Industry mode. No purchase was made.

Source: https://app.tinytapeout.com/calculator?pcbs=1&tiles=1&shuttle=chipfoundry
Other viewed selectors: shuttle=gf180 and shuttle=ihp. Select Individual in the page UI; the URL alone may not preserve that setting.

## Area

| Process template | Approximate single tile | Approximate footprint | Valid tile configurations |
|---|---|---|---|
| SKY130 | 167 x 108 micrometers | 18,036 square micrometers (0.018036 mm²) | 1x1, 1x2, 2x2, 3x2, 4x2, 6x2, 8x2 |
| IHP | 167 x 108 micrometers | 18,036 square micrometers (0.018036 mm²) | 1x1, 1x2, 2x2, 3x2, 4x2, 6x2, 8x2 |
| GF180 | 340 x 160 micrometers | 54,400 square micrometers (0.0544 mm²) | 1x1, 1x2, 2x2, 3x2, 4x2, 3x4, 4x4 |

These are approximate template dimensions, not guaranteed usable standard-cell area. Different processes have different cell sizes; the larger GF tile is not automatically three times the logic capacity. Use the actual shuttle floorplan and physical-flow reports for fit. Multi-tile dimensions should come from that flow, not simply multiplying these rounded dimensions.

Sources:
- https://github.com/TinyTapeout/ttsky-verilog-template/blob/main/info.yaml
- https://github.com/TinyTapeout/ttihp-verilog-template/blob/main/info.yaml
- https://github.com/TinyTapeout/ttgf-verilog-template/blob/main/info.yaml

The FAQ's roughly 160 x 100 micrometer / 1,000-gate description explicitly concerns TT04–TT10. Do not use it as a precise current area budget.

## Requirements and project implications

- Select the template matching the shuttle process and declare a supported `tiles` value in info.yaml.
- Preserve the standard top-level interface: clock, active-low reset, enable, eight inputs, eight outputs, eight bidirectional pins and their output-enable signals.
- List every source file, fill project metadata and pin documentation, and provide meaningful tests.
- Passing synthesis alone does not establish fit. The design must complete the official physical implementation and required checks; passing GDS and documentation builds are required before submission.
- Submit a specific successful revision through the Tiny Tapeout portal. Updating GitHub alone does not update a submitted revision.
- It is possible to try larger tile configurations before buying them. For this accelerator, explore one, two, and four tiles; none is yet validated for the full design.
- Current local info.yaml and single-MAC wrapper are bring-up scaffolding. The full array and controller remain milestones. Official SKY26d physical workflows are now installed.

Sources:
https://tinytapeout.com/faq/
https://www.tinytapeout.com/guides/advanced-workshop/submit-your-design/
https://github.com/TinyTapeout/ttsky-verilog-template/blob/main/src/project.v
