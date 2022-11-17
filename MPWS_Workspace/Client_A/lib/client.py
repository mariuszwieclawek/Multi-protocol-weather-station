import _thread

class ClientData:
    def __init__(self):
        self.protocol = 'none'
        self.protocol_buffer = 'none'
        self.HUMIDITY = 0
        self.TEMPERATURE = 0
        self.MEASURE_READY = False
        self.lock = _thread.allocate_lock()
