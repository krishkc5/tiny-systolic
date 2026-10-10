`default_nettype none
// Bring-up wrapper ONLY. This is one MAC, not the future systolic accelerator.
module tt_um_krishkc5_tinysystolic (
    input wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input wire [7:0] uio_in,
    output wire [7:0] uio_out, uio_oe,
    input wire ena, clk, rst_n
);
    wire signed [15:0] acc;
    mac_pe pe (.clk(clk), .rst_n(rst_n), .clear(uio_in[0]),
        .valid(uio_in[1] & ena), .a(ui_in[3:0]), .b(ui_in[7:4]), .acc(acc));
    assign uo_out = uio_in[2] ? acc[15:8] : acc[7:0];
    assign uio_out = 8'b0;
    assign uio_oe = 8'b0;
    wire _unused = &{uio_in[7:3], 1'b0};
endmodule
