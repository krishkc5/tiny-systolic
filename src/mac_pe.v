`default_nettype none
// Signed INT4 x INT4, configurable accumulator (ACC_W >= 8). clear overrides valid.
module mac_pe #(parameter ACC_W = 16) (
    input wire clk, rst_n, clear, valid,
    input wire signed [3:0] a, b,
    output reg signed [ACC_W-1:0] acc
);
    wire signed [7:0] product = a * b;
    always @(posedge clk) begin
        if (!rst_n || clear) acc <= {ACC_W{1'b0}};
        else if (valid) acc <= acc + {{(ACC_W-8){product[7]}}, product};
    end
endmodule
