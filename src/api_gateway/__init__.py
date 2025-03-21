# client/client.py
import requests
import json
import argparse
import sys
import time

class ApiClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        
    def health_check(self):
        """Check the health of all services"""
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking health: {e}")
            return None
    
    def create_user(self, name, email):
        """Create a new user"""
        url = f"{self.base_url}/users"
        data = {
            "name": name,
            "email": email
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user(self, user_id):
        """Get user details"""
        url = f"{self.base_url}/users/{user_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting user: {e}")
            return None
    
    def create_product(self, name, price, description):
        """Create a new product"""
        url = f"{self.base_url}/products"
        data = {
            "name": name,
            "price": float(price),
            "description": description
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating product: {e}")
            return None
    
    def get_product(self, product_id):
        """Get product details"""
        url = f"{self.base_url}/products/{product_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting product: {e}")
            return None
    
    def create_order(self, user_id, product_ids):
        """Create a new order"""
        url = f"{self.base_url}/orders"
        data = {
            "user_id": user_id,
            "product_ids": product_ids
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating order: {e}")
            return None
    
    def get_order(self, order_id):
        """Get order details"""
        url = f"{self.base_url}/orders/{order_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting order: {e}")
            return None

def interactive_mode(client):
    """Run the client in interactive mode"""
    print("*" * 50)
    print("* Distributed System Client - Interactive Mode *")
    print("*" * 50)
    
    while True:
        print("\nAvailable commands:")
        print("1. Health Check")
        print("2. Create User")
        print("3. Get User")
        print("4. Create Product")
        print("5. Get Product")
        print("6. Create Order")
        print("7. Get Order")
        print("0. Exit")
        
        choice = input("\nEnter command number: ")
        
        if choice == "0":
            print("Exiting...")
            break
        elif choice == "1":
            health = client.health_check()
            if health:
                print("\nSystem Health:")
                for service, status in health.items():
                    print(f"  {service}: {status}")
        elif choice == "2":
            name = input("Enter user name: ")
            email = input("Enter user email: ")
            result = client.create_user(name, email)
            if result:
                print("\nUser created successfully:")
                print(json.dumps(result, indent=2))
        elif choice == "3":
            user_id = input("Enter user ID: ")
            result = client.get_user(user_id)
            if result:
                print("\nUser details:")
                print(json.dumps(result, indent=2))
        elif choice == "4":
            name = input("Enter product name: ")
            price = input("Enter product price: ")
            description = input("Enter product description: ")
            result = client.create_product(name, float(price), description)
            if result:
                print("\nProduct created successfully:")
                print(json.dumps(result, indent=2))
        elif choice == "5":
            product_id = input("Enter product ID: ")
            result = client.get_product(product_id)
            if result:
                print("\nProduct details:")
                print(json.dumps(result, indent=2))
        elif choice == "6":
            user_id = input("Enter user ID: ")
            products_input = input("Enter product IDs (comma separated): ")
            product_ids = [p.strip() for p in products_input.split(",")]
            result = client.create_order(user_id, product_ids)
            if result:
                print("\nOrder created successfully:")
                print(json.dumps(result, indent=2))
        elif choice == "7":
            order_id = input("Enter order ID: ")
            result = client.get_order(order_id)
            if result:
                print("\nOrder details:")
                print(json.dumps(result, indent=2))
        else:
            print("Invalid command!")

def demo_mode(client):
    """Run a demonstration of the system capabilities"""
    print("*" * 50)
    print("* Distributed System Demo *")
    print("*" * 50)
    
    print("\nChecking system health...")
    health = client.health_check()
    if health:
        print("System Health:")
        for service, status in health.items():
            print(f"  {service}: {status}")
    else:
        print("Health check failed. Exiting demo.")
        return
    
    print("\nCreating test user...")
    user = client.create_user("Test User", "test@example.com")
    if not user:
        print("Failed to create user. Exiting demo.")
        return
    print(f"User created with ID: {user['user_id']}")
    
    print("\nCreating test products...")
    product1 = client.create_product("Product 1", 19.99, "This is the first test product")
    product2 = client.create_product("Product 2", 29.99, "This is the second test product")
    if not product1 or not product2:
        print("Failed to create products. Exiting demo.")
        return
    print(f"Products created with IDs: {product1['product_id']}, {product2['product_id']}")
    
    print("\nCreating test order...")
    order = client.create_order(user['user_id'], [product1['product_id'], product2['product_id']])
    if not order:
        print("Failed to create order. Exiting demo.")
        return
    print(f"Order created with ID: {order['order_id']}")
    
    print("\nRetrieving order details...")
    retrieved_order = client.get_order(order['order_id'])
    if retrieved_order:
        print("Order details:")
        print(json.dumps(retrieved_order, indent=2))
    
    print("\nDemo completed successfully!")

def main():
    parser = argparse.ArgumentParser(description="Distributed System Client")
    parser.add_argument("--url", default="http://localhost:8080", help="API Gateway URL")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    
    args = parser.parse_args()
    client = ApiClient(args.url)
    
    if args.demo:
        demo_mode(client)
    else:
        interactive_mode(client)

if __name__ == "__main__":
    main()

