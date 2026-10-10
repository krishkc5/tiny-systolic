# How it works

Scaffold status: single signed INT4 multiply-accumulate unit with INT16 result.
The planned 2x2 systolic array is not implemented. Do not submit this scaffold as the finished accelerator.

# How to test

Run `make check`. Hold rst_n low across a rising clock edge. A is ui_in[3:0], B is ui_in[7:4], both signed. uio_in[0] clears, uio_in[1] enables accumulation when ena is high, uio_in[2] chooses high result byte (otherwise low). Clear takes priority. The accumulator wraps at 16 bits if used beyond its planned bounded workload. All bidirectional pins are inputs. Drive inputs synchronously. Read results only while accumulation is stopped for a coherent two-byte read.

# External hardware

None for simulation. Future silicon demo will need the matching Tiny Tapeout board and a host interface.
