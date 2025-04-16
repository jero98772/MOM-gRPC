# run_all.py
import os
import sys
import time
import subprocess
import signal
import atexit

processes = []

def start_service(script_name):
    """Start a service in a new process"""
    print(f"Starting {script_name}...")
    process = subprocess.Popen([sys.executable, script_name])
    processes.append((script_name, process))
    return process

def cleanup():
    """Terminate all running processes"""
    print("\nShutting down all services...")
    for name, process in processes:
        print(f"Terminating {name}...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"Killing {name} (did not terminate gracefully)")
            process.kill()
    print("All services shut down")

def main():
    # Register cleanup function
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))
    
    # Start all microservices
    start_service("addition_service.py")
    time.sleep(1)
    
    start_service("subtraction_service.py")
    time.sleep(1)
    
    start_service("multiplication_service.py")
    time.sleep(1)
    
    start_service("division_service.py")
    time.sleep(1)
    
    # Start API gateway
    start_service("api_gateway.py")
    time.sleep(3)
    
    # Start client for testing
    client_process = start_service("client.py")
    client_process.wait()  # Wait for client to complete
    
    # Keep running until user terminates
    print("\nAll services are running. Press Ctrl+C to terminate all.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()