
import acs_component.acs_SPI as acs
import SPiiPlusPython as sp
import math

commands= {
    "init": "INIT=1"
}

class PilatesController(acs.ACSController):
    def __init__(self, ip):
        super().__init__(ip_address=ip)
        self.position = 0.0
        self.velocity = 0.0
        self.weight = 0.0
        self.total_weight = 0.0
        self.rubber_coeff = 0.0
        self.pull_coeff = 0.0
        self.push_coeff = 0.0
        self.shake_coeff = 0.0

        self.conversion_to_meters = 120.0* math.pi / 16384

    def child_loop(self):
        self.position = sp.GetFPosition(self.handle, 1)
        # self.velocity = sp.GetFVelocity(self.handle, 0)
        self.velocity = self.read_scalar("PREDICTION", 'float')

        self.weight = self.read_scalar("WEIGHT", 'float')
        # self.total_weight = self.read_scalar("TOTAL_WEIGHT", 'float')
        self.total_weight = self.read_scalar("DCOM(1)", 'float') *-1
        self.rubber_coeff = self.read_scalar("RUBBER", 'float')
        self.pull_coeff = self.read_scalar("PULL", 'float')
        self.push_coeff = self.read_scalar("PUSH", 'float')
        self.shake_coeff = self.read_scalar("SHAKE", 'float')

pilates = PilatesController(ip = "10.0.0.100")