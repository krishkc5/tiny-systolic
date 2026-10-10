`default_nettype none
// Fixed signed INT4 x INT4, INT16 accumulation. clear overrides valid.
module mac_pe (
    input wire clk, rst_n, clear, valid,
    input wire signed [3:0] a, b,
    output reg signed [15:0] acc
);
    wire signed [7:0] product = a * b;
    always @(posedge clk) begin
        if (!rst_n || clear) acc <= 16'sd0;
        else if (valid) acc <= acc + {{8{product[7]}}, product};
    end
endmodule
