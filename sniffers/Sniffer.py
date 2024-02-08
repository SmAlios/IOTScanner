import threading 
class Sniffer(threading.Thread):
    id_counter = -1

    # Sniffer constructor. 
    def __init__(self, serialport, baudrate, type):
        self.serialport = serialport
        self.baudrate = baudrate
        self.type = type
        self.id = Sniffer.get_new_id()
        self.running = False
        super().__init__()

    def __repr__(self):
        return 'sniffer ' + str(self.id) + ' (' + self.type + ', ' + self.serialport + ', ' + str(self.baudrate) + ')'
    
    @classmethod
    def get_new_id(cls):
        cls.id_counter += 1
        return cls.id_counter