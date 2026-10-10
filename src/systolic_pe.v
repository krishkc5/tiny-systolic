`default_nettype none
// Each operand and its validity travels one hop per enabled clock.
module systolic_pe (
    input wire clk, rst_n, clear, step,
    input wire signed [3:0] a_in, b_in,
    input wire av_in, bv_in,
    output reg signed [3:0] a_out, b_out,
    output reg av_out, bv_out,
    output wire signed [15:0] acc
);
    // K<=16 bounds the sum to [-896,1024]. Signed 12 bits suffice.
    wire signed [11:0] sum;
    assign acc = {{4{sum[11]}}, sum};
    mac_pe #(.ACC_W(12)) mac (.clk(clk), .rst_n(rst_n), .clear(clear),
        .valid(step & av_in & bv_in), .a(a_in), .b(b_in), .acc(sum));
    always @(posedge clk) begin
        if (!rst_n || clear) begin
            a_out <= 0; b_out <= 0; av_out <= 0; bv_out <= 0;
        end else if (step) begin
            a_out <= a_in; b_out <= b_in;
            av_out <= av_in; bv_out <= bv_in;
        end
    end
endmodule
