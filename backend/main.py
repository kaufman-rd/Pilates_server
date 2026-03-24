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

connected_clients = 0


@app.route('/', methods=['GET'])
def hello():
    return jsonify(message="Hello, World!")

def manual_listener():
    while True:
        try:
            data = input("Enter a command")
            if not data:
                continue
            
            if data[0] == '#':
                acs.pilates.execute_command(data[1:])
        except (EOFError, KeyboardInterrupt):
            logger.info("Manual listener stopping")
            break
        except Exception as e:
            logger.error(f"Error in manual listener: {e}")

        time.sleep(0.01)

def bg_task():
    sample_counter = 0
    
    while True:

        sensor_data = {
            'timestamp': time.time(),
            'position': round(acs.pilates.position, 2),
            'velocity': round(acs.pilates.velocity, 2),
            'weight': round(acs.pilates.weight, 2),
            'total_weight': round(acs.pilates.total_weight, 2),
            'rubber_coeff': round(acs.pilates.rubber_coeff, 2),
            'pull_coeff': round(acs.pilates.pull_coeff, 2),
            'push_coeff': round(acs.pilates.push_coeff, 2),
            'connected_clients': connected_clients,

        }
        
        socketio.emit('message', sensor_data)
        # logger.info(f"Emitted sensor data: {sensor_data}")
        socketio.sleep(0.05)  # Send data every 20ms for smooth animation

@socketio.on('connect')
def handle_connect():
    global connected_clients
    connected_clients += 1
    logger.info(f'Client connected. Total clients: {connected_clients}')
    # emit('message', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    global connected_clients
    connected_clients -= 1
    logger.info(f'Client disconnected. Total clients: {connected_clients}')

@socketio.on('message')
def handle_message(data):
    try:
        logger.info(f'Received message: {data}')
        if data.startswith('INIT'):
            acs.pilates.execute_command("INIT=1")
        
        elif data.startswith('WEIGHT='):
            data_value = data.split('=')[1]
            data_value_float = float(data_value)
            if data_value_float < 0 or data_value_float > 40:
                raise ValueError("Weight value out of range (0-40)")
            acs.pilates.execute_command(f"WEIGHT={data_value_float}")
        
        elif data.startswith('RUBBER='):
            data_value = data.split('=')[1]
            data_value_float = float(data_value)
            if data_value_float < 0 or data_value_float > 100:
                raise ValueError("Rubber value out of range (0-100)")
            acs.pilates.execute_command(f"RUBBER={data_value_float}")

        elif data.startswith('PULL='):
            data_value = data.split('=')[1]
            data_value_float = float(data_value)
            if data_value_float < 0 or data_value_float > 100:
                raise ValueError("Pull value out of range (0-100)")
            acs.pilates.execute_command(f"PULL={data_value_float}")

        elif data.startswith('PUSH='):
            data_value = data.split('=')[1]
            data_value_float = float(data_value)
            if data_value_float < 0 or data_value_float > 100:
                raise ValueError("Push value out of range (0-100)")
            acs.pilates.execute_command(f"PUSH={data_value_float}")
        else:
            raise ValueError("Unknown command")
        # emit('message', {'status': 'Command executed', 'command': data})
    
    except Exception as e:
        logger.error(f'Error executing command: {e}')
        # emit('message', {'status': 'Error', 'error': str(e)})

if __name__ == '__main__':
    acs.pilates.start()
    threading.Thread(target=manual_listener, daemon=True).start()
    socketio.start_background_task(bg_task)
    # socketio.run(app, debug=True, use_reloader=False, port=8000)
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False, port=8000)

    # while True:
    #     time.sleep(1)