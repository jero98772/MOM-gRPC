from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from .mom_service import message_queue

app = FastAPI(title="Message-Oriented Middleware API")

class MessageData(BaseModel):
    content: Dict[str, Any]

class MessageResponse(BaseModel):
    message_id: str

class QueueInfo(BaseModel):
    name: str
    size: int

@app.post("/queue/{queue_name}", response_model=MessageResponse)
async def send_message(queue_name: str, message: MessageData):
    """Send a message to a specific queue"""
    message_id = message_queue.enqueue(queue_name, message.content)
    return {"message_id": message_id}

@app.get("/queue/{queue_name}", response_model=Optional[Dict[str, Any]])
async def receive_message(queue_name: str):
    """Receive and remove a message from a specific queue"""
    message = message_queue.dequeue(queue_name)
    if message is None:
        raise HTTPException(status_code=404, detail="Queue empty or does not exist")
    return message

@app.get("/queue/{queue_name}/peek", response_model=Optional[Dict[str, Any]])
async def peek_message(queue_name: str):
    """View the next message in a specific queue without removing it"""
    message = message_queue.peek(queue_name)
    if message is None:
        raise HTTPException(status_code=404, detail="Queue empty or does not exist")
    return message

@app.get("/queues", response_model=List[QueueInfo])
async def list_queues():
    """List all queues and their sizes"""
    queues = message_queue.get_queues()
    result = []
    for queue_name in queues:
        result.append({
            "name": queue_name,
            "size": message_queue.queue_size(queue_name)
        })
    return result

@app.get("/queue/{queue_name}/size", response_model=int)
async def queue_size(queue_name: str):
    """Get the number of messages in a specific queue"""
    return message_queue.queue_size(queue_name)

def start():
    """Start the MOM API server"""
    uvicorn.run("mom.mom_api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()