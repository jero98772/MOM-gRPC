from flask import Flask, request, jsonify
import threading
import time
import json
import os
from datetime import datetime

app = Flask(__name__)

# In-memory message queues and results storage
message_queues = {
    'add': [],
    'subtract': [],
    'multiply': [],
    'divide': []
}

# Results storage for completed operations
results = {}

# Lock for thread safety
queue_lock = threading.Lock()
results_lock = threading.Lock()

@app.route('/queue', methods=['POST'])
def queue_message():
    """Queue a message for processing"""
    data = request.get_json()
    
    if not data or 'operation' not in data or 'a' not in data or 'b' not in data or 'request_id' not in data:
        return jsonify({'error': 'Invalid message format'}), 400
    
    operation = data['operation']
    if operation not in message_queues:
        return jsonify({'error': f'Unknown operation: {operation}'}), 400
    
    with queue_lock:
        # Add message to appropriate queue
        message_queues[operation].append({
            'operation': operation,
            'a': data['a'],
            'b': data['b'],
            'request_id': data['request_id'],
            'timestamp': datetime.now().isoformat()
        })
    
    return jsonify({'status': 'queued', 'request_id': data['request_id']}), 201

@app.route('/messages/<operation>', methods=['GET'])
def get_messages(operation):
    """Get queued messages for a specific operation"""
    if operation not in message_queues:
        return jsonify({'error': f'Unknown operation: {operation}'}), 400
    
    with queue_lock:
        # Get messages and clear queue
        messages = message_queues[operation].copy()
        message_queues[operation] = []
    
    return jsonify(messages), 200

@app.route('/complete', methods=['POST'])
def complete_message():
    """Mark a queued message as completed"""
    data = request.get_json()
    
    if not data or 'request_id' not in data:
        return jsonify({'error': 'Invalid completion data'}), 400
    
    request_id = data['request_id']
    
    with results_lock:
        # Store the result
        results[request_id] = {
            'result': data.get('result', 0),
            'status': data.get('status', 'success'),
            'completed_at': datetime.now().isoformat()
        }
    
    return jsonify({'status': 'completed', 'request_id': request_id}), 200

@app.route('/status/<request_id>', methods=['GET'])
def get_status(request_id):
    """Get status of a request"""
    # Check if result is available
    with results_lock:
        if request_id in results:
            return jsonify({
                'status': 'completed',
                'result': results[request_id]['result'],
                'completed_at': results[request_id]['completed_at']
            }), 200
    
    # Check if message is in any queue
    with queue_lock:
        for operation, queue in message_queues.items():
            for message in queue:
                if message['request_id'] == request_id:
                    return jsonify({
                        'status': 'queued',
                        'operation': operation,
                        'queued_at': message['timestamp']
                    }), 200
    
    return jsonify({'status': 'not_found', 'request_id': request_id}), 404

# Purge old results periodically
def purge_old_results():
    """Clean up old results to prevent memory issues"""
    while True:
        time.sleep(3600)  # Run every hour
        
        current_time = datetime.now()
        keys_to_remove = []
        
        with results_lock:
            for request_id, result in results.items():
                # Parse completed_at timestamp
                completed_at = datetime.fromisoformat(result['completed_at'])
                
                # If older than 24 hours, mark for removal
                if (current_time - completed_at).total_seconds() > 86400:
                    keys_to_remove.append(request_id)
            
            # Remove old results
            for key in keys_to_remove:
                results.pop(key, None)

if __name__ == '__main__':
    # Start background purge thread
    purge_thread = threading.Thread(target=purge_old_results, daemon=True)
    purge_thread.start()
    
    # Start Flask application
    app.run(host='0.0.0.0', port=5001, debug=True)