from flask import jsonify
from config import app, socketio
import time
import threading
import json
import os

# import acs_SPI as acs
import acs_pilates as acs
from pySerialWorker.pyserialworker import SerialWorker



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

SERIAL_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "serial_config.json")

DEFAULT_SERIAL_CONFIG = {
    "loadcells": {
        "port": "COM4",
        "baudrate": 115200
    },
    "resistance_surface": {
        "port": "COM5",
        "baudrate": 115200
    }
}


def load_serial_config():
    """Load serial port configuration from JSON, creating defaults if missing."""
    if not os.path.exists(SERIAL_CONFIG_PATH):
        logger.warning(f"Serial config not found, creating default at {SERIAL_CONFIG_PATH}")
        try:
            with open(SERIAL_CONFIG_PATH, "w") as f:
                json.dump(DEFAULT_SERIAL_CONFIG, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to write default serial config: {e}")
        return DEFAULT_SERIAL_CONFIG

    try:
        with open(SERIAL_CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read serial config, using defaults: {e}")
        return DEFAULT_SERIAL_CONFIG


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

def drain_rx(serialworker):
    """Return the last serial message available, or empty string if none."""
    last_msg = ""
    while True:
        msg = serialworker.get_data()
        if not msg:
            break
        last_msg = msg
    return last_msg

def bg_task():
    """Background task to read sensor data and broadcast to clients."""
    config = load_serial_config()
    loadcells_cfg = config.get("loadcells", DEFAULT_SERIAL_CONFIG["loadcells"])
    resistance_cfg = config.get("resistance_surface", DEFAULT_SERIAL_CONFIG["resistance_surface"])

    try:
        serialworker_loadCells = SerialWorker(True, False)
        serialworker_loadCells.set_terminators("\n", "\n")
        serialworker_loadCells.set_connection_params(loadcells_cfg["port"], loadcells_cfg["baudrate"])
        serialworker_loadCells.start()

        serialworker_resistanceSurface = SerialWorker(True, False)
        serialworker_resistanceSurface.set_terminators("\n", "\n")
        serialworker_resistanceSurface.set_connection_params(resistance_cfg["port"], resistance_cfg["baudrate"])
        serialworker_resistanceSurface.start()

        logger.info(f"SerialWorker (loadcells) started on {loadcells_cfg['port']}")
        logger.info(f"SerialWorker (resistance surface) started on {resistance_cfg['port']}")
    except Exception as e:
        logger.error(f"Failed to start SerialWorker: {e}")
        serialworker_loadCells = None
        serialworker_resistanceSurface = None

    while True:
        try:
            weight1 = 0
            weight2 = 0
            resistance_surface_data = ""
            
            if serialworker_loadCells:
                msg = drain_rx(serialworker_loadCells)
                
                if msg.startswith("loadcell_data: "):
                    try:
                        payload = msg.replace("loadcell_data: ", "")
                        weight1, weight2 = map(float, payload.split(',')[0:2])
                    except (ValueError, IndexError):
                        logger.warning(f"Failed to parse loadcell data: {msg}")
                        
            if serialworker_resistanceSurface:
                msg = drain_rx(serialworker_resistanceSurface)       
                if msg.startswith("L:"):
                    try:
                        resistance_surface_data = msg.replace("L:", "")
                    except (ValueError, IndexError):
                        logger.warning(f"Failed to parse L: data: {msg}")

            sensor_data = {
                'timestamp': time.time(),
                'position': round(acs.pilates.position, 2),
                'velocity': round(acs.pilates.velocity, 2),
                'weight': round(acs.pilates.weight, 2),
                'total_weight': round(acs.pilates.total_weight, 2),
                'rubber_coeff': round(acs.pilates.rubber_coeff, 2),
                'pull_coeff': round(acs.pilates.pull_coeff, 2),
                'push_coeff': round(acs.pilates.push_coeff, 2),
                'shake_coeff': round(acs.pilates.shake_coeff, 2),
                'hand1': weight1,
                'hand2': weight2,
                'connected_clients': connected_clients,
                'resistance_surface_data': resistance_surface_data
            }
            # print(f"Broadcasting sensor data: {sensor_data}")

            # logger.info(f"Broadcasting sensor data: {sensor_data}")
            socketio.emit('message', sensor_data)
            time.sleep(0.05)

        except Exception as e:
            logger.error(f"Error in bg_task: {e}")
            time.sleep(0.1)

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
            # if data_value_float < 0 or data_value_float > 1000:
            #     raise ValueError("Weight value out of range (0-1000)")
            acs.pilates.execute_command(f"WEIGHT={data_value_float}")
        
        elif data.startswith('RUBBER='):
            data_value = data.split('=')[1]
            data_value_float = float(data_value)
            # if data_value_float < 0 or data_value_float > 100:
            #     raise ValueError("Rubber value out of range (0-100)")
            acs.pilates.execute_command(f"RUBBER={data_value_float}")

        elif data.startswith('PULL='):
            data_value = data.split('=')[1]
            data_value_float = float(data_value)
            # if data_value_float < 0 or data_value_float > 100:
            #     raise ValueError("Pull value out of range (0-100)")
            acs.pilates.execute_command(f"PULL={data_value_float}")

        elif data.startswith('PUSH='):
            data_value = data.split('=')[1]
            data_value_float = float(data_value)
            # if data_value_float < 0 or data_value_float > 100:
            #     raise ValueError("Push value out of range (0-100)")
            acs.pilates.execute_command(f"PUSH={data_value_float}")
            
        elif data.startswith('SHAKE='):
            data_value = data.split('=')[1]
            data_value_float = float(data_value)
            # if data_value_float < 0 or data_value_float > 100:
            #     raise ValueError("Shake value out of range (0-100)")
            acs.pilates.execute_command(f"SHAKE={data_value_float}")
            
        else:
            raise ValueError("Unknown command")
        # emit('message', {'status': 'Command executed', 'command': data})
    
    except Exception as e:
        logger.error(f'Error executing command: {e}')
        # emit('message', {'status': 'Error', 'error': str(e)})

if __name__ == '__main__':
    # acs.pilates.start()
    threading.Thread(target=manual_listener, daemon=True).start()
    socketio.start_background_task(bg_task)
    # socketio.run(app, debug=True, use_reloader=False, port=8000)
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False, port=8000)

    # while True:
    #     time.sleep(1)