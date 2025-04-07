import requests
import json
import time
import sys

class CalculatorClient:
    """REST Client for Distributed Calculator"""
    
    def __init__(self, api_gateway_url="http://localhost:5000"):
        self.api_gateway_url = api_gateway_url
    
    def perform_operation(self, operation, a, b):
        """Perform a calculation operation"""
        if operation not in ['add', 'subtract', 'multiply', 'divide']:
            print(f"Error: Invalid operation '{operation}'")
            return None
        
        try:
            # Prepare request
            url = f"{self.api_gateway_url}/calculate/{operation}"
            payload = {'a': a, 'b': b}
            
            # Send request to API Gateway
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                # Immediate success
                result = response.json()
                return result
            elif response.status_code == 202:
                # Request queued - poll for result
                result = response.json()
                request_id = result['request_id']
                return self.poll_result(request_id)
            else:
                print(f"Error: {response.json().get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error performing operation: {e}")
            return None
    
    def poll_result(self, request_id, max_retries=30, interval=2):
        """Poll for result of queued operation"""
        print(f"Operation queued (ID: {request_id}). Polling for result...")
        
        for i in range(max_retries):
            try:
                url = f"{self.api_gateway_url}/status/{request_id}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result['status'] == 'completed':
                        print("Operation completed!")
                        return result
                    
                    print(f"Still waiting... (Attempt {i+1}/{max_retries})")
                
                # Wait before next poll
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error polling for result: {e}")
        
        print("Timed out waiting for result")
        return {'status': 'timeout', 'request_id': request_id}

def interactive_mode():
    """Run client in interactive mode"""
    client = CalculatorClient()
    
    print("Distributed Calculator Client")
    print("----------------------------")
    print("Available operations: add, subtract, multiply, divide")
    
    while True:
        try:
            print("\nEnter operation (or 'exit' to quit):")
            operation = input("> ").strip().lower()
            
            if operation == 'exit':
                break
                
            if operation not in ['add', 'subtract', 'multiply', 'divide']:
                print("Invalid operation. Try again.")
                continue
                
            a = float(input("Enter first number: "))
            b = float(input("Enter second number: "))
            
            print(f"\nPerforming: {a} {operation} {b}")
            result = client.perform_operation(operation, a, b)
            
            if result:
                if 'result' in result:
                    print(f"Result: {result['result']}")
                else:
                    print(f"Status: {result['status']}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except ValueError:
            print("Invalid number. Please enter numeric values.")
        except Exception as e:
            print(f"Error: {e}")

def command_line_mode():
    """Run client with command line arguments"""
    if len(sys.argv) < 4:
        print("Usage: python client.py <operation> <number1> <number2>")
        print("Example: python client.py add 5 3")
        return
        
    try:
        operation = sys.argv[1].lower()
        a = float(sys.argv[2])
        b = float(sys.argv[3])
        
        if operation not in ['add', 'subtract', 'multiply', 'divide']:
            print(f"Invalid operation: {operation}")
            print("Valid operations: add, subtract, multiply, divide")
            return
            
        client = CalculatorClient()
        result = client.perform_operation(operation, a, b)
        
        if result and 'result' in result:
            print(f"Result: {result['result']}")
        elif result:
            print(f"Status: {result['status']}")
            
    except ValueError:
        print("Error: Please provide valid numeric values.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check if running in command line mode or interactive mode
    if len(sys.argv) > 1:
        command_line_mode()
    else:
        interactive_mode()