import threading, random, time, datetime
from . import Sniffer
from logs.logger import logger
from devices.device import Device
from devices.network import Network
from serial import Serial, SerialException


class ZigBeeSniffer(Sniffer.Sniffer, threading.Thread):
    def __init__(self, serialport, baudrate):
        super().__init__(serialport, baudrate, type="ZigBee")

        self.oldChannels = []
        self.channels = []
        self.simulation = False
        valueTimeout = 10
        if self.simulation:
            for i in range(11, 27):
                self.channels.append(str(i))
            valueTimeout = 1
        self.dataVal = 0
        self.serial = Serial(serialport, baudrate, timeout=valueTimeout)
        self.devices = {}
        self.networks = {}
        self.logger = logger
        self.restart = False
        self.datas = [
            "received: 41D86FCDABFFFFEA5195E0EC3D05967F3B01F04D4C4D4C073600152A0800000000000001AA6CBF182D92A44F25F24A030D5A6BC65C8263279BF82C6D5F18B3EF8F9B5933C1 power: -8 lqi: 48 time: 152849947\r\n",  # 6lowpan broad
            "received: 41cc61ffff8a1800ffffda1c00881800ffffda1c00c107004742fb60400401169c6048656c6c6f20313338203078443838370a0012131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f50515253545556 power: -8 lqi: 48 time: 152849947\r\n",  # 6lowpan
            "received: 4188740601ffffb5a50910fcffb5a501ac35886903006f0d000870130713dd1a11722305452f01fa36119a3711cd5111415333bc6b11af7913468e11b89311af9511819811c3be0505d311 power: -8 lqi: 48 time: 152849947\r\n",  # link status
            "received: 4188c30601ffff65550800fdff3db215be0800130000000018c83db2216da902006f0d008e power: -8 lqi: 48 time: 152849947\r\n",  # device announcement
            "received: 4188630601ffff7c000910fcff532910b4ab87a902006f0d0001002f00001e power: -8 lqi: 48 time: 152849947\r\n",  # normal route request
            "received: 41887a0601ffffcd510910fcff00001c617f77994100a213000110b8fcff02 power: -8 lqi: 48 time: 152849947\r\n",  # many to one route request
            "received: 6188973ddf000063e00802000063e01e3e284ca603000500ae0601a852d000fd51f3e899cb12905f28aac67716641a17 power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188c30601ffff65550800fdff3db215be0800130000000018c83db2216da902006f0d008e power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188c30601ffff65550800fdff3db215be0800130000000018c83db2216da902006f0d008e power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188630601ffff7c000910fcff532910b4ab87a902006f0d0001002f00001e power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188630601ffff7c000910fcff532910b4ab87a902006f0d0001002f00001e power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188630601ffff7c000910fcff532910b4ab87a902006f0d0001002f00001e power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 41887a0601ffffcd510910fcff00001c617f77994100a213000110b8fcff02 power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 41887a0601ffffcd510910fcff00001c617f77994100a213000110b8fcff02 power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 41887a0601ffffcd510910fcff00001c617f77994100a213000110b8fcff02 power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 41887a0601ffffcd510910fcff00001c617f77994100a213000110b8fcff02 power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 6388223DDF0000C9B4040900 power: -83 lqi: 36 time: 155043482\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -80 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -70 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -13 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -51 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -52 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -36 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -26 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -46 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -77 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -66 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -44 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -34 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -54 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -20 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -80 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -83 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -86 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -87 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -81 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF00000912FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -82 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF 0000 0912 FCFF0000016F0100A7AF72A852D028E5B3A4000100A7AF72A852D0002509572926AF0CAF power: -8 lqi: 48 time: 152849947\r\n",
            # "received: 4188EF3DDFFFFF72EC0800FDFF3DB217BE0800130000000018C83DB2216DA902006F0D008E power: -8 lqi: 48 time: 152849947\r\n",
        ]

    def start(
        self,
        add_zigbee_device_row,
        update_zigbee_device_row,
        remove_zigbee_device_row,
        add_zigbee_network_row,
        update_zigbee_network_row,
        remove_zigbee_network_row,
        add_sixlowpan_device_row,
        update_sixlowpan_device_row,
        remove_sixlowpan_device_row,
    ):
        # device row operations
        self.add_zigbee_device_row = add_zigbee_device_row
        self.remove_zigbee_device_row = remove_zigbee_device_row
        self.update_zigbee_device_row = update_zigbee_device_row
        self.add_sixlowpan_device_row = add_sixlowpan_device_row
        self.update_sixlowpan_device_row = update_sixlowpan_device_row
        self.remove_sixlowpan_device_row = remove_sixlowpan_device_row
        # network row operations
        self.add_zigbee_network_row = add_zigbee_network_row
        self.update_zigbee_network_row = update_zigbee_network_row
        self.remove_zigbee_network_row = remove_zigbee_network_row

        self.running = True
        super().start()

    def stop(self):
        self.running = False
        self.serial.close()

    def findChannels(self):
        for _ in range(1):
            for channel in range(11, 27):
                self.logger.debug(f"Searching channel {channel}")

                self.serial.reset_input_buffer()
                timeout_start = time.time()
                self.serial.write("receive\r\n".encode())
                rec = self.serial.readline()
                self.serial.write("channel {}\r\n".format(channel).encode())
                rec = self.serial.readline()
                rec = None

                while time.time() < timeout_start + 10:
                    rec = self.serial.readline()

                    if not rec:
                        break

                    if (rec.decode().split())[0] == "channel":
                        continue

                    elif channel not in self.channels:
                        self.logger.debug(f"Found data on channel {channel}")
                        self.channels.append(channel)
                        self.serial.reset_input_buffer()
                        break

    def sniff(self):
        if not self.channels:
            return

        self.serial.write("receive\r\n".encode())
        rec = self.serial.readline()

        for channel in self.channels:
            self.logger.debug(f"Sniffing channel {channel}")
            self.dataVal = 0
            timeout_start = time.time()
            self.serial.write("channel {}\r\n".format(channel).encode())

            rec = self.serial.readline()
            rec = None

            while time.time() < timeout_start + random.randint(20, 30):
                if not self.running or self.restart:
                    self.restart = False
                    return

                rec = self.serial.readline()

                if not rec:
                    if self.simulation:
                        rec = self.datas[self.dataVal].encode()
                        self.dataVal += 1
                        if self.dataVal > len(self.datas):
                            self.dataVal = 0
                    else:
                        break

                if (rec.decode().split())[0] == "channel":
                    continue

                message = (rec.decode().split())[1]
                rssi = (rec.decode().split())[3]

                # Convert the message in hex to binary with padding
                messageBinSize = len(message) * 4
                messageBin = (bin(int(message, 16))[2:]).zfill(messageBinSize)

                frameTypeIEEE = messageBin[5:8]
                addressingModeIEEE = messageBin[8:10]
                destAddrModeIEEE = messageBin[12:14]
                intraPAN = messageBin[1]

                # First: Get the Frame Control Field bits that matter (Frame type and source addressing mode)

                # Doing the bytes checks
                if (
                    frameTypeIEEE != "010"
                    and addressingModeIEEE == "10"
                    and destAddrModeIEEE == "10"
                    and intraPAN == "1"
                ):
                    extAddr = ""

                    initialSrcAddress = message[16:18] + message[14:16]
                    value = (
                        "Source address: "
                        + initialSrcAddress
                        + ", RSSI: "
                        + rssi
                        + ", Channel: "
                        + str(channel)
                        + ", Type: "
                        + frameTypeIEEE
                    )

                    self.logger.debug(f"Read ZigBee value: {value}")

                    # If it is a frame type of data, then it has the upper layers heaers and we can explore the extended addresses.
                    if frameTypeIEEE == "001":
                        srcAddress = message[28:30] + message[26:28]
                        # If the bit for extended source on the FCF on the Network layer is true, then we can get the address from there
                        if int(messageBin[83]):
                            extAddr = ""
                            for i in range(0, 16, 2):
                                extAddr = message[34 + i : 36 + i] + extAddr
                                if i != 14:
                                    extAddr = ":" + extAddr

                        # If not present in the FCF of Network Layer, checks if there is the Security Header and if the address is inside it
                        elif int(messageBin[86]) and int(messageBin[138]):
                            extAddr = ""
                            for i in range(0, 16, 2):
                                extAddr = message[44 + i : 46 + i] + extAddr
                                if i != 14:
                                    extAddr = ":" + extAddr

                        elif not int(messageBin[86]) and message[42:46] == "0000":
                            print("zdp")
                            for i in range(0, 16, 2):
                                extAddr = message[56 + i : 58 + i] + extAddr
                                if i != 14:
                                    extAddr = ":" + extAddr

                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    new_device = Device(
                        address=srcAddress,
                        name=(None, "Hub")[srcAddress == "0000"],
                        RSSI=rssi,
                        type="ZigBee",
                        channel=channel,
                        extAddress=extAddr,
                        timestamp=timestamp,
                    )

                    if srcAddress == "0000" and intraPAN == "1":
                        panID = message[8:10] + message[6:8]
                        new_network = Network(
                            ID=panID,
                            RSSI=rssi,
                            channel=channel,
                            type="ZigBee",
                            timestamp=timestamp,
                        )
                        self.addOrUpdateNetwork(new_network)

                    self.addOrUpdateDevice(new_device)

                elif (
                    frameTypeIEEE != "010"
                    and addressingModeIEEE == "11"
                    and destAddrModeIEEE == "11"
                    and intraPAN == "1"
                ):
                    extAddr = ""
                    for i in range(0, 16, 2):
                        extAddr = message[26 + i : 28 + i] + extAddr
                        if i != 14:
                            extAddr = ":" + extAddr
                    print(extAddr)

                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    new_device = Device(
                        address=extAddr,
                        name=(None, "Hub")[extAddr == "0000"],
                        RSSI=rssi,
                        type="6LoWPAN",
                        channel=channel,
                        timestamp=timestamp,
                    )

                    self.addOrUpdateDevice(new_device)

                elif (
                    frameTypeIEEE != "010"
                    and addressingModeIEEE == "11"
                    and destAddrModeIEEE == "10"
                    and intraPAN == "1"
                ):
                    extAddr = ""
                    for i in range(0, 16, 2):
                        extAddr = message[14 + i : 16 + i] + extAddr
                        if i != 14:
                            extAddr = ":" + extAddr
                    print(extAddr)

                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    new_device = Device(
                        address=extAddr,
                        name=(None, "Hub")[extAddr == "0000"],
                        RSSI=rssi,
                        type="6LoWPAN",
                        channel=channel,
                        timestamp=timestamp,
                    )

                    self.addOrUpdateDevice(new_device)

    def run(self):
        while self.running:
            try:
                if not self.channels:
                    self.findChannels()
                else:
                    self.sniff()

            except SerialException as e:
                self.logger.error(
                    f"Error while reading data from nRF ZigBee Sniffer serial: {e}"
                )
            except Exception as e:
                self.logger.error(f"Error in ZigbeeSniffer thread: {e}")

    def addOrUpdateDevice(self, new_device):
        # Update existing device
        if new_device.key in self.devices:
            device = self.devices[new_device.key]
            if device.RSSI != new_device.RSSI:
                device.RSSI = new_device.RSSI
                if new_device.type == "ZigBee":
                    self.update_zigbee_device_row(
                        new_device.key, "RSSI", new_device.RSSI
                    )
                else:
                    self.update_sixlowpan_device_row(
                        new_device.key, "RSSI", new_device.RSSI
                    )
            if device.name != new_device.name and new_device.name != "":
                device.name = new_device.name
                if new_device.type == "ZigBee":
                    self.update_zigbee_device_row(
                        new_device.key, "name", new_device.name
                    )
                else:
                    self.update_sixlowpan_device_row(
                        new_device.key, "name", new_device.name
                    )

            if (
                device.extAddress != new_device.extAddress
                and new_device.extAddress != ""
                and new_device.extAddress
            ):
                device.extAddress = new_device.extAddress
                self.update_zigbee_device_row(
                    new_device.key, "extAddress", new_device.extAddress
                )
            if device.timestamp != new_device.timestamp:
                device.timestamp = new_device.timestamp
                if new_device.type == "ZigBee":
                    self.update_zigbee_device_row(
                        new_device.key, "timestamp", new_device.timestamp
                    )
                else:
                    self.update_sixlowpan_device_row(
                        new_device.key, "timestamp", new_device.timestamp
                    )
        # Add new device
        else:
            self.devices[new_device.key] = new_device
            if new_device.type == "ZigBee":
                self.add_zigbee_device_row(new_device)
            else:
                self.add_sixlowpan_device_row(new_device)

    def addOrUpdateNetwork(self, new_network):
        key = new_network.key

        # Update existing network
        if key in self.networks:
            network = self.networks[new_network.key]
            key = network.key
            if network.RSSI != new_network.RSSI:
                network.RSSI = new_network.RSSI
                self.update_zigbee_network_row(key, "RSSI", new_network.RSSI)
            if network.timestamp != new_network.timestamp:
                network.timestamp = new_network.timestamp
                self.update_zigbee_network_row(key, "timestamp", new_network.timestamp)

        # Add new network
        else:
            self.networks[key] = new_network
            self.add_zigbee_network_row(new_network)

    def setChannel(self, channel):
        if not self.oldChannels:
            self.oldChannels = self.channels
        self.restart = True
        self.channels = []
        self.channels.append(channel)

    def unsetChannel(self):
        self.restart = True
        self.channels = self.oldChannels
        self.oldChannels = []
