class Device:
    def __init__(
        self, address, RSSI, type, timestamp, channel=None, name=None, extAddress=None
    ):
        self.address = address
        self.RSSI = RSSI
        self.type = type  # BLE, WiFi-2.4GHz, ZigBee, 6LoWPAN
        self.timestamp = timestamp
        self.channel = channel
        self.name = name
        self.extAddress = extAddress
        self.key = (
            self.address + "_" + str(self.channel)
            if self.type != "WiFi-2.4GHz"
            else self.address
        )

    def __eq__(self, other):
        if isinstance(other, Device):
            if self.type == "ZigBee" and other.type == "ZigBee":
                return self.key == other.key
            elif self.type == other.type:
                return self.address == other.address
        return False

    def __repr__(self):
        return f"Device(address: {self.address}, RSSI:{self.RSSI}, type:{self.type}, timestamp:{self.timestamp}, channel:{self.channel}, name:{self.name}, extAddress:{self.extAddress})"
