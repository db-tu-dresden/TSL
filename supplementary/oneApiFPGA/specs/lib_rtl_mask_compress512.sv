module mask_compress_module #(
  VECTOR_SIZE = 8,
  DATA_WIDTH = 64
) (
  input   clock,
  input   resetn,
  input   ivalid,
  input   iready,
  output  ovalid,
  output  oready,
  input   [VECTOR_SIZE*DATA_WIDTH-1:0]  datain_src,
  input   [VECTOR_SIZE*DATA_WIDTH-1:0]  datain_a,
  input   [VECTOR_SIZE-1:0]  maskin,
  output  [(VECTOR_SIZE)*DATA_WIDTH-1:0]  dataout);

  logic ivalid_reg1;
  logic ovalid_reg1;
  logic [63:0] test;
  logic [VECTOR_SIZE*DATA_WIDTH-1:0] data_src_reg1;
  logic [VECTOR_SIZE*DATA_WIDTH-1:0] data_a_reg1;
  logic [VECTOR_SIZE*DATA_WIDTH-1:0] data_src_reg2;
  logic [VECTOR_SIZE*DATA_WIDTH-1:0] data_a_reg2;
  logic [VECTOR_SIZE-1:0] mask_reg1;
  logic [3:0] ones [VECTOR_SIZE];
  logic [3:0] position [VECTOR_SIZE];
  reg [VECTOR_SIZE*DATA_WIDTH-1:0] dataout_reg1;
  logic [3:0] index [VECTOR_SIZE];
  assign  ovalid = ovalid_reg1;
  assign  oready = 1'b1;
  assign  dataout = dataout_reg1;


 genvar i;
  
  //valid signal propagated from ivalid to ovalid (2 clk latency)
  always_ff @(posedge clock) begin 
    if(~resetn) begin
	ivalid_reg1 <= 1'b0;
	ovalid_reg1 <= 1'b0;
    end else begin
	ivalid_reg1 <= ivalid;
	ovalid_reg1 <= ivalid_reg1;
    end	
  end

  //input src and mask data stored in working registers
  always_ff @(posedge clock) begin
    if(~resetn)
      begin
	data_src_reg1 <= 'b0;
	data_a_reg1 <= 'b0;
	data_src_reg2 <= 'b0;
	data_a_reg2 <= 'b0;
	mask_reg1 <= 'b0;
      end
    else if (ivalid)
      begin
	data_src_reg1 <= datain_src;
	data_a_reg1 <= datain_a;
	mask_reg1 <= maskin;
 	data_src_reg2 <= data_src_reg1;
	data_a_reg2 <= data_a_reg1;
     end
  end

 
  //calculate input "a" data places in output reg eg.mask=01100110/index=XXXX6521
  integer idx1;
  integer idx2;
  always @(*) begin
    idx1 = 0;
    idx2 = 0;
    while (idx1 < VECTOR_SIZE) begin
      if (mask_reg1[idx1]==1) begin
       index[idx2]=idx1+1;
       idx2=idx2+1;
      end
      idx1 = idx1+1;
    end
  end

  //store calculated indexes in positions register
  generate
    for(i=0;i<VECTOR_SIZE;i++) begin : positions
       always_ff @(posedge clock) begin 
	  if (~resetn)
	    position[i] <= 'b0;
          else if (ivalid_reg1 && (i<$countones(mask_reg1)))
	    position[i] <= index[i];
          else
	    position[i] <= 'b0;
       end
    end
  endgenerate
 
// first word data_out[0]
// wor data_out1[DATA_WIDTH-1:0];
// assign dataout_reg1[DATA_WIDTH-1:0] = data_out1;
 always @(*) begin
     case(position[0])
       4'h1: dataout_reg1[DATA_WIDTH-1:0]  = data_a_reg1[DATA_WIDTH-1:0];
       4'h2: dataout_reg1[DATA_WIDTH-1:0]  = data_a_reg1[2*DATA_WIDTH-1:1*DATA_WIDTH];
       4'h3: dataout_reg1[DATA_WIDTH-1:0]  = data_a_reg1[3*DATA_WIDTH-1:2*DATA_WIDTH];
       4'h4: dataout_reg1[DATA_WIDTH-1:0]  = data_a_reg1[4*DATA_WIDTH-1:3*DATA_WIDTH];
       4'h5: dataout_reg1[DATA_WIDTH-1:0]  = data_a_reg1[5*DATA_WIDTH-1:4*DATA_WIDTH];
       4'h6: dataout_reg1[DATA_WIDTH-1:0]  = data_a_reg1[6*DATA_WIDTH-1:5*DATA_WIDTH];
       4'h7: dataout_reg1[DATA_WIDTH-1:0]  = data_a_reg1[7*DATA_WIDTH-1:6*DATA_WIDTH];
       4'h8: dataout_reg1[DATA_WIDTH-1:0]  = data_a_reg1[8*DATA_WIDTH-1:7*DATA_WIDTH];

