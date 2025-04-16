import json
import os
import threading
import time
from pathlib import Path

class MessageQueue:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.queue_dir = f"queues/{queue_name}"
        Path(self.queue_dir).mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        
    def enqueue(self, message):
        """Add a message to the queue"""
        with self.lock:
            # Generate unique message ID based on timestamp
            message_id = f"{time.time()}_{threading.get_ident()}"
            message_path = os.path.join(self.queue_dir, f"{message_id}.json")
            
            # Store message with metadata
            with open(message_path, 'w') as f:
                data = {
                    'id': message_id,
                    'timestamp': time.time(),
                    'content': message,
                    'status': 'pending'  # pending, processing, completed, failed
                }
                json.dump(data, f)
            
            return message_id
    
    def dequeue(self):
        """Get the next pending message from the queue"""
        with self.lock:
            pending_messages = []
            for filename in os.listdir(self.queue_dir):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.queue_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        message_data = json.load(f)
                        if message_data['status'] == 'pending':
                            pending_messages.append((message_data, file_path))
                except Exception as e:
                    print(f"Error reading message file {file_path}: {e}")
            
            if not pending_messages:
                return None
                
            # Sort by timestamp (oldest first)
            pending_messages.sort(key=lambda x: x[0]['timestamp'])
            message_data, file_path = pending_messages[0]
            
            # Mark as processing
            message_data['status'] = 'processing'
            with open(file_path, 'w') as f:
                json.dump(message_data, f)
                
            return message_data
    
    def mark_completed(self, message_id, result=None):
        """Mark a message as completed"""
        self._update_message_status(message_id, 'completed', result)
    
    def mark_failed(self, message_id, error=None):
        """Mark a message as failed"""
        self._update_message_status(message_id, 'failed', error)
    
    def _update_message_status(self, message_id, status, result=None):
        """Update message status and optionally add result data"""
        with self.lock:
            for filename in os.listdir(self.queue_dir):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.queue_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        message_data = json.load(f)
                        
                    if message_data['id'] == message_id:
                        message_data['status'] = status
                        if result is not None:
                            message_data['result'] = result
                            
                        with open(file_path, 'w') as f:
                            json.dump(message_data, f)
                        return True
                except Exception as e:
                    print(f"Error updating message {file_path}: {e}")
            
            return False
    
    def get_pending_operations(self):
        """Get all pending operations (for recovery)"""
        pending = []
        for filename in os.listdir(self.queue_dir):
            if not filename.endswith('.json'):
                continue
                
            file_path = os.path.join(self.queue_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    message_data = json.load(f)
                    if message_data['status'] in ['pending', 'processing']:
                        pending.append(message_data)
            except Exception as e:
                print(f"Error reading message file {file_path}: {e}")
        
        return pending
    
    def cleanup_old_messages(self, max_age_hours=24):
        """Cleanup completed messages older than max_age_hours"""
        with self.lock:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.queue_dir):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.queue_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        message_data = json.load(f)
                        
                    # Remove completed or failed messages that are old
                    if message_data['status'] in ['completed', 'failed']:
                        age = current_time - message_data['timestamp']
                        if age > max_age_seconds:
                            os.remove(file_path)
                except Exception as e:
                    print(f"Error cleaning up message {file_path}: {e}")


class MessageBroker:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageBroker, cls).__new__(cls)
            cls._instance.queues = {}
        return cls._instance
    
    def get_queue(self, queue_name):
        """Get or create a queue with the given name"""
        if queue_name not in self.queues:
            self.queues[queue_name] = MessageQueue(queue_name)
        return self.queues[queue_name]
    
    def periodic_cleanup(self):
        """Periodically clean up old messages"""
        while True:
            for queue in self.queues.values():
                queue.cleanup_old_messages()
            time.sleep(3600)  # Run every hour