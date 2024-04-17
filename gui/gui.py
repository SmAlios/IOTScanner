import tkinter as tk
from tkinter.ttk import Progressbar, Style
import os, subprocess
from devices.csv import CSV
from devices.device import Device
from devices.network import Network
from gui.scrollable_frame import ScrollFrame
from gui.network_gui import NetworkTable
from gui.device_gui import DeviceTable
from logs.logger import logger
from devices.compress import Compress
from time import sleep
import platform
import threading

# Thread made to run a progressbar, it must start when home page's "start scan" button is pressed
# until ZigBee scan is complite or scan is stopped.

class Myprogressbar(threading.Thread):
    def __init__(self, master_gui):
        super().__init__(daemon=True)
        self.value = 0
        self.running = False
        self.already_start = False
        self.master_gui = master_gui

    # Display the progressbar on home page
    def draw_progressbar(self, master, columnspan, row, column):
        self.master = master

        # Set a style to the progressbar
        self.style = Style()
        self.style.layout(
            'text.Horizontal.TProgressbar',
            [
                (
                    'Horizontal.Progressbar.trough', 
                    {'children':
                        [
                            ('Horizontal.Progressbar.pbar',
                                {
                                    'side': 'left',
                                    'sticky': 'ns'
                                }
                            )
                        ],
                        'sticky': 'nswe'
                    }
                ),
                (
                    'Horizontal.Progressbar.label',
                    {'sticky': 'nswe'}
                )
            ]
        )
        
        # Add a text on center of the progressbar to display the purcentage of scan
        self.style.configure('text.Horizontal.TProgressbar', text=f"{self.value} %", anchor='center', foreground='black', background='green')

        # Display a label on top of the progressbar
        self.progressbar_label= tk.Label(
            self.master,
            text="Click on start to begin the scan"
        )
        self.progressbar_label.grid(columnspan=columnspan, row=row, column=column, sticky="n")

        # Display the progressbar
        self.progressbar = Progressbar(
            self.master,
            cursor="spider",
            style="text.Horizontal.TProgressbar",
            orient='horizontal',
            length=520,
            mode='determinate'
        )
        self.progressbar.grid(columnspan=columnspan, row=(row + 1), column=column, sticky="n")

        # When navigating between tabs and returning to home page, the class is reload.
        # To prevent the progress bar and it messages to return to the starting configuration,
        # the progressbar progression is saved and load on class reload.
        if self.value > 0:
            self.progressbar['value'] = self.value

        if self.value == 0 and self.running == False: 
            self.progressbar_label["text"] = "Scan ready to start"
        elif self.value > 0 and self.value < 100 and self.running == True:
            self.progressbar_label["text"] = "Scan in progress, it's slow and should take some minutes ..."
        elif self.value >= 100 and self.running == False:
            self.progressbar_label["text"] = "Scan is complete, antennas continue to perform background"
        elif self.master_gui.scan_stop_signal and self.running == False:
            self.progressbar_label["text"] = "Scan stopped, antennas do no perform anymore"
        else:
            self.progressbar_label["text"] = "Error - case of use not known"

    def start(self, get_value, scan_start_value, scan_end_value):
        self.get_value = get_value
        self.scan_start_value = scan_start_value
        self.scan_end_value = scan_end_value
        self.already_start = True
        self.running = True
        super().start()

    def stop(self):
        self.progressbar_label["text"] = "Scan stopped, antennas do no perform anymore"
        self.master.update_idletasks()

        self.running = False
        daemon=False

    def run(self):
        # Progressbar's label is updated at scan start
        # update_idletask is used to refresh screen
        self.progressbar_label["text"] = "Scan in progress, it's slow and should take some minutes ..."
        self.master.update_idletasks()

        while self.running:

            # Get progress of the Zigbee scan
            get_value = self.get_value.get_progressbar_value()

            # Convert value to a purcentage
            self.value = get_value * (100 / (self.scan_end_value - self.scan_start_value))

            # Update the text into the progressbar
            self.progressbar['value'] = self.value
            self.style.configure('text.Horizontal.TProgressbar', text=f"{self.value} %")
            self.master.update_idletasks()

            sleep(1)

            # Stop condition of the progressbar
            if self.value >= 100:
                self.value = 100
                self.running = False

        # Update progressbar's label value
        print("Stopping progressbar thread ...")
        self.progressbar_label["text"] = "Scan is complete, antennas continue to perform background"
        self.master.update_idletasks()

        # Stop thread
        self.stop()