//   generate
//	  for(i=0;i<VECTOR_SIZE;i++) begin
//		assign data_out1 = position[0] ? data_a_reg1[(i+1)*DATA_WIDTH-1:i*DATA_WIDTH] : 
//	  end
//   endgenerate


       default:  dataout_reg1[DATA_WIDTH-1:0]  = data_src_reg1[DATA_WIDTH-1:0];
     endcase
 end 
// word data_out[1]
 always @(*) begin
     case(position[1])
       4'h2: dataout_reg1[127:64]  = data_a_reg1[127:64];
       4'h3: dataout_reg1[127:64]  = data_a_reg1[191:128];
       4'h4: dataout_reg1[127:64]  = data_a_reg1[255:192];
       4'h5: dataout_reg1[127:64]  = data_a_reg1[319:256];
       4'h6: dataout_reg1[127:64]  = data_a_reg1[383:320];
       4'h7: dataout_reg1[127:64]  = data_a_reg1[447:384];
       4'h8: dataout_reg1[127:64]  = data_a_reg1[511:448];
       default:  dataout_reg1[127:64]  = data_src_reg1[127:64];
     endcase
 end 
// word data_out[2]
 always @(*) begin
     case(position[2])
       4'h3: dataout_reg1[191:128]  = data_a_reg1[191:128];
       4'h4: dataout_reg1[191:128]  = data_a_reg1[255:192];
       4'h5: dataout_reg1[191:128]  = data_a_reg1[319:256];
       4'h6: dataout_reg1[191:128]  = data_a_reg1[383:320];
       4'h7: dataout_reg1[191:128]  = data_a_reg1[447:384];
       4'h8: dataout_reg1[191:128]  = data_a_reg1[511:448];
       default:  dataout_reg1[191:128]  = data_src_reg1[191:128];
     endcase
 end 
// word data_out[3]
 always @(*) begin
     case(position[3])
       4'h4: dataout_reg1[255:192]  = data_a_reg1[255:192];
       4'h5: dataout_reg1[255:192]  = data_a_reg1[319:256];
       4'h6: dataout_reg1[255:192]  = data_a_reg1[383:320];
       4'h7: dataout_reg1[255:192]  = data_a_reg1[447:384];
       4'h8: dataout_reg1[255:192]  = data_a_reg1[511:448];
       default:  dataout_reg1[255:192]  = data_src_reg1[255:192];
     endcase
 end 
// word data_out[4]
 always @(*) begin
     case(position[4])
       4'h5: dataout_reg1[319:256]  = data_a_reg1[319:256];
       4'h6: dataout_reg1[319:256]  = data_a_reg1[383:320];
       4'h7: dataout_reg1[319:256]  = data_a_reg1[447:384];
       4'h8: dataout_reg1[319:256]  = data_a_reg1[511:448];
       default:  dataout_reg1[319:256]  = data_src_reg1[319:256];
     endcase
 end 

// word data_out[5]
 always @(*) begin
     case(position[5])
       4'h6: dataout_reg1[383:320]  = data_a_reg1[383:320];
       4'h7: dataout_reg1[383:320]  = data_a_reg1[447:384];
       4'h8: dataout_reg1[383:320]  = data_a_reg1[511:448];
       4'h0:  dataout_reg1[383:320]  = data_src_reg1[383:320];
       default:  dataout_reg1[383:320]  = data_src_reg1[383:320];
     endcase
 end 

 // word data_out[6]
 always @(*) begin
     case(position[6])
       4'h7: dataout_reg1[447:384]  = data_a_reg1[447:384];
       4'h8: dataout_reg1[447:384]  = data_a_reg1[511:448];
       4'h0:  dataout_reg1[447:384]  = data_src_reg1[447:384];
       default:  dataout_reg1[447:384]  = data_src_reg1[447:384];
     endcase
 end 
// word data_out[7]
 always @(*) begin
     case(position[7])
       4'h8: dataout_reg1[511:448]  = data_a_reg1[511:448];
       4'h0:  dataout_reg1[511:448]  = data_src_reg1[511:448];
       default:  dataout_reg1[511:448]  = data_src_reg1[511:448];
     endcase
 end 

endmodule


