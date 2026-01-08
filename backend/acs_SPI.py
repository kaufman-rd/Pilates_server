import SPiiPlusPython as sp
import threading
import time
from enum import Enum, auto
import logging
import queue

import math


class Device_States(Enum):
    UNCONNECTED = -1
    UNINIT = 0
    IDLE = 1
    BUSY = 2
    DONE = 3
    ERROR = 4

    UNKNOWN = 99


class ACSController(threading.Thread):
    _state: Device_States = Device_States.UNCONNECTED
    _previous_state: Device_States = Device_States.UNCONNECTED
    _state_timer: float = 0.0

    velocity = 0
    position = 0
    
    def __init__(self, ip_address: str = "10.0.0.100", port: int = 701):
        self.ip_address = ip_address
        self.port = port
        self.handle = None  # Will store the communication handle

        threading.Thread.__init__(self, daemon=True)
        self.logger = logging.getLogger('__main__.'+__name__)
        self.logger.info("acs initialized")
        self.output_queue = queue.Queue()
        self.set_state(Device_States.UNCONNECTED)

    def connect(self) -> bool:
        print(f"Attempting to connect to controller at {self.ip_address}:{self.port}...")
        try:
            # Open the communication channel via TCP/IP
            # The handle is stored in self.handle for use in other functions
            self.handle = sp.OpenCommEthernetTCP(self.ip_address, self.port)
            if  self.handle == -1:
                self.logger.info(f"acs failed to connect with error: {err}")
                self.set_state(Device_States.UNCONNECTED)
                self.handle = None
            else:
                self.logger.info(f"ACS driver connected to {self.ip_address} successfully")
                self.set_state(Device_States.UNINIT)
        
        except Exception as err:
            self.logger.info(f"ACS driver connected to {self.ip_address} successfully")
            self.set_state(Device_States.UNCONNECTED)
            self.handle = None

    def disconnect(self):
        if self.handle is not None:
            print("Disconnecting from controller...")
            sp.CloseComm(self.handle)
            self.handle = None
            print("Disconnected.")
        else:
            print("Already disconnected.")

    def set_state(self, st):
        self._state_timer = time.time()
        self._previous_state = self._state
        self._state = st
        self.logger.info(f"acs state: {self._previous_state} -> {self._state}")
        # gv.gui_queue.put({"ACS": {"State" :f"{self._state.name}"}})

    def get_state(self):
        return self._state
    
    #------------------------------------------------------------

    def execute_command(self, command_str: str) -> str | None:
        """
        Sends a raw ACSPL+ command string to the controller and returns the response.

        Args:
            command_str (str): The ACSPL+ command to send (e.g., "?T1", "VEL(0)=100").

        Returns:
            str | None: The controller's response string, or None if an error occurs.
            """
        if self.handle is None:
            print("Error: Not connected to the controller.")
            return None
        try:
            # Use Transaction to send a command and receive a reply.
            reply = sp.Transaction(self.handle, command_str)
            
            # Check if reply is an AcsError object
            if hasattr(reply, '__class__') and 'AcsError' in str(type(reply)):
                print(f"Error executing command '{command_str}': {reply}")
                return None
            
            # The reply often includes a newline character, so we strip it.
            if isinstance(reply, str):
                return reply.strip()
            else:
                print(f"Unexpected reply type for command '{command_str}': {type(reply)}")
                return None
        except Exception as e:
            print(f"Error executing command '{command_str}': {e}")
            return None
    
    def enable_disable_axis(self, axis: int, enable: bool):
        if self.handle is None:
            print("Error: Not connected to the controller.")
            return
        
        if enable:
            try:
                sp.Enable(self.handle, axis)
                print(f"Axis {axis} enabled.")
            except Exception as e:
                print(f"Error: Failed to enable axis {axis}. {e}")
        else:
            try:
                sp.Disable(self.handle, axis)
                print(f"Axis {axis} disabled.")
            except Exception as e:
                print(f"Error: Failed to disable axis {axis}. {e}")

    def read_scalar(self, var_name: str, type: str) -> int | float | None:
        reply = self.execute_command(f"?{var_name}")
        if reply is not None:
            try:
                if type == 'int':
                    return int(reply)
                elif type == 'float':
                    return float(reply)
                else:
                    print(f"Error: Unsupported type '{type}' specified.")
                    return None
            except (ValueError, TypeError):
                print(f"Error: Could not parse {type} from controller reply: '{reply}'")
                return None

    def read_array(self, var_name: str, type: str) -> list | None:
        reply = self.execute_command(f"?{var_name}")
        if reply is not None:
            try:
                str_list = list(reply.replace(" ", "").replace("\r", ""))
                if type == 'int':
                    return [int(i) for i in str_list]
                elif type == 'float':
                    return [float(i) for i in str_list]
                else:
                    print(f"Error: Unsupported type '{type}' specified.")
                    return None
            except (ValueError, TypeError):
                print(f"Error: Could not parse integer from controller reply: '{reply}'")
                return None
        return None
        
    
    def run(self):
        self.connect()
        self.position = 0
        while True:
            # if self.handle is None:
            #     time.sleep(5)
            #     self.connect()
            #     continue

            # self.position = sp.GetFPosition(self.handle, 0)
            # self.velocity = sp.GetFVelocity(self.handle, 0)

            self.position +=1


            time.sleep(0.01)

acs = ACSController()

# --- Example Usage ---
if __name__ == '__main__':
    import time
    import random
    # Define your controller's IP address
    CONTROLLER_IP = "10.0.0.101"
    # Define the axis you want to control
    # TARGET_AXIS = 0 # Corresponds to ACSPL+ axis 0 (X)

    # 1. Create an instance of the controller
    controller = ACSController(ip_address=CONTROLLER_IP)
    var_int = "HOLE_POSITION"
    var_real = "TEST_REAL"
    array_real = "TEST_ARRAY_REAL"
    array_int = "TEST_ARRAY_INT"
    # 2. Connect to the controller
    if controller.connect():
        tic = time.time_ns()

        try:
            val_t1 = controller.read_scalar_real(var_int)
            if val_t1 is not None:
                print(f"Value of T1 is: {val_t1}")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print(f"Time elapsed: {(time.time_ns()-tic)/1000000:.2f} milliseconds")
            controller.disconnect()