import grpc
from concurrent import futures
import time

import hello_pb2
import hello_pb2_grpc

class GreeterService(hello_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        print(f"[Server] Received request: name={request.name}")  # Print when request is received
        response = hello_pb2.HelloReply(message=f"Hello, {request.name}!")
        print(f"[Server] Sending response: message={response.message}")  # Print before sending response
        return response

def serve():
    print("[Server] Initializing gRPC server...")  # Server setup message
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    print("[Server] Registering GreeterService...")  
    hello_pb2_grpc.add_GreeterServicer_to_server(GreeterService(), server)
    
    server_address = "[::]:50051"
    server.add_insecure_port(server_address)
    
    print(f"[Server] Starting server on {server_address}...")
    server.start()
    
    try:
        while True:
            time.sleep(86400)  # Keep server running
    except KeyboardInterrupt:
        print("[Server] Stopping server...")
        server.stop(0)
        print("[Server] Server stopped.")

if __name__ == "__main__":
    print("[Main] Starting server...")
    serve()
