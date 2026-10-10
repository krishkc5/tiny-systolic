PYTHON ?= python3
RTL = src/mac_pe.v src/project.v
.PHONY: check lint test model-test synth
check: lint test model-test
lint:
	verilator --lint-only -Wall --top-module tt_um_krishkc5_tinysystolic -Wno-DECLFILENAME $(RTL)
test:
	mkdir -p build
	verilator --binary --timing --top-module tb_mac -Wno-TIMESCALEMOD --Mdir build/obj $(RTL) test/tb_mac.sv > build/compile.log 2>&1
	./build/obj/Vtb_mac
model-test:
	$(PYTHON) -m unittest discover -s test -p 'test_*.py' -v
synth:
	mkdir -p reports
	yosys -p 'read_verilog $(RTL); synth -top tt_um_krishkc5_tinysystolic; check; stat' > reports/synthesis-generic.txt
