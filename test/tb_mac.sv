`timescale 1ns/1ps
module tb_mac;
    reg clk=0, rst_n=0, ena=1;
    reg [7:0] ui_in=0, uio_in=0;
    wire [7:0] uo_out, uio_out, uio_oe;
    integer expected;
    tt_um_krishkc5_tinysystolic dut (.*);
    task tick;
        #5; clk=1; #5; clk=0;
    endtask
    task check(input integer value);
        uio_in[2]=0; #1;
        if (uo_out !== 8'(value)) $fatal(1,"low byte mismatch");
        uio_in[2]=1; #1;
        if (uo_out !== 8'(value >>> 8)) $fatal(1,"high byte mismatch");
        if (uio_out !== 0 || uio_oe !== 0) $fatal(1,"unsafe IO");
    endtask
    initial begin
        tick(); check(0); rst_n=1;
        for (int a=-8; a<8; a++) begin
            for (int b=-8; b<8; b++) begin
                uio_in=1; tick();
                ui_in={4'(b),4'(a)}; uio_in=2; tick(); check(a*b);
            end
        end
        uio_in=1; tick(); expected=0;
        for (int i=0;i<16;i++) begin
            ui_in=8'h88; uio_in=2; tick(); expected+=64; check(expected);
        end
        uio_in=0; tick(); check(expected); // invalid holds accumulator
        ena=0; uio_in=2; tick(); check(expected);
        ena=1; uio_in=3; tick(); check(0); // clear beats valid
        uio_in=2; tick(); check(64);
        rst_n=0; tick(); check(0); // reset during active valid
        $display("PASS: 256 signed products, accumulation, bubble, enable, clear, reset and byte readback");
        $finish;
    end
endmodule
