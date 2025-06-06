import sys
import re
from pathlib import Path

ALU_TEXT = """\
module alu (
  input [31:0] a, b,
  input [1:0] ALUControl,
  output reg [31:0] Result,
  output wire [3:0] ALUFlags
);

wire neg, zero, carry, overflow;
wire [31:0] condinvb;
wire [32:0] sum; // suma 33 bits, carry bit 33

assign condinvb = ALUControl[0] ? ~b : b; // mux
assign sum = a + condinvb + ALUControl[0]; // a + b + cin

always @(*) begin
  casex (ALUControl[1:0])
    2'b0?: Result = sum;
    2'b10: Result = a & b;
    2'b11: Result = a | b;
  endcase
end

assign neg = Result[31];
assign zero = (Result == 32'b0);
assign carry = (ALUControl[1] == 1'b0) & sum[32];
assign overflow = (ALUControl[1] == 1'b0) & ~(a[31] ^ b[31] ^ ALUControl[0]) & (a[31] ^ sum[31]);
assign ALUFlags = {neg, zero, carry, overflow};

endmodule
"""

def split_modules(input_path: Path):
    text = input_path.read_text()

    module_re = re.compile(
        r'\bmodule\s+(\w+).*?\bendmodule\b',
        flags=re.DOTALL | re.IGNORECASE
    )

    matches = list(module_re.finditer(text))
    if not matches:
        print("No modules found in", input_path)
        return 0

    for m in matches:
        module_name = m.group(1)
        module_text = m.group(0).strip() + "\n"
        out_file = Path(f"{module_name}.v")
        if out_file.exists():
            print(f"Warning: {out_file} exists - overwriting.")
        out_file.write_text(module_text)
        print(f"-> Wrote {out_file}")

    return len(matches)

def write_alu_file():
    out_file = Path("alu.v")
    if out_file.exists():
        print("Warning: alu.v exists — overwriting.")
    out_file.write_text(ALU_TEXT)
    print("→ Wrote alu.v")

def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.is_file():
        print(f"Error: {input_path} is not a file.")
        sys.exit(1)

    count = split_modules(input_path)
    if count:
        print(f"\nSplit {count} module(s).")
    write_alu_file()
    print("Done.")

if __name__ == "__main__":
    main()
