Sure! Here's the English translation of your document:

---

# MOM-gRPC

Project for remote process communication with fault tolerance using gRPC, REST, and a message-oriented middleware (MOM).

Our project was developed for the course *Special Topics in Telematics* at Universidad EAFIT. Its main objective is to demonstrate a modern distributed architecture with microservices that use REST and gRPC, integrated through a MOM to ensure availability.

## Team Members
- Victor Arango S  
- Laura Danniela Zárate Guerrero  
- Felipe Uribe Correa

## Objectives

### General Objective
Design and implement a distributed application with microservices that integrates:
- REST-based client  
- Microservices communicating via gRPC  
- Messaging middleware with fault recovery mechanisms

### Specific Objectives
- Develop an API Gateway to manage REST requests  
- Apply gRPC for communication between microservices  
- Implement a MOM to route requests and manage fault tolerance  
- Ensure modularity and scalability with Docker  

## Technologies Used
- Python 3.10+  
- Flask (API Gateway)  
- gRPC + Protocol Buffers  
- Docker & Docker Compose  
- Libraries: `grpcio`, `grpcio-tools`, `requests`, `protobuf`

## Installation and Execution
### Requirements
- Docker  
- Docker Compose

### Steps
```bash
cd src
python setup.py

```

## System Usage
To test the system, you can send a POST request to the API Gateway like this:

	python run_all.py
