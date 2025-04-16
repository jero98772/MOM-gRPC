import requests
import json
import time
import uuid
import argparse

class CalculatorClient:
    def __init__(self, gateway_url="http://localhost:5000"):
        self.gateway_url = gateway_url
        
    def calculate(self, operation, num1, num2):
        """Send a calculation request to the API Gateway"""
        payload = {
            "operation": operation,
            "num1": num1,
            "num2": num2
        }
        
        try:
            response = requests.post(
                f"{self.gateway_url}/calculate", 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 503:
                # Service unavailable, request was queued
                result = response.json()
                print(f"Operation queued: {result}")
                
                # Poll for status if an operation_id was provided
                if 'operation_id' in result:
                    return self.poll_operation_status(result['operation_id'])
                else:
                    return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return response.json()
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"error": str(e)}
    
    def poll_operation_status(self, operation_id, max_polls=10, poll_interval=2):
        """Poll for the status of a queued operation"""
        print(f"Polling for operation {operation_id}...")
        
        for i in range(max_polls):
            try:
                response = requests.get(
                    f"{self.gateway_url}/operation/{operation_id}"
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'completed':
                        print(f"Operation completed: {result}")
                        return result
                    print(f"Operation status: {result.get('status')}. Waiting...")
                else:
                    print(f"Error checking status: {response.status_code} - {response.text}")
                    
                # Wait before polling again
                time.sleep(poll_interval)
                
            except requests.exceptions.RequestException as e:
                print(f"Status check failed: {e}")
        
        return {"error": f"Operation timed out after {max_polls * poll_interval} seconds"}
    
    def health_check(self):
        """Check the health of the API Gateway and services"""
        try:
            # Check API Gateway health
            gateway_response = requests.get(f"{self.gateway_url}/health")
            
            # Check services health
            services_response = requests.get(f"{self.gateway_url}/services/health")
            
            return {
                "gateway": gateway_response.json() if gateway_response.ok else {"error": gateway_response.text},
                "services": services_response.json() if services_response.ok else {"error": services_response.text}
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Health check failed: {str(e)}"}


def run_manual_mode(client):
    while True:
        print("\n=== Calculator Client Menu ===")
        print("1. Perform a calculation")
        print("2. Perform health check")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            print("\nAvailable operations: add, subtract, multiply, divide")
            operation = input("Enter operation: ").strip().lower()
            if operation not in {"add", "subtract", "multiply", "divide"}:
                print("Invalid operation. Please try again.")
                continue

            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))
            except ValueError:
                print("Invalid input. Please enter numeric values.")
                continue

            result = client.calculate(operation, num1, num2)
            print("Result:")
            print(json.dumps(result, indent=2))

        elif choice == "2":
            print("\nPerforming health check...")
            health = client.health_check()
            print(json.dumps(health, indent=2))

        elif choice == "3":
            print("Exiting the client. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def run_autotest_mode(client):
    print("Performing health check...")
    health = client.health_check()
    print(json.dumps(health, indent=2))

    operations = [
        {"operation": "add", "num1": 10, "num2": 5},
        {"operation": "subtract", "num1": 10, "num2": 5},
        {"operation": "multiply", "num1": 10, "num2": 5},
        {"operation": "divide", "num1": 10, "num2": 5},
        {"operation": "divide", "num1": 10, "num2": 0}
    ]

    for op in operations:
        print(f"\nTesting: {op['num1']} {op['operation']} {op['num2']}")
        result = client.calculate(op['operation'], op['num1'], op['num2'])
        print(json.dumps(result, indent=2))
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Calculator Client for MOM-gRPC System")
    parser.add_argument(
        "--mode",
        choices=["manual", "autotest"],
        required=True,
        help="Choose 'manual' for interactive mode or 'autotest' to run predefined tests"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:5000",
        help="Base URL of the API Gateway (default: http://localhost:5000)"
    )

    args = parser.parse_args()
    client = CalculatorClient(gateway_url=args.url)

    if args.mode == "manual":
        run_manual_mode(client)
    elif args.mode == "autotest":
        run_autotest_mode(client)


if __name__ == "__main__":
    main()

