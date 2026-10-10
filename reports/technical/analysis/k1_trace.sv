`timescale 1ns/1ps
module report_trace;
reg clk=0,rst_n=0,ena=1;
reg [7:0] ui_in=0,uio_in=0;
wire [7:0] uo_out,uio_out,uio_oe;
integer cycle=0;
reg [7:0] before_byte;
tt_um_krishkc5_tinysystolic dut(.*);
task edge_clock(input [2:0] command,input [7:0] data);
 begin
  uio_in={5'b0,command};ui_in=data;#50;
  before_byte=uo_out;clk=1;#50;
  $display("%0d,%0d,%02x,%02x,%02x,%02x",cycle,command,data,before_byte,uo_out,uio_out);
  clk=0;cycle=cycle+1;
 end
endtask
initial begin
 $dumpfile("reports/technical/evidence/k1-wave.vcd");$dumpvars(0,report_trace);
 $display("cycle,command,input,byte_before_edge,byte_after_edge,status_after_edge");
 edge_clock(0,0);rst_n=1;
 edge_clock(1,0);edge_clock(2,8'h78);edge_clock(2,8'h3e);
 edge_clock(0,0);edge_clock(0,0);
 if(uio_out!==8'h40 || uo_out!==8'h10) $fatal(1,"Unexpected K1 result");
 repeat(8)edge_clock(3,0);
 if(uo_out!==8'h10) $fatal(1,"Read pointer did not wrap");
 $finish;
end
endmodule
