# run_all.py
import os
import sys
import time
import subprocess
import signal
import atexit
from client import run_manual_mode ,run_autotest_mode
processes = []

def start_service(script_name, *args):
    """Start a service in a new process with optional command-line arguments"""
    cmd = [sys.executable, script_name] + list(args)
    print(f"Starting {' '.join(cmd)}...")
    process = subprocess.Popen(cmd)
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
    print("\nStarting client...")
    option=input("""Press Enter to start client...\n
        do you prefere
        1) automatic testing
        2) manual testing
        please enter your choice[1/2]
    """)
    if option=="1":
        client_process = start_service("client.py", "--mode", "autotest")
    if option=="2" :
        client_process = start_service("client.py", "--mode", "manual")
    #client_process = start_service("client.py")

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