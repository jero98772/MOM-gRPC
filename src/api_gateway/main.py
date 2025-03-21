# api_gateway/main.py
import grpc
import uvicorn
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys

# Add the microservices directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(parent_dir, "microservices"))

# Import the generated gRPC stubs
from common.protos.service1_pb2 import UserRequest, CreateUserRequest
from common.protos.service1_pb2_grpc import UserServiceStub
from common.protos.service2_pb2 import ProductRequest, CreateProductRequest
from common.protos.service2_pb2_grpc import ProductServiceStub
from common.protos.service3_pb2 import OrderRequest, CreateOrderRequest
from common.protos.service3_pb2_grpc import OrderServiceStub

app = FastAPI(title="API Gateway")

# Define service addresses (could be loaded from environment variables)
USER_SERVICE_ADDR = "localhost:50051"
PRODUCT_SERVICE_ADDR = "localhost:50052"
ORDER_SERVICE_ADDR = "localhost:50053"
MOM_SERVICE_URL = "http://localhost:8000"

# Create gRPC channel connections
user_channel = grpc.insecure_channel(USER_SERVICE_ADDR)
user_stub = UserServiceStub(user_channel)

product_channel = grpc.insecure_channel(PRODUCT_SERVICE_ADDR)
product_stub = ProductServiceStub(product_channel)

order_channel = grpc.insecure_channel(ORDER_SERVICE_ADDR)
order_stub = OrderServiceStub(order_channel)

# Pydantic models for API validation
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str

class ProductCreate(BaseModel):
    name: str
    price: float
    description: str

class ProductResponse(BaseModel):
    product_id: str
    name: str
    price: float
    description: str

class OrderCreate(BaseModel):
    user_id: str
    product_ids: List[str]

class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    product_ids: List[str]
    total_price: float
    status: str

