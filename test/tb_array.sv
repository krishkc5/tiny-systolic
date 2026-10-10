`timescale 1ns/1ps
module tb_array;
    reg clk=0,rst_n=0,clear=0,step=1,valid=0;
    reg signed [3:0] a0=0,a1=0,b0=0,b1=0;
    wire signed [15:0] c00,c01,c10,c11;
    integer e00,e01,e10,e11,x0,x1,y0,y1;
    integer cycles;
    systolic_array dut (.*);
    task tick; #5; clk=1; #5; clk=0; endtask
    task check;
        if (int'(c00)!==e00 || int'(c01)!==e01 || int'(c10)!==e10 || int'(c11)!==e11)
            $fatal(1,"array mismatch: %0d %0d %0d %0d vs %0d %0d %0d %0d", c00,c01,c10,c11,e00,e01,e10,e11);
    endtask
    initial begin
        tick(); rst_n=1;
        for(int k=1;k<=16;k++) for(int trial=0;trial<100;trial++) begin
            clear=1; step=1; valid=0; tick(); clear=0;
            e00=0;e01=0;e10=0;e11=0;cycles=0;
            for(int t=0;t<k;t++) begin
                if(trial!=0) begin
                    valid=0;
                    repeat($urandom_range(0,3)) tick();
                end
                x0=int'($urandom_range(0,15))-8; x1=int'($urandom_range(0,15))-8;
                y0=int'($urandom_range(0,15))-8; y1=int'($urandom_range(0,15))-8;
                a0=4'(x0);a1=4'(x1);b0=4'(y0);b1=4'(y1);valid=1;
                if(trial!=0) begin step=0; repeat($urandom_range(0,2)) tick(); step=1; end
                tick(); cycles++;
                e00+=x0*y0;e01+=x0*y1;e10+=x1*y0;e11+=x1*y1;
            end
            valid=0;tick();tick();cycles+=2;check();
            if(trial==0 && cycles!=k+2) $fatal(1,"unexpected ideal latency");
            repeat(5) tick();check();
        end
        clear=1;tick();clear=0;valid=1;a0=-8;a1=-8;b0=-8;b1=-8;tick();
        rst_n=0;tick();rst_n=1;valid=0;repeat(4)tick();e00=0;e01=0;e10=0;e11=0;check();
        $display("PASS: 1600 array operations, all K, full-rate streaming, bubbles, freeze, reset");$finish;
    end
endmodule
