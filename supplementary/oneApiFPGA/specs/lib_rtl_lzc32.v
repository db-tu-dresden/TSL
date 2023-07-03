`timescale 1 ps / 1 ps

module lzc2b_2022
(	input 	wire	[1:0]  in,
	output 	wire 	v,
	output	wire 	z
);
	assign v = ~|in;	
	assign z = (~in[1]) & in[0];
endmodule

module lzc4b_2022
(	input	wire 	[3:0] 	in,	 
	output 	wire 		v,
	output  wire	[1:0]	z
);
	wire v0,z0,v1,z1;
	lzc2b_2022 left_lzc2b
	(	.in(in[3:2]),
		.v(v1),
		.z(z1)
	);
	lzc2b_2022 right_lzc2b
	(	.in(in[1:0]),
		.v(v0),
		.z(z0)
	);
	assign v = v0 & v1;
	assign z[1] = v1;
	assign z[0] = ((~v1)&z1) | (v1&z0);  	
endmodule

module lzc8b_2022
(	input	wire 	[7:0] 	in,	 
	output 	wire 		v,
	output  wire	[2:0]	z
);
	wire v0,v1,z0,z1,z2,z3;
	lzc4b_2022 left_lzc4b
	(	.in(in[7:4]),
		.v(v1),
		.z({z3,z2})
	);
	lzc4b_2022 right_lzc4b
	(	.in(in[3:0]),
		.v(v0),
		.z({z1,z0})
	);
	assign v = v0 & v1;
	assign z[2] = v1;
	assign z[1] = ((~v1)&z3) | (v1&z1);
	assign z[0] = ((~v1)&z2) | (v1&z0);  	
endmodule

module lzc16b_2022
(	input	wire 	[15:0] 	in,	 
	output 	wire 		v,
	output  wire	[3:0]	z
);
	wire v0,v1,z0,z1,z2,z3,z4,z5;
	lzc8b_2022 left_lzc8b
	(	.in(in[15:8]),
		.v(v1),
		.z({z5,z4,z3})
	);
	lzc8b_2022 right_lzc8b
	(	.in(in[7:0]),
		.v(v0),
		.z({z2,z1,z0})
	);
	assign v = v0 & v1;
	assign z[3] = v1;
	assign z[2] = ((~v1)&z5) | (v1&z2);
	assign z[1] = ((~v1)&z4) | (v1&z1);
	assign z[0] = ((~v1)&z3) | (v1&z0);  	
endmodule

module lzc32b_2022
(	input	wire 	[31:0] 	in,	 
	output 	wire 		v,
	output  wire	[4:0]	z
);
	wire v0,v1,z0,z1,z2,z3,z4,z5,z6,z7;
	lzc16b_2022 left_lzc16b
	(	.in(in[31:16]),
		.v(v1),
		.z({z7,z6,z5,z4})
	);
	lzc16b_2022 right_lzc16b
	(	.in(in[15:0]),
		.v(v0),
		.z({z3,z2,z1,z0})
	);
	assign v = v0 & v1;
	assign z[4] = v1;
	assign z[3] = ((~v1)&z7) | (v1&z3);
	assign z[2] = ((~v1)&z6) | (v1&z2);
	assign z[1] = ((~v1)&z5) | (v1&z1);
	assign z[0] = ((~v1)&z4) | (v1&z0);  	
endmodule


module lzc32_uint_module (
  input   clock,
  input   resetn,
  input   ivalid,
  input   iready,
  output  ovalid,
  output  oready,
  input   [31:0]  datain_a,
  output  [31:0]  dataout);

  assign  ovalid = 1'b1;
  assign  oready = 1'b1;
  // clk, ivalid, iready, resetn are ignored

  wire [4:0] z_out; 
  wire v_out; 

  lzc32b_2022 dut_lzc32b_2022(
      .in(datain_a),
      .z(z_out),  
      .v(v_out)
   );
 
  assign dataout =  {26'b0,v_out,z_out};

endmodule

  
