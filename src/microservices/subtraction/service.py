import grpc
import time
import threading
from concurrent import futures
import requests
import os

# Import the generated gRPC modules
import sys
sys.path.append('./proto')
import calculator_pb2
import calculator_pb2_grpc

# MOM service endpoint
MOM_SERVICE = os.getenv('MOM_SERVICE', 'http://localhost:5001')

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    """Implementation of Calculator service"""
    
    def Subtract(self, request, context):
        """Subtract two numbers"""
        try:
            result = request.a - request.b
            return calculator_pb2.CalculationResponse(
                result=result,
                status="success",
                request_id=request.request_id
            )
        except Exception as e:
            return calculator_pb2.CalculationResponse(
                result=0,
                status="error",
                error=str(e),
                request_id=request.request_id
            )
    
    def ProcessOperation(self, request, context):
        """Process operation from MOM recovery"""
        if request.operation == "subtract":
            return self.Subtract(
                calculator_pb2.CalculationRequest(
                    a=request.a, 
                    b=request.b, 
                    request_id=request.request_id
                ), 
                context
            )
        else:
            return calculator_pb2.CalculationResponse(
                status="error",
                error="Unsupported operation for this service",
                request_id=request.request_id
            )

def fetch_queued_messages():
    """Poll MOM for queued messages for this service"""
    while True:
        try:
            response = requests.get(f"{MOM_SERVICE}/messages/subtract")
            if response.status_code == 200:
                messages = response.json()
                if messages:
                    process_queued_messages(messages)
        except Exception as e:
            print(f"Failed to fetch messages: {e}")
        
        # Poll every 5 seconds
        time.sleep(5)

def process_queued_messages(messages):
    """Process messages retrieved from MOM"""
    servicer = CalculatorServicer()
    
    for message in messages:
        try:
            # Create dummy context for gRPC
            context = type('obj', (object,), {})
            
            # Process the operation
            request = calculator_pb2.OperationRequest(
                operation=message['operation'],
                a=message['a'],
                b=message['b'],
                request_id=message['request_id']
            )
            
            response = servicer.ProcessOperation(request, context)
            
            # Notify MOM of successful processing
            requests.post(
                f"{MOM_SERVICE}/complete",
                json={
                    'request_id': message['request_id'],
                    'result': response.result,
                    'status': response.status
                }
            )
        except Exception as e:
            print(f"Error processing queued message: {e}")

def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServicer(), server
    )
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Subtraction Service started on port 50052")
    
    # Start background thread to poll for queued messages
    message_thread = threading.Thread(target=fetch_queued_messages, daemon=True)
    message_thread.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()