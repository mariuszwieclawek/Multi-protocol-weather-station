import threading

class ClientData:
    def __init__(self):
        self.proto = 'none'
        self.protobuff = 'none'
        self.AM2320_HUMIDITY = 0
        self.AM2320_TEMPERATURE = 0
        self.LPS25HB_PRESSURE = 0
        self.LPS25HB_TEMPERATURE = 0
        self.lock = threading.Lock()