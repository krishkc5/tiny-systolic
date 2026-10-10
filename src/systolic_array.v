`default_nettype none
// Unskewed boundary input: A[:,k] and B[k,:], one quartet per valid step.
// clear resets both pipeline and accumulators; step=0 freezes everything.
module systolic_array (
    input wire clk, rst_n, clear, step, valid,
    input wire signed [3:0] a0, a1, b0, b1,
    output wire signed [15:0] c00, c01, c10, c11
);
    reg signed [3:0] a1_skew, b1_skew;
    reg skew_valid;
    always @(posedge clk) begin
        if (!rst_n || clear) begin
            a1_skew <= 0; b1_skew <= 0; skew_valid <= 0;
        end else if (step) begin
            a1_skew <= a1; b1_skew <= b1; skew_valid <= valid;
        end
    end
    wire signed [3:0] a00, b00, a10, b01;
    wire av00, bv00, av10, bv01;
    wire [3:0] unused_a01, unused_b10, unused_a11, unused_b11;
    wire unused_av01, unused_bv10, unused_av11, unused_bv11;
    systolic_pe p00 (.clk(clk), .rst_n(rst_n), .clear(clear), .step(step),
        .a_in(a0), .b_in(b0), .av_in(valid), .bv_in(valid),
        .a_out(a00), .b_out(b00), .av_out(av00), .bv_out(bv00), .acc(c00));
    systolic_pe p01 (.clk(clk), .rst_n(rst_n), .clear(clear), .step(step),
        .a_in(a00), .b_in(b1_skew), .av_in(av00), .bv_in(skew_valid),
        .a_out(unused_a01), .b_out(b01), .av_out(unused_av01), .bv_out(bv01), .acc(c01));
    systolic_pe p10 (.clk(clk), .rst_n(rst_n), .clear(clear), .step(step),
        .a_in(a1_skew), .b_in(b00), .av_in(skew_valid), .bv_in(bv00),
        .a_out(a10), .b_out(unused_b10), .av_out(av10), .bv_out(unused_bv10), .acc(c10));
    systolic_pe p11 (.clk(clk), .rst_n(rst_n), .clear(clear), .step(step),
        .a_in(a10), .b_in(b01), .av_in(av10), .bv_in(bv01),
        .a_out(unused_a11), .b_out(unused_b11), .av_out(unused_av11), .bv_out(unused_bv11), .acc(c11));
    wire _unused = &{unused_a01, unused_b10, unused_a11, unused_b11,
        unused_av01, unused_bv10, unused_av11, unused_bv11, 1'b0};
endmodule
