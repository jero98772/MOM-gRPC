# generate_proto.py
import os
import sys

def generate_proto():
    """Generate Python code from the .proto file"""
    print("Generating Python code from calculator.proto...")
    
    # Check if grpcio-tools is installed
    try:
        import grpc_tools.protoc
    except ImportError:
        print("Error: grpcio-tools not installed.")
        print("Please install it with: pip install grpcio-tools")
        return False
    
    # Create proto file if it doesn't exist
    proto_file = "calculator.proto"
    if not os.path.exists(proto_file):
        with open(proto_file, "w") as f:
            f.write('''syntax = "proto3";

package calculator;

service Calculator {
  rpc Add (CalculationRequest) returns (CalculationResponse) {}
  rpc Subtract (CalculationRequest) returns (CalculationResponse) {}
  rpc Multiply (CalculationRequest) returns (CalculationResponse) {}
  rpc Divide (CalculationRequest) returns (CalculationResponse) {}
}

message CalculationRequest {
  float num1 = 1;
  float num2 = 2;
  string operation_id = 3;  // Unique identifier for tracking operations
}

message CalculationResponse {
  float result = 1;
  string operation_id = 2;
  bool success = 3;
  string error_message = 4;
}''')
    
    # Generate the Python code
    proto_include = os.path.dirname(os.path.abspath(grpc_tools.protoc.__file__)) + "/_proto"
    
    ret_code = grpc_tools.protoc.main([
        "grpc_tools.protoc",
        f"-I{proto_include}",
        "-I.",  # Add current directory to proto path
        "--python_out=.",
        "--grpc_python_out=.",
        proto_file
    ])
    
    if ret_code != 0:
        print(f"Error: Proto compilation failed with code {ret_code}")
        return False
    
    print("Proto files generated successfully!")
    return True

if __name__ == "__main__":
    generate_proto()