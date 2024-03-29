import tkinter as tk
import os, subprocess
from devices.csv import CSV
from devices.device import Device
from devices.network import Network
from gui.scrollable_frame import ScrollFrame
from gui.network_gui import NetworkTable
from gui.device_gui import DeviceTable, SeizedDeviceTable
from logs.logger import logger
from .myprogressbar import Myprogressbar
from devices.compress import Compress

from time import sleep
import platform


class GUI:
    def __init__(self, master, BLE_sniffer, WiFi_sniffer, ZigBee_sniffer, current_pannel):
        self.logger = logger  # configure logger
        self.master = master
        self.BLE_sniffer = BLE_sniffer
        self.WiFi_sniffer = WiFi_sniffer
        self.ZigBee_sniffer = ZigBee_sniffer
        self.seized_devices = set()

        self.pannels = ["Home","WiFi","BLE","Zigbee","6loWPAN"]
        self.current_pannel = self.pannels[current_pannel]
        self.fields_ble = ["address", "RSSI", "type", "timestamp", "channel", "name", "extAddress"]
        self.fields_wifi_networks = ["ID", "RSSI", "channel", "type", "timestamp", "BSSID"]
        self.fields_wifi_devices = self.fields_ble
        self.fields_zigbee_networks = ["ID", "RSSI", "channel", "type", "timestamp"]
        self.fields_zigbee_devices = ["address", "name", "RSSI", "type", "channel", "extAddress", "timestamp"]
        self.fields_sixlowpan = ["address", "name", "RSSI", "type", "channel", "timestamp"]

        self.zigbee_scan_start = 11
        self.zigbee_scan_progress = 0
        self.zigbee_scan_end = 27

        self.scan_progressbar = Myprogressbar()
        self.scv_dir = "csv_dir"
        self.csv_file = CSV("csv_dir")

        self.allowed_file_sys_for_usb_key = ["exfat", "fat32", "ntfs", "ext", "ext4"]

        self.scan_started = False

        self.call_frequence_widget(self.current_pannel)

    # ====================
    # Rebuild
    # ====================
        
    #choose the frequence to display, this'll display the control board and
    #the tables containing data about the scanned frequences
    def call_frequence_widget(self, protocol):
        
        if protocol == "WiFi":
            title = "WiFi Sniffer"
        elif protocol == "BLE":
            title = "BLE Devices"
        elif protocol == "Zigbee":
            title = "ZigBee Devices"
        elif protocol == "6loWPAN":
            title = "6LoWPAN Devices"
        elif protocol == "Home":
            self.create_home_frame()


        if protocol != "Home":
            self.create_frequence_widget(title)  

    def create_frequence_widget(self, title):
        self.control_frame = tk.LabelFrame(
            self.master,
            text="Control Panel",
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.RAISED,
            padx=0,
            pady=50,
            background="white",
        )
        self.control_frame.grid(row=0, column=0, sticky="nsew")
        self.create_control_frame()

        # create blank space usable to display tables
        self.widget_base_frame = tk.LabelFrame(
            self.master,
            text=title,
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.RAISED,
            padx=0,
            pady=5,
            background="white",
        )
        self.widget_base_frame.grid(row=0, column=1, sticky="nsew")

        if title == "WiFi Sniffer":
            self.create_wifi_sniffer_frame()
        elif title == "BLE Devices":
            self.create_ble_sniffer_frame()
        elif title == "ZigBee Devices":
            self.create_zigbee_sniffer_frame()
        elif title == "6LoWPAN Devices":
            self.create_sixlowpan_sniffer_frame()

        # adjust row height and column width
        self.master.grid_columnconfigure(0, minsize=100, weight=2)
        self.master.grid_columnconfigure(1, minsize=450, weight=2)
        self.master.grid_rowconfigure(0, weight=1)

    # ====================
    # Home page
    # ====================
    def create_home_frame(self):
        self.home_frame = tk.LabelFrame(
            self.master,
            text="Home pannel",
            font=("Arial", 14),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.RAISED,
            padx=50,
            pady=40,
            background="white",
        )
        self.home_frame.grid(row=0, column=0, sticky="nsew")

        # adjust row height and column width
        self.master.grid_columnconfigure(0, minsize=800, weight=2)
        self.master.grid_rowconfigure(0, weight=1)

        if self.scan_started == False:
            btn_txt = "start scan"
            lb_txt = ""
            cmd = self.start_scan
        elif self.scan_started == True:
            btn_txt = "stop scan"
            lb_txt = ""
            cmd = self.stop_scan
        elif self.scan_started == "scanned":
            btn_txt = "transfert archive"
            lb_txt = "insert your usb drive; It must be wiped in exFat"
            cmd = self.transfert_archive
        elif self.scan_started == "win":
            btn_txt = "[done]"
            lb_txt = ""
            cmd = ""
        elif self.scan_started == "done":
            btn_txt = "[transfert done]"
            lb_txt = "you can withdraw the usb stick"
            cmd = ""
        elif self.scan_started == "win":
            btn_txt = "[done]"
            lb_txt = ""
            cmd = ""
        elif self.scan_started == "E-CI":
            btn_txt = "transfert archive"
            lb_txt = "[Error - command injection in usb name detected]"
            cmd = ""
        elif self.scan_started == "E-NC":
            btn_txt = "transfert archive"
            lb_txt = "[ERROR - not compatible file system, please prefer exfat]"
            cmd = ""

        self.label_start_scan = tk.Label(
            self.home_frame,
            text=lb_txt
        )
        self.label_start_scan.grid(columnspan=2, row=0, column=0, sticky="n")
        
        self.button_start_scan = tk.Button(
            self.home_frame,
            text=btn_txt,
            font=("Arial", 14),
            command=cmd,
            borderwidth=5,
            relief=tk.RAISED,
            padx=5,
            pady=10,
            width=50,
        )
        self.button_start_scan.grid(columnspan=2, row=1, column=0, sticky="n")
        
        self.home_frame_frequences_btn()

        if platform.system() != "Windows":
            self.home_control_btn(row=4)

        self.scan_progressbar.draw_progressbar(self.home_frame, columnspan=2, column=0, row=5)

        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_columnconfigure(1, weight=1)
        self.home_frame.grid_rowconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(1, weight=1)
        self.home_frame.grid_rowconfigure(2, weight=1)
        self.home_frame.grid_rowconfigure(3, weight=1)
        self.home_frame.grid_rowconfigure(4, weight=1)

        if platform.system() != "Windows":
            self.home_frame.grid_rowconfigure(5, weight=1)

    def home_frame_frequences_btn(self):
        buttons_list = [
            self.button_change_page_home,
            self.button_change_page_wifi,
            self.button_change_page_ble,
            self.button_change_page_zigbee,
            self.button_change_page_sixlowpan
        ]

        i = 0
        y = [0,2]
        for element in self.pannels:

            if element != "Home":
                tk.Button(
                    self.home_frame,
                    text=element,
                    font=("Arial", 14),
                    command=buttons_list[i + 1], #to not allocate home button
                    borderwidth=5,
                    relief=tk.RAISED,
                    padx=5,
                    pady=10,
                    width=15,
                ).grid(column=y[0], row=y[1], sticky="n")
                
                i += 1
                y[0] += 1

            if y[0] == 2:
                y[0] = 0
                y[1] += 1

    def home_control_btn(self, row):
        self.button_shutdown = tk.Button(
                self.home_frame,
                text="shutdown",
                font=("Arial", 14),
                command=lambda: os.system("sudo shutdown now"),
                borderwidth=5,
                relief=tk.RAISED,
                padx=5,
                pady=10,
                width=15,
            )
        self.button_shutdown.grid(row=row, column=0, sticky="n")

        self.button_reboot = tk.Button(
                self.home_frame,
                text="reboot",
                font=("Arial", 14),
                command=lambda: os.system("sudo reboot now"),
                borderwidth=5,
                relief=tk.RAISED,
                padx=5,
                pady=10,
                width=15,
            )
        self.button_reboot.grid(row=row, column=1, sticky="n")

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

        # adjust row height and column width
        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)

    def create_commands_frame(self):

        self.commands_frame.grid_columnconfigure(0, weight=1)
        buttons_list = [
            self.button_change_page_home,
            self.button_change_page_wifi,
            self.button_change_page_ble,
            self.button_change_page_zigbee,
            self.button_change_page_sixlowpan
        ]

        i = 0
        for element in self.pannels:
            
            if element != self.current_pannel:
                tk.Button(
                    self.commands_frame,
                    text=element,
                    font=("Arial", 12),
                    command=buttons_list[i],
                    borderwidth=5,
                    relief=tk.RAISED,
                    padx=5,
                    pady=5,
                    width=15,
                ).grid(row=i, column=0, sticky="n")
                self.commands_frame.grid_rowconfigure(i, weight=1)
            
            i += 1

    # ====================
    # WiFi frames
    # ====================
    def create_wifi_sniffer_frame(self):
        # create WiFi devices frame
        self.wifi_devices_frame = tk.LabelFrame(
            self.widget_base_frame,
            text="WiFi Devices",
            font=("Arial", 12),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.wifi_devices_frame.grid(row=0, column=0, sticky="nsew")
        self.create_wifi_devices_frame()

        # create WiFi networks frame
        self.wifi_networks_frame = tk.LabelFrame(
            self.widget_base_frame,
            text="WiFi Networks",
            font=("Arial", 12),
            labelanchor="n",
            foreground="grey",
            borderwidth=5,
            relief=tk.FLAT,
            padx=0,
            pady=5,
            background="white",
        )
        self.wifi_networks_frame.grid(row=1, column=0, sticky="nsew")
        self.create_wifi_networks_frame()

        # adjust row height and column width
        self.widget_base_frame.grid_rowconfigure(0, weight=1)
        self.widget_base_frame.grid_rowconfigure(1, weight=100)
        self.widget_base_frame.grid_columnconfigure(0, weight=1)

    def create_wifi_devices_frame(self):
        # create WiFi device table
        self.wifi_device_scrollable_frame = ScrollFrame(self.wifi_devices_frame)
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
        self.WiFi_sniffer.set_wifi_device_table(self.wifi_device_table)

        try:
            self.display_wifi_device()
        except:
            print("No data found for wifi devices")

    def create_wifi_networks_frame(self):
        # create WiFi network table
        self.wifi_network_scrollable_frame = ScrollFrame(self.wifi_networks_frame)
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

        try:
            self.display_wifi_network()
        except:
            print("No data found for wifi networks")

    def display_wifi_device(self):

        file = open(f"{self.scv_dir}/log_wifi_devices.csv", "r")
        for line in file:

            device = Device(
                address=line.split(";")[0],
                RSSI=line.split(";")[1],
                type=line.split(";")[2],
                timestamp=line.split(";")[3],
                channel=line.split(";")[4],
                name=line.split(";")[5],
                extAddress=line.split(";")[6]
            )

            self.wifi_device_table.add_row(device)

    def display_wifi_network(self):

        file = open(f"{self.scv_dir}/log_wifi_networks.csv", "r")
        for line in file:

            network = Network(
                ID=line.split(";")[0],
                RSSI=line.split(";")[1],
                channel=line.split(";")[2],
                type=line.split(";")[3],
                timestamp=line.split(";")[4],
                BSSID=line.split(";")[5],
            )

            self.wifi_network_table.add_row(network)

    # ====================
    # BLE frames
    # ====================
    def create_ble_sniffer_frame(self):
        # create BLE device table
        self.ble_device_scrollable_frame = ScrollFrame(self.widget_base_frame)
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

        try:
            self.display_ble_data()
        except:
            print("No data found for BLE")

    #call the data in file to display it
    def display_ble_data(self):

        file = open(f"{self.scv_dir}/log_ble.csv", "r")
        for line in file:

            device = Device(
                address=line.split(";")[0],
                RSSI=line.split(";")[1],
                type=line.split(";")[2],
                timestamp=line.split(";")[3],
                channel=line.split(";")[4],
                name=line.split(";")[5],
                extAddress=line.split(";")[6]
            )

            self.ble_device_table.add_row(device)

    # ====================
    # ZigBee frames
    # ====================
    def create_zigbee_sniffer_frame(self):
        # create ZigBee devices frame
        self.zigbee_devices_frame = tk.LabelFrame(
            self.widget_base_frame,
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
        self.zigbee_devices_frame.grid(row=0, column=0, sticky="nsew")
        self.create_zigbee_devices_frame()

        # create ZigBee networks frame
        self.zigbee_networks_frame = tk.LabelFrame(
            self.widget_base_frame,
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
        self.zigbee_networks_frame.grid(row=1, column=0, sticky="nsew")
        self.create_zigbee_networks_frame()

        # adjust row height and column width
        self.widget_base_frame.grid_rowconfigure(0, weight=1)
        self.widget_base_frame.grid_rowconfigure(1, weight=100)
        self.widget_base_frame.grid_columnconfigure(0, weight=1)

    def create_zigbee_devices_frame(self):
        # create ZigBee device table
        self.zigbee_device_scrollable_frame = ScrollFrame(self.zigbee_devices_frame)
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

        try:
            self.display_zigbee_device()
        except:
            print("No data found for zigbee device")

    def create_zigbee_networks_frame(self):
        # create ZigBee network table
        self.zigbee_network_scrollable_frame = ScrollFrame(
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

        try:
            self.display_zigbee_network()
        except:
            print("No data found for zigbee networks")

    def display_zigbee_device(self):

        file = open(f"{self.scv_dir}/log_zigbee_device.csv", "r")
        for line in file:

            device = Device(
                address=line.split(";")[0],
                RSSI=line.split(";")[1],
                type=line.split(";")[2],
                timestamp=line.split(";")[3],
                channel=line.split(";")[4],
                name=line.split(";")[5],
                extAddress=line.split(";")[6]
            )

            self.zigbee_device_table.add_row(device)

    def display_zigbee_network(self):

        file = open(f"{self.scv_dir}/log_zigbee_networks.csv", "r")
        for line in file:

            network = Network(
                ID=line.split(";")[0],
                RSSI=line.split(";")[1],
                channel=line.split(";")[2],
                type=line.split(";")[3],
                timestamp=line.split(";")[4]
            )

            self.zigbee_network_table.add_row(network)

    # ====================
    # 6LoWPAN frames
    # ====================
    def create_sixlowpan_sniffer_frame(self):
        # create BLE device table
        self.sixlowpan_device_scrollable_frame = ScrollFrame(
            self.widget_base_frame
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

        try:
            self.display_sixlowpan()
        except:
            print("No data found for 6loWpan")

    def display_sixlowpan(self):

        file = open(f"{self.scv_dir}/log_zigbee_device.csv", "r")
        for line in file:

            device = Device(
                address=line.split(";")[0],
                RSSI=line.split(";")[1],
                type=line.split(";")[2],
                timestamp=line.split(";")[3],
                channel=line.split(";")[4],
                #name=line.split(";")[5]
            )
        
        self.sixlowpan_device_table.add_row(device)

    # ====================
    # Buttons functions
    # ====================
    def start_scan(self):
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

        #start a thread for the progress bar. The progress is calculate on Zigbee scan
        self.scan_progressbar.start(
            self.ZigBee_sniffer,
            self.zigbee_scan_start,
            self.zigbee_scan_end
        )

        self.scan_started = True
        self.button_start_scan['text'] = "stop scan"
        self.button_start_scan['command'] = self.stop_scan
        self.home_frame.update_idletasks()

    def stop_scan(self):
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

        if platform.system() != "Windows":
            #compress the files to an archive and delete old files
            compress_data = Compress(self.scv_dir)
            compress_data.launch()

            self.scan_started = "scanned"
            self.button_start_scan['text'] = "transfert archive"
            self.label_start_scan['text'] = "insert your usb drive; It must be wiped in exFat"
            self.button_start_scan['command'] = self.transfert_archive
        else:
            self.scan_started = "win"
            self.button_start_scan['text'] = "[done]"
            self.button_start_scan['command'] = ""

        self.home_frame.update_idletasks()

    def transfert_archive(self):
        file_sys = self.check_usb_drive()

        if(file_sys == 0):
            #copy the last archive onto the usb drive detected
            os.system("tmp=$(lsblk | grep sda1); file=$(ls -l /home/$(whoami)/Desktop/IOTScanner/archives/ | tail -1 | awk '{print $9}'); cp /home/$(whoami)/Desktop/IOTScanner/archives/$file $(echo $tmp | awk '{print $7}')/$file")
            
            #eject usb drive
            os.system("tmp=$(lsblk | grep sda1); sudo umount $(echo $tmp | awk '{print $7}')")

            self.scan_started = "done"
            self.label_start_scan['text'] = "you can withdraw the usb stick"
            self.button_start_scan['text'] = "[transfert done]"
            self.button_start_scan['command'] = ""
            self.home_frame.update_idletasks()

    def check_usb_drive(self):
        btn_txt = self.button_start_scan['text']

        self.button_start_scan['text'] = ""
        self.label_start_scan['text'] = "check for command injection by usb name"
        self.home_frame.update_idletasks()

        #Security for command forged on usb drive name
        proc = subprocess.run(["tmp=$(lsblk | grep sda1); echo $tmp | awk '{print $7}'"], shell=True, capture_output=True, text=True)
        proc = str(proc.stdout).split("\n")[0].split("/")[-1]

        if(";" in proc):
            self.scan_started = "E-CI"
            self.button_start_scan['text'] = btn_txt
            self.label_start_scan['text'] = "[Error - command injection by usb name detected]"
            self.home_frame.update_idletasks()
            return 1
        
        self.button_start_scan['text'] = ""
        self.label_start_scan['text'] = "check for usb file"
        self.home_frame.update_idletasks()

        file_sys = subprocess.run(["tmp=$(lsblk -f | grep sda1); echo $tmp | awk '{print $2}'"], shell=True, capture_output=True, text=True)
        file_sys = str(file_sys.stdout).split("\n")[0]

        if(file_sys in self.allowed_file_sys_for_usb_key):
            return 0
        else:
            self.scan_started = "E-NC"
            self.button_start_scan['text'] = btn_txt
            self.label_start_scan['text'] = "[ERROR - not compatible file system, please prefer exfat]"
            self.home_frame.update_idletasks()
            return 1

    def button_change_page_home(self):
        self.change_screen(0)

    def button_change_page_wifi(self):
        self.change_screen(1)

    def button_change_page_ble(self):
        self.change_screen(2)

    def button_change_page_zigbee(self):
        self.change_screen(3)

    def button_change_page_sixlowpan(self):
        self.change_screen(4)
    
    def change_screen(self, pannel):

        if self.current_pannel == "Home":
            self.home_frame.grid_forget()
        else:
            self.widget_base_frame.grid_forget()
        
        self.current_pannel = self.pannels[pannel]
        self.call_frequence_widget(self.current_pannel)

    # ====================
    # Seized Devices call back functions
    # ====================
    def add_seized_device_row(self, device):
        self.logger.debug(f"{device.__repr__()} seized")
        self.seized_devices.add(device.key)  # Add device to the set of seized devices
        #self.seized_device_table.add_row(device)
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
        if os.path.isfile(f"{self.scv_dir}/log_wifi_networks.csv") == False:
            self.csv_file.write_csv_header(f"{self.scv_dir}/log_wifi_networks.csv", self.fields_wifi_networks)
            print("create file")

        self.csv_file.write_csv_line(f"{self.scv_dir}/log_wifi_networks.csv", self.fields_wifi_networks, network)

    def update_wifi_network_row(self, key, field, value):
        #Only display the update if the screen is displayed
        #Must be updated to update the log file directly
        try:
            self.wifi_network_table.update_row(key, field, value)
        except:
            pass

    def remove_wifi_network_row(self, key):
        #self.wifi_network_table.remove_row(key)
        print(key)

    def add_wifi_device_row(self, device):
        if device.key in self.seized_devices:
            pass
        else:
            if os.path.isfile(f"{self.scv_dir}/log_wifi_devices.csv") == False:
                self.csv_file.write_csv_header(f"{self.scv_dir}/log_wifi_devices.csv", self.fields_wifi_devices)
                print("create file")

            self.csv_file.write_csv_line(f"{self.scv_dir}/log_wifi_devices.csv", self.fields_wifi_devices, device)

    def update_wifi_device_row(self, key, field, value):
        #Only display the update if the screen is displayed
        #Must be updated to update the log file directly
        try:
            if key in self.seized_devices:
                pass
            else:
                self.wifi_device_table.update_row(key, field, value)
        except:
            pass

    def remove_wifi_device_row(self, key):
        #self.wifi_device_table.remove_row(key)
        print(key)

    # ====================
    # BLE call back functions
    # ====================
    def add_ble_device_row(self, device):
        if device.key in self.seized_devices:
            pass
        else:
            if os.path.isfile(f"{self.scv_dir}/log_ble.csv") == False:
                self.csv_file.write_csv_header(f"{self.scv_dir}/log_ble.csv", self.fields_ble)
                print("create file")

            self.csv_file.write_csv_line(f"{self.scv_dir}/log_ble.csv", self.fields_ble, device)

    def update_ble_device_row(self, key, field, value):
        #Only display the update if the screen is displayed
        #Must be updated to update the log file directly
        try:
            if key in self.seized_devices:
                pass
            else:
                self.ble_device_table.update_row(key, field, value)
        except:
            pass

    def remove_ble_device_row(self, key):
        print(key)
        #CSV.write_csv_line("save/log_ble.csv", self.fields, device)

    # ====================
    # ZigBee Call back functions
    # ====================
    def add_zigbee_network_row(self, network):
        if os.path.isfile(f"{self.scv_dir}/log_zigbee_networks.csv") == False:
            self.csv_file.write_csv_header(f"{self.scv_dir}/log_zigbee_networks.csv", self.fields_zigbee_networks)
            print("create file")

        self.csv_file.write_csv_line(f"{self.scv_dir}/log_zigbee_networks.csv", self.fields_zigbee_networks, network)

    def update_zigbee_network_row(self, key, field, value):
        #Only display the update if the screen is displayed
        #Must be updated to update the log file directly
        try:
            self.zigbee_network_table.update_row(key, field, value)
        except:
            pass

    def remove_zigbee_network_row(self, key):
        print(key)
        #self.zigbee_network_table.remove_row(key)

    def add_zigbee_device_row(self, device):
        if os.path.isfile(f"{self.scv_dir}/log_zigbee_device.csv") == False:
            self.csv_file.write_csv_header(f"{self.scv_dir}/log_zigbee_device.csv", self.fields_zigbee_devices)
            print("create file")

        self.csv_file.write_csv_line(f"{self.scv_dir}/log_zigbee_device.csv", self.fields_zigbee_devices, device)

    def update_zigbee_device_row(self, key, field, value):
        try:
            if key in self.seized_devices:
                pass
            else:
                self.zigbee_device_table.update_row(key, field, value)
        except:
            pass

    def remove_zigbee_device_row(self, key):
        print(key)
        #self.zigbee_device_table.remove_row(key)

    # ====================
    # 6LoWPAN call back functions
    # ====================
    def add_sixlowpan_device_row(self, device):
        if os.path.isfile(f"{self.scv_dir}/log_sixlowpan.csv") == False:
            self.csv_file.write_csv_header(f"{self.scv_dir}/log_sixlowpan.csv", self.fields_sixlowpan)
            print("create file")

        self.csv_file.write_csv_line(f"{self.scv_dir}/log_sixlowpan.csv", self.fields_sixlowpan, device)

    def update_sixlowpan_device_row(self, key, field, value):
        try:
            if key in self.seized_devices:
                pass
            else:
                self.sixlowpan_device_table.update_row(key, field, value)
        except:
            pass

    def remove_sixlowpan_device_row(self, key):
        print(key)
        #self.sixlowpan_device_table.remove_row(key)
