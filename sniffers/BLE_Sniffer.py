# Copyright (c) Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging, threading, datetime
from serial import SerialException
from . import Sniffer
from utils import Packet
from utils.Exceptions import SnifferTimeout
from logs.logger import logger
from utils.Types import *
from devices.device import Device


class BLESniffer(Sniffer.Sniffer, threading.Thread):
    def __init__(self, serialport, baudrate):
        super().__init__(serialport=serialport, baudrate=baudrate, type="BLE")
        self.packetReader = Packet.PacketReader(portnum=serialport, baudrate=baudrate)
        self.devices = {}
        self.logger = logger
        self.setup_scan()

        # Must the distance be converted to meters or display the RSSI ? (True for meters)
        self.convert = True

    # Signal the Sniffer to  for advertising devices by sending the REQ_SCAN_CONT UART packet.
    # This will cause it to stop sniffing any device it is sniffing at the moment.
    def setup_scan(self, findScanRsp=False, findAux=False, scanCoded=False):
        self.packetReader.sendScan(findScanRsp, findAux, scanCoded)
        self.packetReader.sendTK([0])

    def start(self, add_data_row, update_data_row, remove_data_row):
        self.add_data_row = add_data_row
        self.update_data_row = update_data_row
        self.remove_data_row = remove_data_row
        self.running = True
        super().start()

    def stop(self):
        self.running = False
        self.packetReader.doExit()

    def run(self):
        while self.running:
            """Start of the code reused"""
            try:
                packet = self.packetReader.getPacket(timeout=12)
                if packet == None or not packet.valid:
                    pass
            except SnifferTimeout as e:
                logging.info(str(e))
                packet = None
            except SerialException as e:
                self.logger.error(
                    f"Error while reading data from BLESniffer serial: {e}"
                )
                self.running = False

            if packet.id == EVENT_PACKET_DATA_PDU or packet.id == EVENT_PACKET_ADV_PDU:
                if packet.OK:
                    try:
                        if packet.blePacket.type == PACKET_TYPE_ADVERTISING:
                            if (
                                packet.blePacket.advType in [0, 1, 2, 4, 6, 7]
                                and packet.blePacket.advAddress != None
                                and packet.crcOK
                                and not packet.direction
                            ):
                                """End of the code reused"""
                                source_address = Packet.listToAddress(
                                    packet.blePacket.advAddress
                                )
                                timestamp = datetime.datetime.now().strftime("%H:%M:%S")

                                name = (
                                    packet.blePacket.name
                                    if (
                                        packet.blePacket.name != '""'
                                        or packet.blePacket.name != '"'
                                    )
                                    else ""
                                )

                                # create a device
                                new_device = Device(
                                    address=source_address,
                                    name=name,
                                    RSSI=packet.RSSI,
                                    type="BLE",
                                    timestamp=timestamp,
                                )
                                key = new_device.key

                                distance  = self.get_distance(new_device.RSSI, self.convert)

                                # Update existing device
                                if key in self.devices:
                                    device = self.devices[key]
                                    if device.channel != new_device.channel:
                                        device.channel = new_device.channel
                                        self.update_data_row(
                                            key, "channel", int(new_device.channel), "ble", "devices"
                                        )
                                    if device.RSSI != new_device.RSSI:
                                        device.RSSI = new_device.RSSI
                                        self.update_data_row(
                                            key, "RSSI", distance, "ble", "devices"
                                        )
                                    if (
                                        device.name != new_device.name
                                        and len(new_device.name) != 2
                                        and len(new_device.name) < 20
                                    ):
                                        device.name = new_device.name
                                        self.update_data_row(
                                            key, "name", new_device.name, "ble", "devices"
                                        )
                                    if device.timestamp != new_device.timestamp:
                                        device.timestamp = new_device.timestamp
                                        self.update_data_row(
                                            key, "timestamp", new_device.timestamp, "ble", "devices"
                                        )

                                # Add new device
                                else:
                                    self.devices[key] = new_device
                                    #self.add_ble_device_row(new_device)
                                    self.add_data_row(new_device, "ble", "devices")

                    except Exception as e:
                        logging.exception("packet processing error %s" % str(e))

    def get_devices(self):
        return self.devices
    
    # Calcul the distance in meters based on the RSSI
    def get_distance(self, RSSI, convert):
        mesured_power = -69 # mesure at 1m of a Nokia Kontact
        N = 2 # constante

        # BLE contant variate between 2 and 4. It's better to consider the low strenght

        if convert:
            distance = str(round(10**((mesured_power - int(RSSI))/(10*N)), 2)) + " m"
        else:
            distance = int(RSSI)

        return distance
