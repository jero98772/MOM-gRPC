from flask import Flask, request, jsonify
import grpc
import uuid
import json
import requests
import os
import time
from concurrent import futures
import threading
from werkzeug.utils import url_quote


# Import the generated gRPC modules
import sys
sys.path.append('./proto')
import calculator_pb2
import calculator_pb2_grpc

app = Flask(__name__)

# Service endpoints
SERVICE_ENDPOINTS = {
    'add': os.getenv('ADDITION_SERVICE', 'localhost:50051'),
    'subtract': os.getenv('SUBTRACTION_SERVICE', 'localhost:50052'),
    'multiply': os.getenv('MULTIPLICATION_SERVICE', 'localhost:50053'),
    'divide': os.getenv('DIVISION_SERVICE', 'localhost:50054')
}

# MOM service endpoint
MOM_SERVICE = os.getenv('MOM_SERVICE', 'http://localhost:5001')

def send_to_mom(operation, a, b, request_id):
    """Send message to MOM in case of service failure"""
    try:
        message = {
            'operation': operation,
            'a': a,
            'b': b,
            'request_id': request_id
        }
        response = requests.post(f"{MOM_SERVICE}/queue", json=message)
        return response.status_code == 201
    except Exception as e:
        print(f"Failed to send to MOM: {e}")
        return False

@app.route('/calculate/<operation>', methods=['POST'])
def calculate(operation):
    """Handle calculation request from client"""
    if operation not in SERVICE_ENDPOINTS:
        return jsonify({'error': 'Invalid operation'}), 400
    
    data = request.get_json()
    if not data or 'a' not in data or 'b' not in data:
        return jsonify({'error': 'Missing parameters'}), 400
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    try:
        a = float(data['a'])
        b = float(data['b'])
        
        # Create gRPC channel to appropriate service
        with grpc.insecure_channel(SERVICE_ENDPOINTS[operation]) as channel:
            stub = calculator_pb2_grpc.CalculatorStub(channel)
            
            # Create request based on operation
            calc_request = calculator_pb2.CalculationRequest(
                a=a, b=b, request_id=request_id
            )
            
            # Call appropriate method based on operation
            if operation == 'add':
                response = stub.Add(calc_request)
            elif operation == 'subtract':
                response = stub.Subtract(calc_request)
            elif operation == 'multiply':
                response = stub.Multiply(calc_request)
            elif operation == 'divide':
                if b == 0:
                    return jsonify({'error': 'Division by zero'}), 400
                response = stub.Divide(calc_request)
                
            return jsonify({
                'result': response.result,
                'status': response.status,
                'request_id': response.request_id
            })
            
    except grpc.RpcError as e:
        print(f"gRPC service error: {e}")
        # Service failure - send to MOM
        if send_to_mom(operation, a, b, request_id):
            return jsonify({
                'status': 'queued',
                'message': 'Service temporarily unavailable. Your request has been queued.',
                'request_id': request_id
            }), 202
        else:
            return jsonify({'error': 'Service unavailable and queueing failed'}), 503
            
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status/<request_id>', methods=['GET'])
def check_status(request_id):
    """Check status of a queued request"""
    try:
        response = requests.get(f"{MOM_SERVICE}/status/{request_id}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)