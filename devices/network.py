class Network:
    def __init__(self, ID, RSSI, channel, type, timestamp, BSSID=None):
        self.ID = ID #SSID or PANID
        self.RSSI = RSSI
        self.channel = channel
        self.type = type # WiFi-2.4GHz or ZigBee
        self.timestamp = timestamp
        self.BSSID = BSSID
        self.key = self.ID + "_" + str(self.channel)

        
    def __eq__(self, other):
        if isinstance(other, Network):
            return self.key == other.key
        return False
  
    def __repr__(self):
        return f"Network(ID:{self.ID}, RSSI:{self.RSSI}, channel:{self.channel}, type:{self.type}, timestamp:{self.timestamp}, BSSID:{self.BSSID})"
  