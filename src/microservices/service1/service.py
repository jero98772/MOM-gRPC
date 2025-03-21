# microservices/service1/service.py
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
from common.protos.service1_pb2 import UserRequest, UserResponse, CreateUserRequest
from common.protos.service1_pb2_grpc import UserServiceServicer, add_UserServiceServicer_to_server

# In-memory storage (would be replaced by a database in a real system)
users: Dict[str, Dict[str, Any]] = {}

class UserService(UserServiceServicer):
    def __init__(self, mom_url="http://localhost:8000"):
        self.mom_url = mom_url
        # Queue name for user service operations
        self.queue_name = "user_service_queue"
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
                
                if operation == "create_user":
                    # Process create user operation
                    user_id = data.get("user_id", str(uuid.uuid4()))
                    users[user_id] = {
                        "user_id": user_id,
                        "name": data.get("name", ""),
                        "email": data.get("email", "")
                    }
                    print(f"Processed queued create user: {user_id}")
                
                # Add other operations as needed
                
        except Exception as e:
            print(f"Error processing pending messages: {e}")
    
    def GetUser(self, request, context):
        user_id = request.user_id
        if user_id not in users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with ID {user_id} not found")
            return UserResponse()
        
        user = users[user_id]
        return UserResponse(
            user_id=user["user_id"],
            name=user["name"],
            email=user["email"]
        )
    
    def CreateUser(self, request, context):
        try:
            user_id = str(uuid.uuid4())
            user = {
                "user_id": user_id,
                "name": request.name,
                "email": request.email
            }
            users[user_id] = user
            
            # Also queue the operation for fault tolerance
            self.queue_operation("create_user", {
                "user_id": user_id,
                "name": request.name,
                "email": request.email
            })
            
            return UserResponse(
                user_id=user_id,
                name=request.name,
                email=request.email
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating user: {str(e)}")
            return UserResponse()
    
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

def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"User service started on port {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
