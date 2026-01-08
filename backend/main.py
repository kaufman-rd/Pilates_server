from flask import request, jsonify
from config import app, socketio
from flask_socketio import emit
import random
import time
import math

import acs_SPI as acs



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


def bg_task():
    sample_counter = 0
    
    while True:

        signal = acs.acs.position
        
        sensor_data = {
            'value': round(signal, 4),
            'timestamp': time.time()
        }
        sample_counter += 1
        
        socketio.emit('message', sensor_data)
        logger.info(f"Emitted sensor data: {sensor_data}")
        socketio.sleep(1)  # Send data every 1 second for smooth animation

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    # emit('message', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('message')
def handle_message(data):
    logger.info(f'Received message: {data}')
    # emit('message', {'data': f'Echo: {data}'})

if __name__ == '__main__':
    acs.acs.start()
    socketio.start_background_task(bg_task)
    socketio.run(app, debug=True, use_reloader=False, port=8000)