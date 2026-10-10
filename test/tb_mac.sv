`timescale 1ns/1ps
module tb_mac;
    reg clk=0, rst_n=0, clear=0, valid=0;
    reg signed [3:0] a=0,b=0;
    wire signed [15:0] acc;
    mac_pe dut (.*);
    task tick; #5; clk=1; #5; clk=0; endtask
    initial begin
        tick(); if(acc !== 0) $fatal;
        rst_n=1;
        for(int i=-8;i<8;i++) for(int j=-8;j<8;j++) begin
            clear=1; tick(); clear=0; valid=1; a=4'(i); b=4'(j); tick();
            if (int'(acc) !== i*j) $fatal(1,"signed multiply mismatch");
        end
        clear=1; tick(); clear=0; a=-8; b=-8;
        for(int i=1;i<=16;i++) begin tick(); if(int'(acc) !== i*64) $fatal; end
        valid=0; tick(); if(acc !== 1024) $fatal;
        valid=1; clear=1; tick(); if(acc !== 0) $fatal;
        clear=0; tick(); rst_n=0; tick(); if(acc !== 0) $fatal;
        $display("PASS: exhaustive MAC arithmetic and controls"); $finish;
    end
endmodule
