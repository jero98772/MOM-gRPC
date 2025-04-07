FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# (We'll handle the proto files in Docker Compose instead)

EXPOSE 50053

CMD ["python", "service.py"]