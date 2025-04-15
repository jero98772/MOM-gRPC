# MOM-gRPC

Proyecto de comunicación entre procesos remotos con tolerancia a fallos utilizando gRPC, REST y un middleware orientado a mensajes o MOM.

Nuestro proyecto fue desarrollado para la materia Tópicos Especiales en Telemática en la Universidad EAFIT. Tiene como objetivo principal demostrar una arquitectura distribuida moderna con microservicios que utilizan REST y gRPC, integrados mediante un MOM para garantizar availability.

## Integrantes
- Victor Arango Sohm
- Laura Danniela Zárate Guerrero
- Felipe Uribe Correa

## Objetivos

### Objetivo General
Diseñar e implementar una aplicación distribuida con microservicios que integre:
- Cliente basado en REST
- Microservicios que se comuniquen mediante gRPC
- Middleware de mensajería con mecanismo de recuperación de fallos

### Objetivos Específicos
- Desarrollar un API Gateway que gestione las peticiones REST.
- Aplicar gRPC para la comunicación entre microservicios.
- Implementar un MOM que enrute solicitudes y administre tolerancia a fallos.
- Asegurar modularidad y escalabilidad con Docker.

## Tecnologías Utilizadas
- Python 3.10+
- Flask (API Gateway)
- gRPC + Protocol Buffers
- Docker & Docker Compose
- Librerías: grpcio, grpcio-tools, requests, protobuf

## Instalación y Ejecución
### Requisitos
- Docker
- Docker Compose

### Pasos
```bash
cd src
docker-compose up --build
```

## Uso del sistema
Para probrar se puede enviar una solicitud POST al API Gateway como esta:
```bash
curl -X POST http://localhost:8080/calculate \
     -H "Content-Type: application/json" \
     -d '{"operation": "multiplication", "operands": [8, 3]}'
```

