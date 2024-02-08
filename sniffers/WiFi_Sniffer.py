import threading, time, datetime
from . import Sniffer
from logs.logger import logger
from devices.device import Device
from devices.network import Network
from serial import Serial, SerialException

class WiFiSniffer(Sniffer.Sniffer, threading.Thread):
    
    def __init__(self, serialport, baudrate):
        super().__init__(serialport, baudrate, type="WiFi-2.4GHz")
        self.serial = Serial(serialport, baudrate)
        self.devices = {}
        self.networks = {}
        self.logger = logger

    def start(self, add_wifi_device_row, update_wifi_device_row, remove_wifi_device_row, 
              add_wifi_network_row, update_wifi_network_row, remove_wifi_network_row):
        # device row operations
        self.add_wifi_device_row = add_wifi_device_row
        self.update_wifi_device_row = update_wifi_device_row
        self.remove_wifi_device_row = remove_wifi_device_row
        # network row operations
        self.add_wifi_network_row = add_wifi_network_row
        self.update_wifi_network_row = update_wifi_network_row
        self.remove_wifi_network_row = remove_wifi_network_row
        
        self.running = True
        super().start()
    
    def stop(self):
        self.running = False
        self.serial.close()

    def run(self):
        while self.running:
            # read data from serial port
            try:
                raw_data = self.serial.readline().decode("utf-8").strip()
            except SerialException as e:
                self.logger.error(f'Error while reading data from WiFiSniffer serial: {e}')
                self.running = False  
            # parse data
            self.parse_data(raw_data)
            # wait 1 ms before read again the serial port
            time.sleep(0.001) 

    def parse_data(self, raw_data):
        try: 
            l = raw_data.split(',')
            # WiFi Network scanned
            if(l[0] == 'N'): 
                self.parse_network_data(l)
            # WiFi Packet sniffed
            elif(l[0] == 'H' or (len(l[0]) == 2 and (l[0])[1] == 'H') ):
                if(len(l[0]) == 2 and (l[0])[1] == 'H'):
                    raise Exception(f'format of WiFi data unknown: {l}')
                self.parse_device_data(l)
            # something wrong happened
            else:
                if(l[0] == 'E' and l.find("esp_netif_new")):
                    # send information to sniff only required channel in case of reboot
                    previous_channel = self.wifi_device_table.get_selected_channel()
                    if(previous_channel != -1):
                        self.serial.write(str(previous_channel).encode('utf-8'))
                raise Exception(f'format of WiFi data unknown: {l}')
        
        except Exception as e:
            self.logger.error(f'Error in parsing WiFi data: {e}')
            
    def parse_network_data(self, l):
        try: 
            [_,channel, RSSI, SSID, BSSID] = l
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            # create a network
            new_network = Network(SSID, int(RSSI), int(channel), 'WiFi-2.4GHz', timestamp, BSSID)
            key = new_network.key

            # Update existing network
            if(key in self.networks):
                network = self.networks[key]
                if(network.RSSI != new_network.RSSI):
                    network.RSSI = new_network.RSSI
                    self.update_wifi_network_row(key, "RSSI", int(RSSI))
                    
                if(network.BSSID != new_network.BSSID):
                    network.BSSID = new_network.BSSID
                    self.update_wifi_network_row(key, "BSSID", BSSID)
            
                if(network.timestamp != new_network.timestamp):
                    network.timestamp = new_network.timestamp
                    self.update_wifi_network_row(key, "timestamp", timestamp)
        
            # Add new network
            else:
                self.networks[key] = new_network
                self.add_wifi_network_row(new_network)

        except Exception as e:
            self.logger.error(f'Error parsing wifi network data: {e}')

    def parse_device_data(self, l):
        try: 
            [_,channel, RSSI, source_address, frame_type] = l
        except Exception as e:
            self.logger.error(f'Error parsing WiFi device data: {e}')

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # create a device
        new_device = Device(source_address, int(RSSI), 'WiFi-2.4GHz', timestamp, int(channel))
        key = new_device.key
        
        # Update existing device
        if(key in self.devices):
            device = self.devices[key]
            if(device.RSSI != new_device.RSSI):
                device.RSSI = new_device.RSSI
                self.update_wifi_device_row(key, "RSSI", int(RSSI))
            if(device.channel != new_device.channel):
                device.channel = new_device.channel
                self.update_wifi_device_row(key, "channel", int(channel))  
            if(device.timestamp != new_device.timestamp):
                device.timestamp = new_device.timestamp
                self.update_wifi_device_row(key, "timestamp", timestamp)      
                    
        # Add new device
        else:
            self.devices[key] = new_device
            self.add_wifi_device_row(new_device)
    
    def set_wifi_device_table(self, wifi_device_table):
        self.wifi_device_table = wifi_device_table