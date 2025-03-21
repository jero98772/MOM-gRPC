import os
import json
import time
import threading
from collections import defaultdict, deque
import uuid

class MessageQueue:
    def __init__(self):
        self.queues = defaultdict(deque)
        self.lock = threading.Lock()
        
        # Directory to persist messages in case of failure
        self.persistence_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'persistence')
        os.makedirs(self.persistence_dir, exist_ok=True)
        
        # Load any persisted messages
        self._load_persisted_messages()
        
    def _get_persistence_file(self, queue_name):
        return os.path.join(self.persistence_dir, f"{queue_name}.json")
        
    def _persist_queue(self, queue_name):
        """Persist queue to disk for fault tolerance"""
        file_path = self._get_persistence_file(queue_name)
        with open(file_path, 'w') as f:
            json.dump(list(self.queues[queue_name]), f)
            
    def _load_persisted_messages(self):
        """Load persisted messages from disk"""
        for filename in os.listdir(self.persistence_dir):
            if filename.endswith('.json'):
                queue_name = filename[:-5]  # Remove .json extension
                file_path = os.path.join(self.persistence_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        messages = json.load(f)
                        self.queues[queue_name] = deque(messages)
                except Exception as e:
                    print(f"Error loading persisted messages for queue {queue_name}: {e}")
    
    def enqueue(self, queue_name, message):
        """Add a message to the specified queue"""
        with self.lock:
            # Generate a message ID for tracking
            if 'message_id' not in message:
                message['message_id'] = str(uuid.uuid4())
            
            # Add timestamp for processing order
            if 'timestamp' not in message:
                message['timestamp'] = time.time()
                
            self.queues[queue_name].append(message)
            self._persist_queue(queue_name)
            return message['message_id']
    
    def dequeue(self, queue_name):
        """Remove and return a message from the specified queue"""
        with self.lock:
            if not self.queues[queue_name]:
                return None
            
            message = self.queues[queue_name].popleft()
            self._persist_queue(queue_name)
            return message
    
    def peek(self, queue_name):
        """Return but don't remove a message from the specified queue"""
        with self.lock:
            if not self.queues[queue_name]:
                return None
            
            return self.queues[queue_name][0]
    
    def queue_size(self, queue_name):
        """Return the number of messages in the queue"""
        with self.lock:
            return len(self.queues[queue_name])
    
    def get_queues(self):
        """Return a list of all queue names"""
        with self.lock:
            return list(self.queues.keys())

# Create a global message queue instance
message_queue = MessageQueue()

