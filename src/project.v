`default_nettype none
// See docs/protocol.md. All commands are sampled on enabled rising edges.
module tt_um_krishkc5_tinysystolic (
    input wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input wire [7:0] uio_in,
    output wire [7:0] uio_out, uio_oe,
    input wire ena, clk, rst_n
);
    localparam [1:0] IDLE=0, LOAD=1, DRAIN=2, DONE=3;
    localparam [2:0] NOP=0, START=1, DATA=2, READ=3, ABORT=4;
    reg [1:0] state;
    reg [3:0] remaining;
    reg half, drain_last, error;
    reg [7:0] a_pair;
    reg [2:0] read_index;
    wire [2:0] command = uio_in[2:0];
    wire start_ok = command == START && (state == IDLE || state == DONE) && ui_in[7:4] == 0;
    wire clear = ena && (command == ABORT || start_ok);
    wire inject = ena && state == LOAD && command == DATA && half;
    wire signed [15:0] c00, c01, c10, c11;
    systolic_array array (.clk(clk), .rst_n(rst_n), .clear(clear), .step(ena), .valid(inject),
        .a0(a_pair[3:0]), .a1(a_pair[7:4]), .b0(ui_in[3:0]), .b1(ui_in[7:4]),
        .c00(c00), .c01(c01), .c10(c10), .c11(c11));

    always @(posedge clk) begin
        if (!rst_n) begin
            state <= IDLE; remaining <= 0; half <= 0; drain_last <= 0;
            error <= 0; a_pair <= 0; read_index <= 0;
        end else if (ena) begin
            // Pipeline continues through command errors; invalid commands do not
            // consume input data, change read position, or restart the operation.
            if (state == DRAIN) begin
                if (drain_last) state <= DONE;
                else drain_last <= 1;
            end
            case (command)
                NOP: begin end
                ABORT: begin
                    state <= IDLE; remaining <= 0; half <= 0; drain_last <= 0;
                    error <= 0; a_pair <= 0; read_index <= 0;
                end
                START: begin
                    if (start_ok) begin
                        state <= LOAD; remaining <= ui_in[3:0]; half <= 0;
                        drain_last <= 0; error <= 0; read_index <= 0;
                    end else error <= 1;
                end
                DATA: begin
                    if (state == LOAD) begin
                        if (!half) begin a_pair <= ui_in; half <= 1; end
                        else begin
                            half <= 0;
                            if (remaining == 0) begin state <= DRAIN; drain_last <= 0; end
                            else remaining <= remaining - 1'b1;
                        end
                    end else error <= 1;
                end
                READ: begin
                    if (state == DONE) read_index <= read_index + 1'b1;
                    else error <= 1;
                end
                default: error <= 1;
            endcase
        end
    end
    reg [15:0] selected;
    always @* begin
        case (read_index[2:1])
            0: selected = c00;
            1: selected = c01;
            2: selected = c10;
            default: selected = c11;
        endcase
    end
    assign uo_out = state == DONE ? (read_index[0] ? selected[15:8] : selected[7:0]) : 8'b0;
    assign uio_oe = 8'hf0;
    assign uio_out = {error, state == DONE, state == LOAD || state == DRAIN,
                      ena && state == LOAD, 4'b0};
    wire _unused = &{uio_in[7:3], 1'b0};
endmodule
