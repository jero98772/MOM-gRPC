# Common base implementation for all calculator microservices
import os
import sys
import time
import threading
import grpc
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc
from mom_implementation import MessageBroker

class CalculatorServiceBase:
    def __init__(self, service_name, port):
        self.service_name = service_name
        self.port = port
        self.message_queue = MessageBroker().get_queue(service_name)
        
    def start_server(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.add_service_to_server(self.server)
        self.server.add_insecure_port(f'[::]:{self.port}')
        self.server.start()
        print(f"{self.service_name} service running on port {self.port}")
        
        # Start recovery thread to process any pending operations
        recovery_thread = threading.Thread(target=self.recovery_process)
        recovery_thread.daemon = True
        recovery_thread.start()
        
        try:
            self.server.wait_for_termination()
        except KeyboardInterrupt:
            self.server.stop(0)
            
    def recovery_process(self):
        """Process any pending operations from previous runs"""
        print(f"Starting recovery process for {self.service_name}...")
        pending_operations = self.message_queue.get_pending_operations()
        
        if pending_operations:
            print(f"Found {len(pending_operations)} pending operations to recover")
            for op in pending_operations:
                try:
                    content = op['content']
                    result = self.perform_operation(content['num1'], content['num2'])
                    self.message_queue.mark_completed(op['id'], result)
                    print(f"Recovered operation {op['id']} with result {result}")
                except Exception as e:
                    self.message_queue.mark_failed(op['id'], str(e))
                    print(f"Failed to recover operation {op['id']}: {e}")
        else:
            print("No pending operations found")
            
    def add_service_to_server(self, server):
        """To be implemented by subclasses"""
        raise NotImplementedError()
        
    def perform_operation(self, num1, num2):
        """To be implemented by subclasses"""
        raise NotImplementedError()


# Addition Microservice
class AdditionService(calculator_pb2_grpc.CalculatorServicer):
    def __init__(self):
        self.message_queue = MessageBroker().get_queue("addition")
        
    def Add(self, request, context):
        operation_id = request.operation_id
        try:
            # Enqueue the request for failover support
            message_id = self.message_queue.enqueue({
                'num1': request.num1,
                'num2': request.num2,
                'operation': 'add',
                'operation_id': operation_id
            })
            
            # Perform the calculation
            result = request.num1 + request.num2
            
            # Mark operation as completed
            self.message_queue.mark_completed(message_id, result)
            
            return calculator_pb2.CalculationResponse(
                result=result,
                operation_id=operation_id,
                success=True
            )
        except Exception as e:
            # Mark operation as failed
            if 'message_id' in locals():
                self.message_queue.mark_failed(message_id, str(e))
            return calculator_pb2.CalculationResponse(
                result=0,
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
    
    def perform_operation(self, num1, num2):
        return num1 + num2


# Subtraction Microservice
class SubtractionService(calculator_pb2_grpc.CalculatorServicer):
    def __init__(self):
        self.message_queue = MessageBroker().get_queue("subtraction")
        
    def Subtract(self, request, context):
        operation_id = request.operation_id
        try:
            # Enqueue the request for failover support
            message_id = self.message_queue.enqueue({
                'num1': request.num1,
                'num2': request.num2,
                'operation': 'subtract',
                'operation_id': operation_id
            })
            
            # Perform the calculation
            result = request.num1 - request.num2
            
            # Mark operation as completed
            self.message_queue.mark_completed(message_id, result)
            
            return calculator_pb2.CalculationResponse(
                result=result,
                operation_id=operation_id,
                success=True
            )
        except Exception as e:
            # Mark operation as failed
            if 'message_id' in locals():
                self.message_queue.mark_failed(message_id, str(e))
            return calculator_pb2.CalculationResponse(
                result=0,
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
    
    def perform_operation(self, num1, num2):
        return num1 - num2


# Multiplication Microservice
class MultiplicationService(calculator_pb2_grpc.CalculatorServicer):
    def __init__(self):
        self.message_queue = MessageBroker().get_queue("multiplication")
        
    def Multiply(self, request, context):
        operation_id = request.operation_id
        try:
            # Enqueue the request for failover support
            message_id = self.message_queue.enqueue({
                'num1': request.num1,
                'num2': request.num2,
                'operation': 'multiply',
                'operation_id': operation_id
            })
            
            # Perform the calculation
            result = request.num1 * request.num2
            
            # Mark operation as completed
            self.message_queue.mark_completed(message_id, result)
            
            return calculator_pb2.CalculationResponse(
                result=result,
                operation_id=operation_id,
                success=True
            )
        except Exception as e:
            # Mark operation as failed
            if 'message_id' in locals():
                self.message_queue.mark_failed(message_id, str(e))
            return calculator_pb2.CalculationResponse(
                result=0,
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
    
    def perform_operation(self, num1, num2):
        return num1 * num2


# Division Microservice
class DivisionService(calculator_pb2_grpc.CalculatorServicer):
    def __init__(self):
        self.message_queue = MessageBroker().get_queue("division")
        
    def Divide(self, request, context):
        operation_id = request.operation_id
        try:
            # Check for division by zero
            if request.num2 == 0:
                raise ValueError("Division by zero is not allowed")
                
            # Enqueue the request for failover support
            message_id = self.message_queue.enqueue({
                'num1': request.num1,
                'num2': request.num2,
                'operation': 'divide',
                'operation_id': operation_id
            })
            
            # Perform the calculation
            result = request.num1 / request.num2
            
            # Mark operation as completed
            self.message_queue.mark_completed(message_id, result)
            
            return calculator_pb2.CalculationResponse(
                result=result,
                operation_id=operation_id,
                success=True
            )
        except Exception as e:
            # Mark operation as failed
            if 'message_id' in locals():
                self.message_queue.mark_failed(message_id, str(e))
            return calculator_pb2.CalculationResponse(
                result=0,
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
    
    def perform_operation(self, num1, num2):
        if num2 == 0:
            raise ValueError("Division by zero is not allowed")
        return num1 / num2


# Server implementations for each microservice
def run_addition_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        AdditionService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Addition service running on port 50051")
    
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)


def run_subtraction_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        SubtractionService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Subtraction service running on port 50052")
    
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)


def run_multiplication_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        MultiplicationService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    print("Multiplication service running on port 50053")
    
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)


def run_division_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        DivisionService(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    print("Division service running on port 50054")
    
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)