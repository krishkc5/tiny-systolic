PYTHON ?= python3
RTL = src/mac_pe.v src/systolic_pe.v src/systolic_array.v src/project.v
.PHONY: check lint test model-test synth chip-test
check: lint test model-test chip-test
lint:
	verilator --lint-only -Wall --top-module tt_um_krishkc5_tinysystolic -Wno-DECLFILENAME $(RTL)
test:
	mkdir -p build
	verilator --binary --timing --top-module tb_mac -Wno-TIMESCALEMOD --Mdir build/obj $(RTL) test/tb_mac.sv > build/compile.log 2>&1
	./build/obj/Vtb_mac
	verilator --binary --timing --top-module tb_array -Wno-TIMESCALEMOD --Mdir build/array $(RTL) test/tb_array.sv > build/array-compile.log 2>&1
	./build/array/Vtb_array
model-test:
	$(PYTHON) -m unittest discover -s test -p 'test_*.py' -v
synth:
	mkdir -p reports
	yosys -p 'read_verilog $(RTL); synth -top tt_um_krishkc5_tinysystolic; check; stat' > reports/synthesis-generic.txt

chip-test:
	cd test && $(MAKE)
	$(PYTHON) -m cocotb_tools.check_results test/results.xml

ml-train:
	$(PYTHON) ml/train.py
ml-test:
	cd test && $(MAKE) COCOTB_TEST_MODULES=test_ml
	$(PYTHON) -m cocotb_tools.check_results test/results.xml
