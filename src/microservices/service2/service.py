# microservices/service2/service.py
import grpc
import uuid
import time
from concurrent import futures
import sys
import os
import requests
import json
from typing import Dict, Any, List

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the generated protobuf modules
from common.protos.service2_pb2 import ProductRequest, ProductResponse, CreateProductRequest
from common.protos.service2_pb2_grpc import ProductServiceServicer, add_ProductServiceServicer_to_server

# In-memory storage (would be replaced by a database in a real system)
products: Dict[str, Dict[str, Any]] = {}

class ProductService(ProductServiceServicer):
    def __init__(self, mom_url="http://localhost:8000"):
        self.mom_url = mom_url
        # Queue name for product service operations
        self.queue_name = "product_service_queue"
        # Process any pending messages at startup
        self.process_pending_messages()
        
    def process_pending_messages(self):
        """Process any messages that were queued during downtime"""
        try:
            while True:
                response = requests.get(f"{self.mom_url}/queue/{self.queue_name}")
                if response.status_code == 404:
                    # No more messages
                    break
                    
                message = response.json()
                operation = message.get("operation")
                data = message.get("data", {})
                
                if operation == "create_product":
                    # Process create product operation
                    product_id = data.get("product_id", str(uuid.uuid4()))
                    products[product_id] = {
                        "product_id": product_id,
                        "name": data.get("name", ""),
                        "price": data.get("price", 0.0),
                        "description": data.get("description", "")
                    }
                    print(f"Processed queued create product: {product_id}")
                
                # Add other operations as needed
                
        except Exception as e:
            print(f"Error processing pending messages: {e}")
    
    def GetProduct(self, request, context):
        product_id = request.product_id
        if product_id not in products:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Product with ID {product_id} not found")
            return ProductResponse()
        
        product = products[product_id]
        return ProductResponse(
            product_id=product["product_id"],
            name=product["name"],
            price=product["price"],
            description=product["description"]
        )
    
    def CreateProduct(self, request, context):
        try:
            product_id = str(uuid.uuid4())
            product = {
                "product_id": product_id,
                "name": request.name,
                "price": request.price,
                "description": request.description
            }
            products[product_id] = product
            
            # Also queue the operation for fault tolerance
            self.queue_operation("create_product", {
                "product_id": product_id,
                "name": request.name,
                "price": request.price,
                "description": request.description
            })
            
            return ProductResponse(
                product_id=product_id,
                name=request.name,
                price=request.price,
                description=request.description
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating product: {str(e)}")
            return ProductResponse()
    
    def queue_operation(self, operation: str, data: Dict[str, Any]):
        """Queue an operation in the MOM for fault tolerance"""
        try:
            message = {
                "operation": operation,
                "data": data,
                "timestamp": time.time()
            }
            response = requests.post(
                f"{self.mom_url}/queue/{self.queue_name}",
                json={"content": message}
            )
            return response.json().get("message_id")
        except Exception as e:
            print(f"Error queueing operation {operation}: {e}")
            return None

def serve(port=50052):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Product service started on port {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

