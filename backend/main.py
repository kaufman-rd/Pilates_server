from flask import request, jsonify
from config import app, socketio
from flask_socketio import emit
import random
import time
import math
import threading

# import acs_SPI as acs
import acs_pilates as acs



import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\t- %(message)s')

# create console handler and set level to debug, add formatter to ch
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(ch)


@app.route('/', methods=['GET'])
def hello():
    return jsonify(message="Hello, World!")

def manual_listener():
    while True:
        data = input("Enter a command")
        if not data:
            continue
        
        if data[0] == '#':
            acs.pilates.execute_command(data[1:])

        time.sleep(0.01)

def bg_task():
    sample_counter = 0
    
    while True:

        sensor_data = {
            'timestamp': time.time(),
            'position': f"{acs.pilates.position:.2f}",
            'velocity': f"{acs.pilates.velocity:.2f}",
            'weight': f"{acs.pilates.weight:.2f}",
            'total_weight': f"{acs.pilates.total_weight:.2f}",
            'rubber_coeff': f"{acs.pilates.rubber_coeff:.2f}",
            'pull_coeff': f"{acs.pilates.pull_coeff:.2f}",
            'push_coeff': f"{acs.pilates.push_coeff:.2f}",

        }
        
        socketio.emit('message', sensor_data)
        # logger.info(f"Emitted sensor data: {sensor_data}")
        socketio.sleep(0.05)  # Send data every 1 second for smooth animation

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    # emit('message', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('message')
def handle_message(data):
    try:
        logger.info(f'Received message: {data}')
        acs.pilates.execute_command(data)
        # emit('message', {'status': 'Command executed', 'command': data})
    except Exception as e:
        logger.error(f'Error executing command: {e}')
        # emit('message', {'status': 'Error', 'error': str(e)})

if __name__ == '__main__':
    acs.pilates.start()
    threading.Thread(target=manual_listener, daemon=True).start()
    socketio.start_background_task(bg_task)
    socketio.run(app, debug=True, use_reloader=False, port=8000)