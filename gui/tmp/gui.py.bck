""" 
The gui.py file primarily contain code related to the creation and management of the GUI elements, such as defining the layout, creating buttons and labels, and handling user input.
"""

import tkinter as tk
from gui.scrollable_frame import ScrollableFrame
from gui.network_gui import NetworkTable
from gui.device_gui import DeviceTable, SeizedDeviceTable
from logs.logger import logger


class GUI:
    def __init__(self, master, BLE_sniffer, WiFi_sniffer, ZigBee_sniffer):
        self.logger = logger  # configure logger
        self.master = master
        self.BLE_sniffer = BLE_sniffer
        self.WiFi_sniffer = WiFi_sniffer
        self.ZigBee_sniffer = ZigBee_sniffer
        self.seized_devices = set()
        self.create_widgets()

    # ====================
    # Widgets functions
    # ====================
    def create_widgets(self):
        # create control panel frame
        self.control_frame = tk.LabelFrame(
            self.master,
            text="Control Panel",
            font=("Arial", 20),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.RAISED,
            padx=0,
            pady=5,
            background="white",
        )
        self.control_frame.grid(row=0, column=0, sticky="nsew")
        self.create_control_frame()

        # create WiFi sniffer column
        self.wifi_sniffer_frame = tk.LabelFrame(
            self.master,
            text="WiFi Sniffer",
            font=("Arial", 20),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.RAISED,
            padx=0,
            pady=5,
            background="white",
        )
        self.wifi_sniffer_frame.grid(row=0, column=1, sticky="nsew")
        self.create_wifi_sniffer_frame()

        # create BLE sniffer column
        self.ble_sniffer_frame = tk.LabelFrame(
            self.master,
            text="BLE Sniffer",
            font=("Arial", 20),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.RAISED,
            padx=0,
            pady=5,
            background="white",
        )
        self.ble_sniffer_frame.grid(row=0, column=2, sticky="nsew")
        self.create_ble_sniffer_frame()

        # create ZigBee sniffer column
        self.zigbee_sniffer_frame = tk.LabelFrame(
            self.master,
            text="IEEE 802.15.4 Sniffer",
            font=("Arial", 20),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.RAISED,
            padx=0,
            pady=5,
            background="white",
        )
        self.zigbee_sniffer_frame.grid(row=0, column=3, sticky="nsew")
        self.create_zigbee_sniffer_frame()

        # create 6LowPAN sniffer column
        self.sixlowpan_sniffer_frame = tk.LabelFrame(
            self.master,
            text="6LoWPAN Sniffer",
            font=("Arial", 20),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.RAISED,
            padx=0,
            pady=5,
            background="white",
        )
        # self.sixlowpan_sniffer_frame.grid(row=0, column=4, sticky="nsew")
        # self.create_sixlowpan_sniffer_frame()

        # adjust row height and column width
        self.master.grid_columnconfigure(0, minsize=100, weight=2)
        self.master.grid_columnconfigure(1, minsize=450, weight=2)
        self.master.grid_columnconfigure(2, minsize=450, weight=2)
        self.master.grid_columnconfigure(3, minsize=450, weight=1)
        # self.master.grid_columnconfigure(4, minsize=400, weight=2)
        self.master.grid_rowconfigure(0, weight=1)

    # ====================
    # Command frame
    # ====================
    def create_control_frame(self):
        self.commands_frame = tk.LabelFrame(
            self.control_frame,
            text="",
            font=("Arial", 20),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.commands_frame.grid(row=0, column=0, sticky="nsew")
        self.create_commands_frame()

        # create seized device frame
        self.seized_devices_frame = tk.LabelFrame(
            self.control_frame,
            text="Seized Devices",
            font=("Arial", 16),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.seized_devices_frame.grid(row=1, column=0, sticky="nsew")
        self.create_seized_device_frame()

        # adjust row height and column width
        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid_rowconfigure(1, weight=2)
        self.control_frame.grid_columnconfigure(0, weight=1)

    def create_commands_frame(self):
        # create start button
        self.start_button = tk.Button(
            self.commands_frame,
            text="Start",
            font=("Arial", 14),
            command=self.on_start_click,
            borderwidth=5,
            relief=tk.RAISED,
            padx=0,
            pady=5,
        )
        self.start_button.grid(row=0, column=0, sticky="n")
        # create stop button
        self.stop_button = tk.Button(
            self.commands_frame,
            text="Stop",
            font=("Arial", 14),
            command=self.on_stop_click,
            borderwidth=5,
            relief=tk.RAISED,
            padx=0,
            pady=5,
        )
        self.stop_button.grid(row=0, column=1, sticky="n")

        self.commands_frame.grid_columnconfigure(0, weight=1)
        self.commands_frame.grid_columnconfigure(1, weight=1)
        self.commands_frame.grid_rowconfigure(0, weight=1)

    def create_seized_device_frame(self):
        # create seized devices table
        self.seized_device_scrollable_frame = ScrollableFrame(self.seized_devices_frame)
        self.seized_device_scrollable_frame.pack(side="top", fill="both", expand=True)

        # create device table heading
        tk.Label(self.seized_device_scrollable_frame.item_frame, text="Channel").grid(
            row=0, column=0, sticky="nsew"
        )
        tk.Label(self.seized_device_scrollable_frame.item_frame, text="Address").grid(
            row=0, column=1, sticky="nsew"
        )
        tk.Label(self.seized_device_scrollable_frame.item_frame, text="Type").grid(
            row=0, column=2, sticky="nsew"
        )

        # column configure
        self.seized_device_scrollable_frame.item_frame.columnconfigure(
            index=0, weight=1
        )
        self.seized_device_scrollable_frame.item_frame.columnconfigure(
            index=1, weight=1
        )
        self.seized_device_scrollable_frame.item_frame.columnconfigure(
            index=2, weight=1
        )

        self.seized_device_table = SeizedDeviceTable(
            self.seized_device_scrollable_frame.item_frame
        )

    # ====================
    # WiFi frames
    # ====================
    def create_wifi_sniffer_frame(self):
        # create WiFi devices frame
        self.wifi_devices_frame = tk.LabelFrame(
            self.wifi_sniffer_frame,
            text="WiFi Devices",
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.wifi_devices_frame.grid(row=1, column=0, sticky="nsew")
        self.create_wifi_devices_frame()

        # create WiFi networks frame
        self.wifi_networks_frame = tk.LabelFrame(
            self.wifi_sniffer_frame,
            text="WiFi Networks",
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.wifi_networks_frame.grid(row=0, column=0, sticky="nsew")
        self.create_wifi_networks_frame()

        # adjust row height and column width
        self.wifi_sniffer_frame.grid_rowconfigure(0, weight=1)
        self.wifi_sniffer_frame.grid_rowconfigure(1, weight=100)
        self.wifi_sniffer_frame.grid_columnconfigure(0, weight=1)

    def create_wifi_devices_frame(self):
        # create WiFi device table
        self.wifi_device_scrollable_frame = ScrollableFrame(self.wifi_devices_frame)
        self.wifi_device_scrollable_frame.pack(side="top", fill="both", expand=True)

        # create device table heading
        tk.Label(self.wifi_device_scrollable_frame.item_frame, text="RSSI").grid(
            row=0, column=1, sticky="nsew"
        )
        tk.Label(self.wifi_device_scrollable_frame.item_frame, text="Channel").grid(
            row=0, column=2, sticky="nsew"
        )
        tk.Label(self.wifi_device_scrollable_frame.item_frame, text="Address").grid(
            row=0, column=3, sticky="nsew"
        )
        tk.Label(self.wifi_device_scrollable_frame.item_frame, text="Updated").grid(
            row=0, column=4, sticky="nsew"
        )
        tk.Label(self.wifi_device_scrollable_frame.item_frame, text="Action").grid(
            row=0, column=5, sticky="nsew"
        )

        # column configure
        self.wifi_device_scrollable_frame.item_frame.columnconfigure(
            index=0, weight=1, pad=5
        )
        self.wifi_device_scrollable_frame.item_frame.columnconfigure(
            index=1, weight=1, pad=5
        )
        self.wifi_device_scrollable_frame.item_frame.columnconfigure(
            index=2, weight=1, pad=5
        )
        self.wifi_device_scrollable_frame.item_frame.columnconfigure(
            index=3, weight=3, pad=5
        )
        self.wifi_device_scrollable_frame.item_frame.columnconfigure(
            index=4, weight=3, pad=5
        )
        self.wifi_device_scrollable_frame.item_frame.columnconfigure(
            index=5, weight=3, pad=5
        )

        self.wifi_device_table = DeviceTable(
            self.wifi_device_scrollable_frame.item_frame, self.add_seized_device_row
        )
        # self.WiFi_sniffer.set_wifi_device_table(self.wifi_device_table)

    def create_wifi_networks_frame(self):
        # create WiFi network table
        self.wifi_network_scrollable_frame = ScrollableFrame(self.wifi_networks_frame)
        self.wifi_network_scrollable_frame.pack(side="top", fill="both", expand=True)

        # create network table heading
        tk.Label(self.wifi_network_scrollable_frame.item_frame, text="RSSI").grid(
            row=0, column=1, sticky="nsew"
        )
        tk.Label(self.wifi_network_scrollable_frame.item_frame, text="Channel").grid(
            row=0, column=2, sticky="nsew"
        )
        tk.Label(self.wifi_network_scrollable_frame.item_frame, text="SSID").grid(
            row=0, column=3, sticky="nsew"
        )
        tk.Label(self.wifi_network_scrollable_frame.item_frame, text="BSSID").grid(
            row=0, column=4, sticky="nsew"
        )
        tk.Label(self.wifi_network_scrollable_frame.item_frame, text="Updated").grid(
            row=0, column=5, sticky="nsew"
        )

        # column configure
        self.wifi_network_scrollable_frame.item_frame.columnconfigure(
            index=0, weight=1, pad=5
        )
        self.wifi_network_scrollable_frame.item_frame.columnconfigure(
            index=1, weight=1, pad=5
        )
        self.wifi_network_scrollable_frame.item_frame.columnconfigure(
            index=2, weight=1, pad=5
        )
        self.wifi_network_scrollable_frame.item_frame.columnconfigure(
            index=3, weight=3, pad=5
        )
        self.wifi_network_scrollable_frame.item_frame.columnconfigure(
            index=4, weight=3, pad=5
        )
        self.wifi_network_scrollable_frame.item_frame.columnconfigure(
            index=5, weight=3, pad=5
        )

        self.wifi_network_table = NetworkTable(
            self.wifi_network_scrollable_frame.item_frame,
            self.WiFi_sniffer,
            self.wifi_device_table,
        )

    # ====================
    # BLE frames
    # ====================
    def create_ble_sniffer_frame(self):
        # create BLE devices frame
        self.ble_devices_frame = tk.LabelFrame(
            self.ble_sniffer_frame,
            text="BLE Devices",
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.ble_devices_frame.pack(side="top", fill="both", expand=True)
        self.create_ble_devices_frame()

    def create_ble_devices_frame(self):
        # create BLE device table
        self.ble_device_scrollable_frame = ScrollableFrame(self.ble_devices_frame)
        self.ble_device_scrollable_frame.pack(side="top", fill="both", expand=True)

        # create device table heading
        tk.Label(self.ble_device_scrollable_frame.item_frame, text="RSSI").grid(
            row=0, column=1, sticky="nsew"
        )
        tk.Label(self.ble_device_scrollable_frame.item_frame, text="Address").grid(
            row=0, column=2, sticky="nsew"
        )
        tk.Label(self.ble_device_scrollable_frame.item_frame, text="Name").grid(
            row=0, column=3, sticky="nsew"
        )
        tk.Label(self.ble_device_scrollable_frame.item_frame, text="Updated").grid(
            row=0, column=4, sticky="nsew"
        )
        tk.Label(self.ble_device_scrollable_frame.item_frame, text="Action").grid(
            row=0, column=5, sticky="nsew"
        )

        # column configure
        self.ble_device_scrollable_frame.item_frame.columnconfigure(index=0, weight=1)
        self.ble_device_scrollable_frame.item_frame.columnconfigure(index=1, weight=1)
        self.ble_device_scrollable_frame.item_frame.columnconfigure(index=2, weight=1)
        self.ble_device_scrollable_frame.item_frame.columnconfigure(index=3, weight=1)
        self.ble_device_scrollable_frame.item_frame.columnconfigure(index=4, weight=1)
        self.ble_device_scrollable_frame.item_frame.columnconfigure(index=5, weight=1)

        self.ble_device_table = DeviceTable(
            self.ble_device_scrollable_frame.item_frame, self.add_seized_device_row
        )

    # ====================
    # ZigBee frames
    # ====================
    def create_zigbee_sniffer_frame(self):
        # create ZigBee devices frame
        self.zigbee_devices_frame = tk.LabelFrame(
            self.zigbee_sniffer_frame,
            text="ZigBee Devices",
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.zigbee_devices_frame.grid(row=1, column=0, sticky="nsew")
        self.create_zigbee_devices_frame()

        self.sixlowpan_devices_frame = tk.LabelFrame(
            self.zigbee_sniffer_frame,
            text="6LoWPAN Devices",
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.sixlowpan_devices_frame.grid(row=2, column=0, sticky="nsew")
        self.create_sixlowpan_devices_frame()

        # create ZigBee networks frame
        self.zigbee_networks_frame = tk.LabelFrame(
            self.zigbee_sniffer_frame,
            text="ZigBee Networks",
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.zigbee_networks_frame.grid(row=0, column=0, sticky="nsew")
        self.create_zigbee_networks_frame()

        # adjust row height and column width
        self.zigbee_sniffer_frame.grid_rowconfigure(0, weight=1)
        self.zigbee_sniffer_frame.grid_rowconfigure(1, weight=100)
        self.zigbee_sniffer_frame.grid_columnconfigure(0, weight=1)

    def create_zigbee_devices_frame(self):
        # create ZigBee device table
        self.zigbee_device_scrollable_frame = ScrollableFrame(self.zigbee_devices_frame)
        self.zigbee_device_scrollable_frame.pack(side="top", fill="both", expand=True)

        # create device table heading
        tk.Label(self.zigbee_device_scrollable_frame.item_frame, text="RSSI").grid(
            row=0, column=1, sticky="nsew"
        )
        tk.Label(self.zigbee_device_scrollable_frame.item_frame, text="Channel").grid(
            row=0, column=2, sticky="nsew"
        )
        tk.Label(self.zigbee_device_scrollable_frame.item_frame, text="Address").grid(
            row=0, column=3, sticky="nsew"
        )
        tk.Label(
            self.zigbee_device_scrollable_frame.item_frame, text="Full Address"
        ).grid(row=0, column=4, sticky="nsew")
        tk.Label(self.zigbee_device_scrollable_frame.item_frame, text="Updated").grid(
            row=0, column=5, sticky="nsew"
        )
        tk.Label(self.zigbee_device_scrollable_frame.item_frame, text="Action").grid(
            row=0, column=6, sticky="nsew"
        )

        # column configure
        self.zigbee_device_scrollable_frame.item_frame.columnconfigure(
            index=0, weight=1, pad=5
        )
        self.zigbee_device_scrollable_frame.item_frame.columnconfigure(
            index=1, weight=1, pad=5
        )
        self.zigbee_device_scrollable_frame.item_frame.columnconfigure(
            index=2, weight=1, pad=5
        )
        self.zigbee_device_scrollable_frame.item_frame.columnconfigure(
            index=3, weight=1, pad=5
        )
        self.zigbee_device_scrollable_frame.item_frame.columnconfigure(
            index=4, weight=2, pad=5
        )
        self.zigbee_device_scrollable_frame.item_frame.columnconfigure(
            index=5, weight=2, pad=5
        )
        self.zigbee_device_scrollable_frame.item_frame.columnconfigure(
            index=6, weight=2, pad=5
        )

        self.zigbee_device_table = DeviceTable(
            self.zigbee_device_scrollable_frame.item_frame, self.add_seized_device_row
        )

    def create_zigbee_networks_frame(self):
        # create ZigBee network table
        self.zigbee_network_scrollable_frame = ScrollableFrame(
            self.zigbee_networks_frame
        )
        self.zigbee_network_scrollable_frame.pack(side="top", fill="both", expand=True)

        # create network table heading
        tk.Label(self.zigbee_network_scrollable_frame.item_frame, text="RSSI").grid(
            row=0, column=1, sticky="nsew"
        )
        tk.Label(self.zigbee_network_scrollable_frame.item_frame, text="Channel").grid(
            row=0, column=2, sticky="nsew"
        )
        tk.Label(self.zigbee_network_scrollable_frame.item_frame, text="PAN ID").grid(
            row=0, column=3, sticky="nsew"
        )
        tk.Label(self.zigbee_network_scrollable_frame.item_frame, text="Updated").grid(
            row=0, column=4, sticky="nsew"
        )

        # column configure
        self.zigbee_network_scrollable_frame.item_frame.columnconfigure(
            index=0, weight=1, pad=5
        )
        self.zigbee_network_scrollable_frame.item_frame.columnconfigure(
            index=1, weight=1, pad=5
        )
        self.zigbee_network_scrollable_frame.item_frame.columnconfigure(
            index=2, weight=1, pad=5
        )
        self.zigbee_network_scrollable_frame.item_frame.columnconfigure(
            index=3, weight=1, pad=5
        )
        self.zigbee_network_scrollable_frame.item_frame.columnconfigure(
            index=4, weight=2, pad=5
        )

        self.zigbee_network_table = NetworkTable(
            self.zigbee_network_scrollable_frame.item_frame,
            self.ZigBee_sniffer,
            self.zigbee_device_table,
        )

    # ====================
    # 6LoWPAN frames
    # ====================
    def create_sixlowpan_sniffer_frame(self):
        # create 6LoWPAN devices frame
        self.sixlowpan_devices_frame = tk.LabelFrame(
            self.sixlowpan_sniffer_frame,
            text="6LoWPAN Devices",
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.sixlowpan_devices_frame.pack(side="top", fill="both", expand=True)
        self.create_sixlowpan_devices_frame()

    def create_sixlowpan_devices_frame(self):
        # create BLE device table
        self.sixlowpan_device_scrollable_frame = ScrollableFrame(
            self.sixlowpan_devices_frame
        )
        self.sixlowpan_device_scrollable_frame.pack(
            side="top", fill="both", expand=True
        )

        # create device table heading
        tk.Label(self.sixlowpan_device_scrollable_frame.item_frame, text="RSSI").grid(
            row=0, column=1, sticky="nsew"
        )
        tk.Label(
            self.sixlowpan_device_scrollable_frame.item_frame, text="Channel"
        ).grid(row=0, column=2, sticky="nsew")
        tk.Label(
            self.sixlowpan_device_scrollable_frame.item_frame, text="Address"
        ).grid(row=0, column=3, sticky="nsew")
        tk.Label(
            self.sixlowpan_device_scrollable_frame.item_frame, text="Updated"
        ).grid(row=0, column=4, sticky="nsew")
        tk.Label(self.sixlowpan_device_scrollable_frame.item_frame, text="Action").grid(
            row=0, column=5, sticky="nsew"
        )

        # column configure
        self.sixlowpan_device_scrollable_frame.item_frame.columnconfigure(
            index=0, weight=1
        )
        self.sixlowpan_device_scrollable_frame.item_frame.columnconfigure(
            index=1, weight=1
        )
        self.sixlowpan_device_scrollable_frame.item_frame.columnconfigure(
            index=2, weight=1
        )
        self.sixlowpan_device_scrollable_frame.item_frame.columnconfigure(
            index=3, weight=1
        )
        self.sixlowpan_device_scrollable_frame.item_frame.columnconfigure(
            index=4, weight=1
        )
        self.sixlowpan_device_scrollable_frame.item_frame.columnconfigure(
            index=5, weight=1
        )

        self.sixlowpan_device_table = DeviceTable(
            self.sixlowpan_device_scrollable_frame.item_frame,
            self.add_seized_device_row,
        )

    # ====================
    # Buttons functions
    # ====================
    def on_start_click(self):
        self.logger.debug("Start clicked")
        try:
            self.BLE_sniffer.start(
                self.add_ble_device_row,
                self.update_ble_device_row,
                self.remove_ble_device_row,
            )
        except Exception as e:
            self.logger.error(f"Error while starting scan of BLESniffer: {e}")
        try:
            self.WiFi_sniffer.start(
                self.add_wifi_device_row,
                self.update_wifi_device_row,
                self.remove_wifi_device_row,
                self.add_wifi_network_row,
                self.update_wifi_network_row,
                self.remove_wifi_network_row,
            )
        except Exception as e:
            self.logger.error(f"Error while starting scan of WiFiSniffer: {e}")

        try:
            self.ZigBee_sniffer.start(
                self.add_zigbee_device_row,
                self.update_zigbee_device_row,
                self.remove_zigbee_device_row,
                self.add_zigbee_network_row,
                self.update_zigbee_network_row,
                self.remove_zigbee_network_row,
                self.add_sixlowpan_device_row,
                self.update_sixlowpan_device_row,
                self.remove_sixlowpan_device_row,
            )
        except Exception as e:
            self.logger.error(f"Error while starting scan of ZigBeeSniffer: {e}")

    def on_stop_click(self):
        self.logger.debug("Stop clicked")
        # stop reader threads when button clicked
        try:
            self.BLE_sniffer.stop()
        except Exception as e:
            self.logger.error(f"Error while stoping scan of {self.BLE_sniffer}: {e}")
        try:
            self.WiFi_sniffer.stop()
        except Exception as e:
            self.logger.error(f"Error while stoping scan of {self.WiFi_sniffer}: {e}")
        try:
            self.ZigBee_sniffer.stop()
        except Exception as e:
            self.logger.error(f"Error while stoping scan of {self.ZigBee_sniffer}: {e}")

    # ====================
    # Seized Devices call back functions
    # ====================
    def add_seized_device_row(self, device):
        self.logger.debug(f"{device.__repr__()} seized")
        self.seized_devices.add(device.key)  # Add device to the set of seized devices
        self.seized_device_table.add_row(device)
        if device.type == "WiFi-2.4GHz":
            self.wifi_device_table.remove_row(device.key)
        elif device.type == "BLE":
            self.ble_device_table.remove_row(device.key)
        elif device.type == "ZigBee":
            self.zigbee_device_table.remove_row(device.key)
        elif device.type == "6LoWPAN":
            self.sixlowpan_device_table.remove_row(device.key)

    # ====================
    # WiFi call back functions
    # ====================
    def add_wifi_network_row(self, network):
        self.wifi_network_table.add_row(network)

    def update_wifi_network_row(self, key, field, value):
        self.wifi_network_table.update_row(key, field, value)

    def remove_wifi_network_row(self, key):
        self.wifi_network_table.remove_row(key)

    def add_wifi_device_row(self, device):
        if device.key in self.seized_devices:
            pass
        else:
            self.wifi_device_table.add_row(device)

    def update_wifi_device_row(self, key, field, value):
        if key in self.seized_devices:
            pass
        else:
            self.wifi_device_table.update_row(key, field, value)

    def remove_wifi_device_row(self, key):
        self.wifi_device_table.remove_row(key)

    # ====================
    # BLE call back functions
    # ====================
    def add_ble_device_row(self, device):
        if device.key in self.seized_devices:
            pass
        else:
            self.ble_device_table.add_row(device)

    def update_ble_device_row(self, key, field, value):
        if key in self.seized_devices:
            pass
        else:
            self.ble_device_table.update_row(key, field, value)

    def remove_ble_device_row(self, key):
        self.ble_device_table.remove_row(key)

    # ====================
    # ZigBee Call back functions
    # ====================
    def add_zigbee_network_row(self, network):
        self.zigbee_network_table.add_row(network)

    def update_zigbee_network_row(self, key, field, value):
        self.zigbee_network_table.update_row(key, field, value)

    def remove_zigbee_network_row(self, key):
        self.zigbee_network_table.remove_row(key)

    def add_zigbee_device_row(self, device):
        if device.key in self.seized_devices:
            pass
        else:
            self.zigbee_device_table.add_row(device)

    def update_zigbee_device_row(self, key, field, value):
        if key in self.seized_devices:
            pass
        else:
            self.zigbee_device_table.update_row(key, field, value)

    def remove_zigbee_device_row(self, key):
        self.zigbee_device_table.remove_row(key)

    # ====================
    # 6LoWPAN call back functions
    # ====================
    def add_sixlowpan_device_row(self, device):
        if device.key in self.seized_devices:
            pass
        else:
            self.sixlowpan_device_table.add_row(device)

    def update_sixlowpan_device_row(self, key, field, value):
        if key in self.seized_devices:
            pass
        else:
            self.sixlowpan_device_table.update_row(key, field, value)

    def remove_sixlowpan_device_row(self, key):
        self.sixlowpan_device_table.remove_row(key)
