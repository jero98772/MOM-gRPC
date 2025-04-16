import os
import uuid
import grpc
import json
from flask import Flask, request, jsonify
import calculator_pb2
import calculator_pb2_grpc
from mom_implementation import MessageBroker

app = Flask(__name__)

# Configuration
SERVICE_PORTS = {
    'add': 50051,
    'subtract': 50052,
    'multiply': 50053,
    'divide': 50054
}

# Health check endpoints for services
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "API Gateway is operational"}), 200

@app.route('/services/health', methods=['GET'])
def services_health_check():
    health_status = {}
    
    for service, port in SERVICE_PORTS.items():
        try:
            # Try to establish a gRPC connection to check if service is available
            with grpc.insecure_channel(f'localhost:{port}') as channel:
                future = grpc.channel_ready_future(channel)
                future.result(timeout=1)  # Wait for 1 second
                health_status[service] = "up"
        except Exception:
            health_status[service] = "down"
    
    return jsonify({"services": health_status}), 200

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Missing request body"}), 400
            
        # Validate required fields
        required_fields = ['operation', 'num1', 'num2']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        operation = data['operation'].lower()
        num1 = float(data['num1'])
        num2 = float(data['num2'])
        
        # Generate a unique operation ID
        operation_id = str(uuid.uuid4())
        
        # Check if operation is supported
        if operation not in SERVICE_PORTS:
            return jsonify({
                "error": f"Unsupported operation: {operation}",
                "supported_operations": list(SERVICE_PORTS.keys())
            }), 400
        
        port = SERVICE_PORTS[operation]
        
        # Create gRPC request
        calculation_request = calculator_pb2.CalculationRequest(
            num1=num1,
            num2=num2,
            operation_id=operation_id
        )
        
        # Set up retries for resilience
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with grpc.insecure_channel(f'localhost:{port}') as channel:
                    if operation == 'add':
                        stub = calculator_pb2_grpc.CalculatorStub(channel)
                        response = stub.Add(calculation_request)
                    elif operation == 'subtract':
                        stub = calculator_pb2_grpc.CalculatorStub(channel)
                        response = stub.Subtract(calculation_request)
                    elif operation == 'multiply':
                        stub = calculator_pb2_grpc.CalculatorStub(channel)
                        response = stub.Multiply(calculation_request)
                    elif operation == 'divide':
                        stub = calculator_pb2_grpc.CalculatorStub(channel)
                        response = stub.Divide(calculation_request)
                
                # Check if operation was successful
                if response.success:
                    return jsonify({
                        "operation": operation,
                        "num1": num1,
                        "num2": num2,
                        "result": response.result,
                        "operation_id": operation_id
                    }), 200
                else:
                    return jsonify({
                        "error": response.error_message or "Unknown error",
                        "operation_id": operation_id
                    }), 400
                    
            except grpc.RpcError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    # Log the operation to the MOM for later processing
                    queue = MessageBroker().get_queue(operation)
                    queue.enqueue({
                        'num1': num1,
                        'num2': num2,
                        'operation': operation,
                        'operation_id': operation_id
                    })
                    
                    return jsonify({
                        "error": f"Service unavailable after {max_retries} attempts. Request queued for later processing.",
                        "operation_id": operation_id,
                        "status": "queued"
                    }), 503
                
                # Wait before retrying
                import time
                time.sleep(1)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to check the status of a queued operation
@app.route('/operation/<operation_id>', methods=['GET'])
def check_operation_status(operation_id):
    # Check all service queues for the operation
    for service in SERVICE_PORTS.keys():
        queue = MessageBroker().get_queue(service)
        
        # This is a simplistic implementation - in a real system you'd have
        # a more efficient way to look up operations by ID
        pending_operations = queue.get_pending_operations()
        for op in pending_operations:
            if op['content'].get('operation_id') == operation_id:
                return jsonify({
                    "operation_id": operation_id,
                    "status": op['status'],
                    "service": service,
                    "timestamp": op['timestamp']
                }), 200
    
    return jsonify({
        "error": f"Operation ID {operation_id} not found or already processed"
    }), 404

if __name__ == '__main__':
    # Create the queues directory if it doesn't exist
    os.makedirs("queues", exist_ok=True)
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)