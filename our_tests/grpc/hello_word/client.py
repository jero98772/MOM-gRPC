import grpc
import hello_pb2
import hello_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = hello_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(hello_pb2.HelloRequest(name="World"))
        print(f"Greeter response: {response.message}")

if __name__ == "__main__":
    run()
