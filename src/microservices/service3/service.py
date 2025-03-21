# microservices/service3/service.py
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
from common.protos.service3_pb2 import OrderRequest, OrderResponse, CreateOrderRequest
from common.protos.service3_pb2_grpc import OrderServiceServicer, add_OrderServiceServicer_to_server
from common.protos.service1_pb2 import UserRequest
from common.protos.service1_pb2_grpc import UserServiceStub
from common.protos.service2_pb2 import ProductRequest
from common.protos.service2_pb2_grpc import ProductServiceStub

# In-memory storage (would be replaced by a database in a real system)
orders: Dict[str, Dict[str, Any]] = {}

class OrderService(OrderServiceServicer):
    def __init__(self, mom_url="http://localhost:8000", 
                 user_service_addr="localhost:50051",
                 product_service_addr="localhost:50052"):
        # Set up MOM connection
        self.mom_url = mom_url
        self.queue_name = "order_service_queue"
        
        # Set up gRPC connections to other microservices
        self.user_channel = grpc.insecure_channel(user_service_addr)
        self.user_service = UserServiceStub(self.user_channel)
        
        self.product_channel = grpc.insecure_channel(product_service_addr)
        self.product_service = ProductServiceStub(self.product_channel)
        
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
                
                if operation == "create_order":
                    # Process create order operation
                    order_id = data.get("order_id", str(uuid.uuid4()))
                    orders[order_id] = {
                        "order_id": order_id,
                        "user_id": data.get("user_id", ""),
                        "product_ids": data.get("product_ids", []),
                        "total_price": data.get("total_price", 0.0),
                        "status": data.get("status", "pending")
                    }
                    print(f"Processed queued create order: {order_id}")
                
                # Add other operations as needed
                
        except Exception as e:
            print(f"Error processing pending messages: {e}")
    
    def GetOrder(self, request, context):
        order_id = request.order_id
        if order_id not in orders:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Order with ID {order_id} not found")
            return OrderResponse()
        
        order = orders[order_id]
        return OrderResponse(
            order_id=order["order_id"],
            user_id=order["user_id"],
            product_ids=order["product_ids"],
            total_price=order["total_price"],
            status=order["status"]
        )
    
    def CreateOrder(self, request, context):
        try:
            # Verify user exists
            try:
                user_response = self.user_service.GetUser(UserRequest(user_id=request.user_id))
            except grpc.RpcError as e:
                context.set_code(e.code())
                context.set_details(f"Error verifying user: {e.details()}")
                return OrderResponse()
            
            # Verify products exist and calculate total price
            total_price = 0.0
            for product_id in request.product_ids:
                try:
                    product_response = self.product_service.GetProduct(ProductRequest(product_id=product_id))
                    total_price += product_response.price
                except grpc.RpcError as e:
                    context.set_code(e.code())
                    context.set_details(f"Error verifying product {product_id}: {e.details()}")
                    return OrderResponse()
            
            # Create the order
            order_id = str(uuid.uuid4())
            order = {
                "order_id": order_id,
                "user_id": request.user_id,
                "product_ids": list(request.product_ids),
                "total_price": total_price,
                "status": "pending"
            }
            orders[order_id] = order
            
            # Queue the operation for fault tolerance
            self.queue_operation("create_order", order)
            
            return OrderResponse(
                order_id=order_id,
                user_id=request.user_id,
                product_ids=list(request.product_ids),
                total_price=total_price,
                status="pending"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating order: {str(e)}")
            return OrderResponse()
    
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

def serve(port=50053):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Order service started on port {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
