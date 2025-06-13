`timescale 1ns / 1ps

module alu (
  input [31:0] a, b,
  input [2:0] ALUControl,
  output reg [31:0] Result,
  output wire [3:0] ALUFlags
);

wire neg, zero, carry, overflow;
wire [31:0] condinvb;
wire [32:0] sum;
wire [31:0] sign_mag;

assign condinvb = ALUControl[0] ? ~b : b;  // mux
assign sum = a + condinvb + ALUControl[0];  // a + b + cin

wire [31:0] abs_value = a[31] ? ~a : a;
assign sign_mag = (a == 32'h80000000) ? 0 : {a[31], abs_value[30:0]};

always @(*) begin
  casex (ALUControl[2:0])
    3'b00?: Result = sum[31:0];
    3'b010: Result = a & b;
    3'b011: Result = a | b;
    3'b110: Result = a ^ b;
    3'b111: Result = sign_mag;
    default: Result = 32'bx;
  endcase
end

assign neg = Result[31];
assign zero = (Result == 32'b0);
assign carry = (ALUControl[1] == 1'b0) & sum[32];
wire overflow_add_sub = ~(a[31] ^ b[31] ^ ALUControl[0]) & (a[31] ^ sum[31]);
assign overflow = ((ALUControl[1] == 1'b0) & overflow_add_sub) | ((ALUControl == 3'b111) & (a == 32'h80000000));
assign ALUFlags = {neg, zero, carry, overflow};

endmodule
