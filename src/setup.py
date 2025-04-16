# setup.py
import os
import sys
import subprocess

def install_dependencies():
    """Install all required dependencies"""
    print("Installing required packages...")
    
    requirements = [
        "grpcio",
        "grpcio-tools",
        "flask",
        "requests"
    ]
    
    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("All dependencies installed successfully!")

def create_project_structure():
    """Create the project directory structure"""
    print("Creating project structure...")
    
    # Create directory for message queues
    os.makedirs("queues", exist_ok=True)
    
    # Create the main project files
    files = {
        "calculator.proto": open("calculator.proto", "w") if not os.path.exists("calculator.proto") else None,
        "generate_proto.py": open("generate_proto.py", "w") if not os.path.exists("generate_proto.py") else None,
        "mom_implementation.py": open("mom_implementation.py", "w") if not os.path.exists("mom_implementation.py") else None,
        "microservice_implementation.py": open("microservice_implementation.py", "w") if not os.path.exists("microservice_implementation.py") else None,
        "api_gateway.py": open("api_gateway.py", "w") if not os.path.exists("api_gateway.py") else None,
        "client.py": open("client.py", "w") if not os.path.exists("client.py") else None,
        "addition_service.py": open("addition_service.py", "w") if not os.path.exists("addition_service.py") else None,
        "subtraction_service.py": open("subtraction_service.py", "w") if not os.path.exists("subtraction_service.py") else None,
        "multiplication_service.py": open("multiplication_service.py", "w") if not os.path.exists("multiplication_service.py") else None,
        "division_service.py": open("division_service.py", "w") if not os.path.exists("division_service.py") else None
    }
    
    # Close any open file handles
    for f in files.values():
        if f is not None:
            f.close()
    
    print("Project structure created successfully!")

def setup():
    """Run the full setup process"""
    print("Setting up the distributed calculator system...")
    
    install_dependencies()
    create_project_structure()
    
    # Import and run the proto generator
    from generate_proto import generate_proto
    generate_proto()
    
    print("\nSetup completed successfully!")
    print("\nTo start the system, run the following commands in separate terminals:")
    print("1. python addition_service.py")
    print("2. python subtraction_service.py")
    print("3. python multiplication_service.py")
    print("4. python division_service.py")
    print("5. python api_gateway.py")
    print("6. python client.py")

if __name__ == "__main__":
    setup()