class GUI:
    def __init__(self, master, BLE_sniffer, WiFi_sniffer, ZigBee_sniffer, current_pannel = 0):
        self.logger = logger  # configure logger
        self.master = master
        self.BLE_sniffer = BLE_sniffer
        self.WiFi_sniffer = WiFi_sniffer
        self.ZigBee_sniffer = ZigBee_sniffer
        self.seized_devices = set()

        # Zigbee scan start at channel 11 and stop at channel 27
        self.zigbee_scan_start = 11
        self.zigbee_scan_progress = 0
        self.zigbee_scan_end = 27

        self.scan_progressbar = Myprogressbar(self)
        self.scv_dir = "csv_dir"
        self.csv_file = CSV("csv_dir")

        self.allowed_file_sys_for_usb_key = ["exfat", "fat32", "ntfs", "ext", "ext4"]

        self.scan_started = False
        self.scan_stop_signal = False

        # Delete old csv files if not done the last time
        Compress(self.scv_dir).delete_old_files()

        # List of possibles pannels and page is curently displayed / must be displayed
        self.pannels = ["Home","WiFi","BLE","Zigbee","6loWPAN"]
        self.current_pannel = self.pannels[current_pannel]
        self.call_frequence_widget(self.current_pannel)

    # ====================
    # Base structure
    # ====================

    # Build the page on screen based on the page/protocol given in parameters
    def call_frequence_widget(self, protocol):
        
        if protocol == "WiFi":
            title = "WiFi Sniffer"
        elif protocol == "BLE":
            title = "BLE Devices"
        elif protocol == "Zigbee":
            title = "ZigBee Devices"
        elif protocol == "SixloWPAN":
            title = "SixloWPAN Devices"
        elif protocol == "Home":
            self.create_home_frame()


        if protocol != "Home":
            self.create_frequence_widget(title) 

    # Build the base frame and call the selected protocol
    def create_frequence_widget(self, title):
        # Build a control pannel on the left
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

        # Build a pannel for the scan result on the right
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

        # Call the scpecific build for the selected protocol
        if title == "WiFi Sniffer":
            self.create_wifi_sniffer_frame()
        elif title == "BLE Devices":
            self.create_ble_sniffer_frame()
        elif title == "ZigBee Devices":
            self.create_zigbee_sniffer_frame()
        elif title == "6LoWPAN Devices":
            self.create_sixlowpan_sniffer_frame()

        # Adjust row height and column width
        self.master.grid_columnconfigure(0, minsize=100, weight=2)
        self.master.grid_columnconfigure(1, minsize=450, weight=2)
        self.master.grid_rowconfigure(0, weight=1)

    # ====================
    # Home page
    # ====================
    
    # Build the home page
    def create_home_frame(self):
        # Build the base frame
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

        # Display the main button based on the procedure progress
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

        # Display a text to help the user to understand what to do
        self.label_start_scan = tk.Label(
            self.home_frame,
            text=lb_txt
        )
        self.label_start_scan.grid(columnspan=2, row=0, column=0, sticky="n")
        
        # Nuild the button
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
        
        # Loop who display each protocol's button
        self.home_frame_frequences_btn()

        if platform.system() != "Windows":
            self.home_control_btn(row=4)

        # Display the progressbar
        self.scan_progressbar.draw_progressbar(self.home_frame, columnspan=2, column=0, row=5)

        # Set the grid for the called elements
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_columnconfigure(1, weight=1)
        self.home_frame.grid_rowconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(1, weight=1)

        if platform.system() != "Windows":
            self.home_frame.grid_rowconfigure(5, weight=1)

    # Display the buttons according the list "self.pannels"
    def home_frame_frequences_btn(self):

        # The home screen use two columns to display each protocol's button.
        # Buttons are displayed by a loop. To set their position on x and y  axis, the
        # variable y is composed of the two values. So y[0] represent the y axis and y[1] the x one

        i = 0
        y = [0,2]
        for element in self.pannels:

            # Display a button for each protocol and escape an home button
            if element != "Home":
                tk.Button(
                    self.home_frame,
                    text=element,
                    font=("Arial", 14),

                    # +1 to not allocate home button, this is a function who'll automatically set
                    # the good parameters. This function and it parameter'll be called if the button is clicked
                    command=lambda n=(i + 1) : self.change_screen(n),
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

            
            # Set the grid according to the number of buttons called
            self.home_frame.grid_rowconfigure(y[1], weight=1)

    # Display a first button "shutdown" and a second "reboot"
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
    # Command frame on left
    # ====================

    # On a protocol page, build a control pannel on the left
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
        self.display_buttons_of_control_frame()

        # adjust row height and column width
        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)

    # Display buttons on the control frame
    def display_buttons_of_control_frame(self):
        self.commands_frame.grid_columnconfigure(0, weight=1)

        i = 0
        for element in self.pannels:
            
            if element != self.current_pannel:
                tk.Button(
                    self.commands_frame,
                    text=element,
                    font=("Arial", 12),
                    command=lambda n=i : self.change_screen(n),
                    borderwidth=5,
                    relief=tk.RAISED,
                    padx=5,
                    pady=5,
                    width=15,
                ).grid(row=i, column=0, sticky="n")
                self.commands_frame.grid_rowconfigure(i, weight=1)
            
            i += 1

    # ====================
    # Build protocol's table on right
    # ====================
    
    # Based on the protocol and if it must display devices or networks,
    # build the table/s of the selected protocol
    def create_sniffer(self, master, net_or_dev, frequence, sniffer):
        # Create scrollable table
        self.scrollable_frame = ScrollFrame(master)
        self.scrollable_frame.pack(side="top", fill="both", expand=True)

        i = 1

        # Create table heading
        tk.Label(self.scrollable_frame.item_frame, text="RSSI").grid(
            row=0, column=i, sticky="nsew"
        )
        i+=1

        if(net_or_dev == "network"):
            tk.Label(self.scrollable_frame.item_frame, text="Channel").grid(
                row=0, column=i, sticky="nsew"
            )
            i+=1

            if(frequence == "wifi"):
                tk.Label(self.scrollable_frame.item_frame, text="SSID").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1
                
                tk.Label(self.scrollable_frame.item_frame, text="BSSID").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1
            if(frequence == "zigbee"):
                tk.Label(self.scrollable_frame.item_frame, text="PAN ID").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1

        elif(net_or_dev == "devices"):

            if(frequence == "wifi" or frequence == "sixlowpan"):
                tk.Label(self.scrollable_frame.item_frame, text="Channel").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1

                tk.Label(self.scrollable_frame.item_frame, text="Address").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1

            elif(frequence == "ble"):
                tk.Label(self.scrollable_frame.item_frame, text="Address").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1

                tk.Label(self.scrollable_frame.item_frame, text="Name").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1
            elif(frequence == "zigbee"):
                tk.Label(self.scrollable_frame.item_frame, text="Channel").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1

                tk.Label(self.scrollable_frame.item_frame, text="Address").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1

                tk.Label(self.scrollable_frame.item_frame, text="Full Address").grid(
                    row=0, column=i, sticky="nsew"
                )
                i+=1
            
        tk.Label(self.scrollable_frame.item_frame, text="Updated").grid(
            row=0, column=i, sticky="nsew"
        )
        i+=1

        if(net_or_dev == 'devices'):
            tk.Label(self.scrollable_frame.item_frame, text="Action").grid(
                row=0, column=i, sticky="nsew"
            )

        # Some protocols need diferents weight value to display well
        if(frequence == "wifi"):
            table_settings = [1,1,1,3,3,3]
        elif(frequence == "ble"):
            table_settings = [1,1,1,1,1,1]
        elif(frequence == "zigbee" and net_or_dev == "devices"):
            table_settings = [1,1,1,1,2,2,2]
        elif(frequence == "zigbee" and net_or_dev == "network"):
            table_settings = [1,1,1,1,2]
        elif(frequence == "sixlowpan"):
            table_settings = [1,1,1,1,1,1]

        # Set some setting based on protocole
        i = 0
        for element in table_settings:
            if(frequence == "ble" or frequence == "sixlowpan"):
                padding = 1
            else:
                padding = 5

            self.scrollable_frame.item_frame.columnconfigure(
                index=i, weight=element, pad=padding
            )

            i+= 1

        # Set a network if selected in parameters
        if(net_or_dev == "network"):
            self.network_table = NetworkTable(
                self.scrollable_frame.item_frame,
                sniffer,
                self.device_table,
            )

            # Prevent a software crash if trying to open a page while no logs have been created for
            try:
                self.display_network(frequence)
            except:
                print(f"No data found for {frequence} {net_or_dev}")

        # Set a device if selected in parameters
        elif(net_or_dev == "devices"):
            self.device_table = DeviceTable(
                self.scrollable_frame.item_frame, 
                self.add_seized_device_row
            )

            # Prevent a software crash if trying to open a page while no logs have been created for
            try:
                self.display_device(frequence)
            except:
                print(f"No data found for {frequence} {net_or_dev}")

    # Load logs created by gathering data from scan and display it (for devices)
    def display_device(self, freq):
        i = 0
        file = open(f"{self.scv_dir}/log_{freq}_devices.csv", "r")
        for line in file:

            line = line.split(";")

            # Fifth and sixth value for certain protocols could be empty.
            # If it's the case, a value is set to prevent crash
            try:
                line[5] == "test"
            except:
                #None is the default value if not set
                line.append(None)

            try:
                line[6] == "test"
            except:
                #None is the default value if not set
                line.append(None)

            if(i != 0):
                device = Device(
                    address=line[0],
                    RSSI=line[1],
                    type=line[2],
                    timestamp=line[3],
                    channel=line[4],
                    name=line[5],
                    extAddress=line[6]
                )

                self.device_table.add_row(device)

            i+= 1

    # Load logs created by gathering data from scan and display it (for networks)
    def display_network(self, freq):
        i = 0
        file = open(f"{self.scv_dir}/log_{freq}_network.csv", "r")
        for line in file:

            line = line.split(";")

            # Fifth value for certain protocols could be empty.
            # If it's the case, a value is set to prevent crash
            try:
                line[5] == "test"
            except:
                #None is the default value if not set
                line.append(None)

            if(i != 0):
                network = Network(
                    ID=line[0],
                    RSSI=line[1],
                    channel=line[2],
                    type=line[3],
                    timestamp=line[4],
                    BSSID=line[5],
                )

                self.network_table.add_row(network)

            i+= 1

    # ====================
    # Frequences frames
    # ====================

    # Build the frame used to display wifi's data
    def create_wifi_sniffer_frame(self):
        # Create WiFi devices frame
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

        self.create_sniffer(
            master=self.wifi_devices_frame,
            net_or_dev="devices",
            frequence="wifi",
            sniffer=self.WiFi_sniffer
        )

        # Create WiFi networks frame
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

        self.create_sniffer(
            master=self.wifi_networks_frame,
            net_or_dev="network",
            frequence="wifi",
            sniffer=self.WiFi_sniffer
        )

        # Adjust row height and column width
        self.widget_base_frame.grid_rowconfigure(0, weight=1)
        self.widget_base_frame.grid_rowconfigure(1, weight=100)
        self.widget_base_frame.grid_columnconfigure(0, weight=1)

    # Build the frame used to display BLE's data
    def create_ble_sniffer_frame(self):
        # Because this protocol only need one table, the configuration is minimal
        self.create_sniffer(
            master=self.widget_base_frame,
            net_or_dev="devices",
            frequence="ble",
            sniffer=self.BLE_sniffer
        )

    # Build the frame used to display ZigBee's data
    def create_zigbee_sniffer_frame(self):
        # Create ZigBee devices frame
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

        self.create_sniffer(
            master=self.zigbee_devices_frame,
            net_or_dev="devices",
            frequence="zigbee",
            sniffer=self.ZigBee_sniffer
        )

        # Create ZigBee networks frame
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

        self.create_sniffer(
            master=self.zigbee_networks_frame,
            net_or_dev="network",
            frequence="zigbee",
            sniffer=self.ZigBee_sniffer
        )

        # Adjust row height and column width
        self.widget_base_frame.grid_rowconfigure(0, weight=1)
        self.widget_base_frame.grid_rowconfigure(1, weight=100)
        self.widget_base_frame.grid_columnconfigure(0, weight=1)

    # Build the frame used to display sixlowpan's data
    def create_sixlowpan_sniffer_frame(self):
        # Because this protocol only need one table, the configuration is minimal
        self.create_sniffer(
            master=self.widget_base_frame,
            net_or_dev="devices",
            frequence="sixlowpan",
            sniffer=self.ZigBee_sniffer
        )

    # ====================
    # Buttons functions
    # ====================

    # Well, ... start the scan
    # More seriously, it start the scan on each protocols set in the
    # function (if the right antennas are connected)
    def start_scan(self):
        self.logger.debug("Start clicked")
        try:
            self.BLE_sniffer.start(
                self.add_data_row, 
                self.update_data_row,
                self.remove_data_row,
            )
        except Exception as e:
            self.logger.error(f"Error while starting scan of BLESniffer: {e}")

        try:
            self.WiFi_sniffer.start(
                self.add_data_row,
                self.update_data_row,
                self.remove_data_row,
            )

        except Exception as e:
            self.logger.error(f"Error while starting scan of WiFiSniffer: {e}")

        try:
            self.ZigBee_sniffer.start(
                self.add_data_row,
                self.update_data_row,
                self.remove_data_row,
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

        # Update the main home page's button
        self.button_start_scan['text'] = "stop scan"
        self.button_start_scan['command'] = self.stop_scan
        self.home_frame.update_idletasks()

    # Logically, it could stop it
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

        self.scan_progressbar.stop()
        self.scan_stop_signal = True

        # If the system used is Linux, compress the logs and propose to send it on an USB stick
        if platform.system() != "Windows":
            # Compress the files to an archive and delete old files
            # Is only proposed to Linux users because it use Linux commands, and also because Linux is better
            compress_data = Compress(self.scv_dir)
            compress_data.launch()

            # Update home page's button and text
            self.scan_started = "scanned"
            self.button_start_scan['text'] = "transfert archive"
            self.label_start_scan['text'] = "insert your usb drive; It must be wiped in exFat"
            self.button_start_scan['command'] = self.transfert_archive
        else:
            self.scan_started = "win"
            self.button_start_scan['text'] = "[done]"
            self.button_start_scan['command'] = ""

        self.home_frame.update_idletasks()

    # ====================
    # utils
    # ====================

    # Send the archive created with logs to an USB stick
    def transfert_archive(self):
        # security and compatibility check (must return 0)
        file_sys = self.check_usb_drive()

        if(file_sys == 0):
            # Copy the last archive created onto the usb drive detected
            os.system("tmp=$(lsblk | grep sda1); file=$(ls -l /home/$(whoami)/Desktop/IOTScanner/archives/ | tail -1 | awk '{print $9}'); sudo cp /home/$(whoami)/Desktop/IOTScanner/archives/$file $(echo $tmp | awk '{print $7}')/$file")
            
            # Eject usb drive
            os.system("tmp=$(lsblk | grep sda1); sudo umount $(echo $tmp | awk '{print $7}')")

            # Update home page's button and text
            self.scan_started = "done"
            self.label_start_scan['text'] = "you can withdraw the usb stick"
            self.button_start_scan['text'] = "[transfert done]"
            self.button_start_scan['command'] = ""
            self.home_frame.update_idletasks()

    # Security and compatibility check of the USB drive
    def check_usb_drive(self):
        # Save and the home page's button 
        btn_txt = self.button_start_scan['text']

        self.button_start_scan['text'] = ""
        self.label_start_scan['text'] = "check for command injection by usb name"
        self.home_frame.update_idletasks()

        # By purpose of security, an USB drive named with ";" is rejected.
        # Hacking technics constantely improve. It could be possible that an USB drive's name is 
        # forged to hide a Linux command like this :
        #
        #                   my_usb_stick;git clone my_virus.sh;chmod +x my_virus.sh;./my_virus.sh
        #
        # This fonction, include a detection of this ecurity breach
        
        # Security for command forged on usb drive name
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

        # Detect the USB stick file system and if it's readable/writeable
        file_sys = subprocess.run(["tmp=$(lsblk -f | grep sda1); echo $tmp | awk '{print $2}'"], shell=True, capture_output=True, text=True)
        file_sys = str(file_sys.stdout).split("\n")[0]

        if(file_sys in self.allowed_file_sys_for_usb_key):
            print(file_sys)
            return 0
        else:
            self.scan_started = "E-NC"
            self.button_start_scan['text'] = btn_txt
            self.label_start_scan['text'] = "[ERROR - not compatible file system, please prefer exfat]"
            self.home_frame.update_idletasks()
            return 1
    
    # Function called to switch between current and next page
    def change_screen(self, pannel):

        if self.current_pannel == "Home":
            self.home_frame.grid_forget()
        else:
            self.widget_base_frame.grid_forget()
        
        self.current_pannel = self.pannels[pannel]
        self.call_frequence_widget(self.current_pannel)

    # ====================
    # Call back functions
    # ====================

    # Add a device to the sized devices list
    def add_seized_device_row(self, device):
        self.logger.debug(f"{device.__repr__()} seized")
        self.seized_devices.add(device.key)  
        
        if device.type == "WiFi-2.4GHz":
            self.device_table.remove_row(device.key)
        elif device.type == "BLE":
            self.device_table.remove_row(device.key)
        elif device.type == "ZigBee":
            self.device_table.remove_row(device.key)
        elif device.type == "6LoWPAN":
            self.device_table.remove_row(device.key)

    # Add data to a specific protocol table
    def add_data_row(self, data, protocol, net_or_dev):

        # Get the right list of fields for the protocol scanned
        if(net_or_dev == "network"):
            if(protocol == "wifi"):
                fields = ["ID", "RSSI", "channel", "type", "timestamp", "BSSID"]
            elif(protocol == "zigbee"):
                fields = ["ID", "RSSI", "channel", "type", "timestamp"]
        elif(net_or_dev == "devices"):
            if(protocol == "ble" or protocol == "wifi"):
                fields = ["address", "RSSI", "type", "timestamp", "channel", "name", "extAddress"]
            elif(protocol == "zigbee"):
                fields = ["address", "name", "RSSI", "type", "channel", "extAddress", "timestamp"]
            elif(protocol == "sixlowpan"):
                fields = ["address", "name", "RSSI", "type", "channel", "timestamp"]

        if(net_or_dev == "devices"):
            if(data.key in self.seized_devices):
                return 0

        # Check if log file already exist. If it exist, add the data to it
        if os.path.isfile(f"{self.scv_dir}/log_{protocol}_{net_or_dev}.csv") == False:
            self.csv_file.write_csv_header(f"{self.scv_dir}/log_{protocol}_{net_or_dev}.csv", fields)
            print(f"create log_{protocol}_{net_or_dev}.csv file")

        self.csv_file.write_csv_line(f"{self.scv_dir}/log_{protocol}_{net_or_dev}.csv", fields, data)   

    # Update the data displayed on the current page's table/s
    def update_data_row(self, key, field, value, protocol, net_or_dev):
        # Only display the update if the right page is on screen
        if(self.current_pannel.lower() == protocol):
            if(key not in self.seized_devices):
                if(net_or_dev == "network"):
                    try:
                        self.network_table.update_row(key, field, value)
                    except:
                        pass
                elif(net_or_dev == "devices"):
                    try:
                        self.device_table.update_row(key, field, value)
                    except:
                        pass
                else:
                    print(f"{key}, {field}, {value}, {protocol}, {net_or_dev}")

    # Remove the selected data (functionality exist but is currently not used)
    def remove_data_row(self, key, net_or_dev):
        #if(net_or_dev == "devices"):
        #    self.network_table.remove_row(key)
        #else:
        #    self.device_table.remove_row(key)

        print(key)
