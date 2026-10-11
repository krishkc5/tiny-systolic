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
    localparam [2:0] NOP=0, START=1, DATA=2, READ=3, ABORT=4, REUSE=5;
    reg [1:0] state;
    reg [3:0] remaining;
    reg half, drain_last, error;
    reg [7:0] a_pair;
    reg [2:0] read_index;
    // Fixed K=16 cache. A completed normal K=16 load captures B; REUSE
    // rotates the bank once per accepted A byte, returning after 16 steps.
    // Data bits need no reset: cache_valid prevents observation until filled.
    reg [127:0] weights;
    reg cache_valid, cache_fill, reuse_mode;
    wire [2:0] command = uio_in[2:0];
    wire start_ok = command == START && (state == IDLE || state == DONE) && ui_in[7:4] == 0;
    wire reuse_ok = command == REUSE && (state == IDLE || state == DONE)
                    && cache_valid && ui_in == 8'h0f;
    wire clear = ena && (command == ABORT || start_ok || reuse_ok);
    wire inject = ena && state == LOAD && command == DATA && (half || reuse_mode);
    wire [7:0] array_a = reuse_mode ? ui_in : a_pair;
    wire [7:0] array_b = reuse_mode ? weights[7:0] : ui_in;
    always @(posedge clk) begin
        if (rst_n && inject) weights <= {array_b, weights[127:8]};
    end
    wire signed [15:0] c00, c01, c10, c11;
    systolic_array array (.clk(clk), .rst_n(rst_n), .clear(clear), .step(ena), .valid(inject),
        .a0(array_a[3:0]), .a1(array_a[7:4]), .b0(array_b[3:0]), .b1(array_b[7:4]),
        .c00(c00), .c01(c01), .c10(c10), .c11(c11));

    always @(posedge clk) begin
        if (!rst_n) begin
            state <= IDLE; remaining <= 0; half <= 0; drain_last <= 0;
            error <= 0; a_pair <= 0; read_index <= 0;
            cache_valid <= 0; cache_fill <= 0; reuse_mode <= 0;
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
            cache_valid <= 0; cache_fill <= 0; reuse_mode <= 0;
                end
                START: begin
                    if (start_ok) begin
                        state <= LOAD; remaining <= ui_in[3:0]; half <= 0;
                        drain_last <= 0; error <= 0; read_index <= 0;
                        cache_valid <= 0; reuse_mode <= 0;
                        cache_fill <= ui_in[3:0] == 15;
                    end else error <= 1;
                end
                REUSE: begin
                    if (reuse_ok) begin
                        state <= LOAD; remaining <= 15; half <= 0;
                        drain_last <= 0; error <= 0; read_index <= 0;
                        reuse_mode <= 1; cache_fill <= 0;
                    end else error <= 1;
                end
                DATA: begin
                    if (state == LOAD) begin
                        if (!half && !reuse_mode) begin a_pair <= ui_in; half <= 1; end
                        else begin
                            half <= 0;
                            if (remaining == 0) begin
                                state <= DRAIN; drain_last <= 0;
                                if (cache_fill) cache_valid <= 1;
                            end
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