# API endpoints for User service
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    try:
        grpc_request = CreateUserRequest(name=user.name, email=user.email)
        response = user_stub.CreateUser(grpc_request)
        return {
            "user_id": response.user_id,
            "name": response.name,
            "email": response.email
        }
    except grpc.RpcError as e:
        # In case of service failure, try to queue the request via MOM
        try:
            message = {
                "operation": "create_user",
                "data": {
                    "name": user.name,
                    "email": user.email
                }
            }
            mom_response = requests.post(
                f"{MOM_SERVICE_URL}/queue/user_service_queue",
                json={"content": message}
            )
            if mom_response.status_code == 200:
                # Return a provisional response
                return {
                    "user_id": "pending",
                    "name": user.name,
                    "email": user.email
                }
        except Exception as mom_error:
            # If MOM is also down, we have no choice but to fail
            pass
            
        # Propagate the original error if MOM fallback failed
        raise HTTPException(status_code=503, detail=f"User service unavailable: {e.details()}")

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    try:
        grpc_request = UserRequest(user_id=user_id)
        response = user_stub.GetUser(grpc_request)
        return {
            "user_id": response.user_id,
            "name": response.name,
            "email": response.email
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        raise HTTPException(status_code=503, detail=f"User service unavailable: {e.details()}")

# API endpoints for Product service
@app.post("/products", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    try:
        grpc_request = CreateProductRequest(
            name=product.name,
            price=product.price,
            description=product.description
        )
        response = product_stub.CreateProduct(grpc_request)
        return {
            "product_id": response.product_id,
            "name": response.name,
            "price": response.price,
            "description": response.description
        }
    except grpc.RpcError as e:
        # In case of service failure, try to queue the request via MOM
        try:
            message = {
                "operation": "create_product",
                "data": {
                    "name": product.name,
                    "price": product.price,
                    "description": product.description
                }
            }
            mom_response = requests.post(
                f"{MOM_SERVICE_URL}/queue/product_service_queue",
                json={"content": message}
            )
            if mom_response.status_code == 200:
                # Return a provisional response
                return {
                    "product_id": "pending",
                    "name": product.name,
                    "price": product.price,
                    "description": product.description
                }
        except Exception as mom_error:
            # If MOM is also down, we have no choice but to fail
            pass
            
        # Propagate the original error if MOM fallback failed
        raise HTTPException(status_code=503, detail=f"Product service unavailable: {e.details()}")

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    try:
        grpc_request = ProductRequest(product_id=product_id)
        response = product_stub.GetProduct(grpc_request)
        return {
            "product_id": response.product_id,
            "name": response.name,
            "price": response.price,
            "description": response.description
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        raise HTTPException(status_code=503, detail=f"Product service unavailable: {e.details()}")

# API endpoints for Order service
@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    try:
        grpc_request = CreateOrderRequest(
            user_id=order.user_id,
            product_ids=order.product_ids
        )
        response = order_stub.CreateOrder(grpc_request)
        return {
            "order_id": response.order_id,
            "user_id": response.user_id,
            "product_ids": list(response.product_ids),
            "total_price": response.total_price,
            "status": response.status
        }
    except grpc.RpcError as e:
        # In case of service failure, try to queue the request via MOM
        try:
            message = {
                "operation": "create_order",
                "data": {
                    "user_id": order.user_id,
                    "product_ids": order.product_ids
                }
            }
            mom_response = requests.post(
                f"{MOM_SERVICE_URL}/queue/order_service_queue",
                json={"content": message}
            )
            if mom_response.status_code == 200:
                # Return a provisional response
                return {
                    "order_id": "pending",
                    "user_id": order.user_id,
                    "product_ids": order.product_ids,
                    "total_price": 0.0,
                    "status": "queued"
                }
        except Exception as mom_error:
            # If MOM is also down, we have no choice but to fail
            pass
            
        # Propagate the original error if MOM fallback failed
        raise HTTPException(status_code=503, detail=f"Order service unavailable: {e.details()}")

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    try:
        grpc_request = OrderRequest(order_id=order_id)
        response = order_stub.GetOrder(grpc_request)
        return {
            "order_id": response.order_id,
            "user_id": response.user_id,
            "product_ids": list(response.product_ids),
            "total_price": response.total_price,
            "status": response.status
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
        raise HTTPException(status_code=503, detail=f"Order service unavailable: {e.details()}")

# API endpoints for system status
@app.get("/health")
async def health_check():
    status = {
        "api_gateway": "healthy",
        "mom_service": "unknown",
        "user_service": "unknown",
        "product_service": "unknown",
        "order_service": "unknown"
    }
    
    # Check MOM service
    try:
        mom_response = requests.get(f"{MOM_SERVICE_URL}/queues")
        if mom_response.status_code == 200:
            status["mom_service"] = "healthy"
        else:
            status["mom_service"] = "unhealthy"
    except Exception:
        status["mom_service"] = "unavailable"
    
    # Check User service
    try:
        user_stub.GetUser(UserRequest(user_id="health-check"))
        status["user_service"] = "healthy"
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status["user_service"] = "healthy"
        else:
            status["user_service"] = "unhealthy"
    except Exception:
        status["user_service"] = "unavailable"
    
    # Check Product service
    try:
        product_stub.GetProduct(ProductRequest(product_id="health-check"))
        status["product_service"] = "healthy"
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status["product_service"] = "healthy"
        else:
            status["product_service"] = "unhealthy"
    except Exception:
        status["product_service"] = "unavailable"
    
    # Check Order service
    try:
        order_stub.GetOrder(OrderRequest(order_id="health-check"))
        status["order_service"] = "healthy"
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status["order_service"] = "healthy"
        else:
            status["order_service"] = "unhealthy"
    except Exception:
        status["order_service"] = "unavailable"
    
    return status

def start():
    """Start the API Gateway server"""
    uvicorn.run("api_gateway.main:app", host="0.0.0.0", port=8080, reload=True)

if __name__ == "__main__":
    start()
