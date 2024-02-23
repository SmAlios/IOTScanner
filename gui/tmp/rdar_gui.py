import tkinter as tk
from tkinter import ttk
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

        self.iotItems_list = {}

    def create_widgets(self):
        self.base_screen = tk.Frame(self.master)
        self.base_screen.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.radar_frame()
        self.control_panel_frame()

    def radar_frame(self):
        #self.paned_window = tk.PanedWindow(self.base_screen, orient=tk.VERTICAL, width=500, background='#3399ff')
        #self.paned_window.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.base_screen, background='#3399ff', height=500)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def control_panel_frame(self):
        self.label_frame = tk.LabelFrame(self.base_screen, text="control panel", width=300)
        self.label_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        #contenu de la LabelFrame
        self.start_button = tk.Button(self.label_frame, text="start", command=self.on_start_click)
        self.start_button.pack(padx=20, pady=20, fill=tk.X)

        self.stop_button = tk.Button(self.label_frame, text="stop", command=self.on_stop_click)
        self.stop_button.pack(padx=20, pady=10, fill=tk.X)

        br = tk.Label(self.label_frame, text="").pack(pady=10)

        self.prog_bar_label = tk.Label(self.label_frame)
        self.prog_bar_label.config(text='<status : x%>')
        self.prog_bar_label.pack()

        self.prog_bar = ttk.Progressbar(self.label_frame, orient='horizontal', mode='indeterminate', length=160)
        self.prog_bar.pack()

        br = tk.Label(self.label_frame, text="").pack(pady=10)

        self.nbr_devices_detected = tk.Label(self.label_frame)
        self.nbr_devices_detected.config(text='nbr detected devices : \n <x>')
        self.nbr_devices_detected.pack()


    def on_start_click(self):
        self.logger.debug("Start clicked")
        try:
            self.BLE_sniffer.start(
                self.add_ble_device,
                self.update_ble_device,
                self.remove_ble_device,
            )
        except Exception as e:
            self.logger.error(f"Error while starting scan of BLESniffer: {e}")

    def on_stop_click(self):
        self.logger.debug("Stop clicked")
        # stop reader threads when button clicked
        try:
            self.BLE_sniffer.stop()
        except Exception as e:
            self.logger.error(f"Error while stoping scan of {self.BLE_sniffer}: {e}")


    #==========================================
    #           BLE callback func
    #==========================================
    
    BLE_radar_pos = [5, 5, 30, 30]
    def add_ble_device(self, device):

        #print(f"add => {device.address}")

        already_known_ble = [
            "d2:94:9d:8c:ab:22",
            "16:6c:6e:d:2e:e2",
            "24:49:52:f9:1f:45",
            "39:23:60:d1:8d:97",
            "1a:1:89:d7:6e:5d",
            "4e:9b:98:c2:6:c6",
            "4a:78:f:eb:e:fa",
            "35:1:f8:35:73:38",
            "1d:26:8d:4f:dc:d4",
            "73:11:48:b8:ee:c2",
            "6c:c:ee:4c:a4:48",
            "f:ab:8f:9b:a9:4",
            "0:8d:d4:30:6c:a2",
            "3b:8:d2:7f:f4:7",
            "d:7b:fc:69:2c:66",
            "71:66:47:d0:c0:45",
            "9:0:5d:e5:fd:54",
            "53:b5:41:3e:29:39",
            "74:73:57:d7:eb:8c",
            "d9:86:48:d2:5a:d8",
            "e:9:e2:a6:3a:a9",
            "7:8d:3c:e3:a9:73",
            "65:ec:88:c4:7c:ad",
            "ef:64:9d:d4:6d:3d",
            "6a:8a:48:ee:f1:65",
            "c:f:e4:26:83:1b",
            "5f:90:cd:f1:7b:2e",
            "29:49:da:8d:92:1e",
            "49:e3:7c:ee:77:7a",
            "6b:2e:4a:c9:b9:f2",
            "fa:bf:98:64:d:a8",
            "4f:7c:f7:ac:6d:73",
            "fc:fe:cb:ee:5c:8d",
            "2:f4:af:c4:4a:4d",
            "6c:1a:3c:29:8f:d3",
            "19:61:1e:2:6:1e",
            "e8:98:f1:66:15:31",
            "5d:67:16:70:62:bb",
            "d8:68:54:f:63:fc",
            "4f:64:25:69:b3:dc",
            "4f:ce:5d:2f:44:f5",
            "29:e2:32:77:61:e7",
            "7f:9d:16:ca:cb:ab",
            "54:82:28:18:1f:38",
            "6c:c5:7e:5f:b6:c8",
            "6f:9:8f:4b:db:2c",
            "3e:27:a4:b4:61:ae",
            "4:21:55:7e:9c:2",
            "65:5:b1:88:45:3a",
            "fe:e1:61:c3:9a:c5",
            "6e:65:38:db:41:32",
            "4d:65:10:c4:83:7",
            "69:ea:91:73:5:54",
            "6c:b2:d8:25:79:8",
            "f3:6e:9d:39:b9:d",
            "ec:6a:e8:23:e9:24",
            "d4:69:63:9:b3:7a",
            "fd:c8:7f:82:9c:73",
            "7e:92:48:48:6b:aa",
            "0:91:aa:8a:85:ae",
            "61:c1:e5:cd:d4:35",
            "10:1:2c:2d:6a:dc",
            "5a:b:b3:50:80:26",
            "18:36:50:9e:15:fe",
            #range 2
            "56:cc:c:2e:9:aa",
            "47:32:ca:8e:27:61",
            "11:b4:37:5e:4b:ea",
            "e8:6e:15:49:ed:81",
            "19:2:33:81:2b:64",
            "31:d7:ce:c1:2b:0",
            "28:68:aa:8:a2:1",
            "70:9d:2f:a6:1d:16",
            "2f:4d:9b:67:64:15",
            "13:90:d6:2b:33:f3",
            "6e:e5:3a:b6:a5:b2",
            "24:a3:3a:d0:b4:e9",
            "2a:f5:8e:f2:8c:2d",
            "3f:e5:d1:49:51:9c",
            "40:a3:5e:7e:73:55",
            "5d:d4:ef:d1:be:43",
            "c3:b2:19:5d:f8:6d",
            "5b:5d:c1:83:eb:4e",
            "31:d2:83:27:6b:a6",
            "36:66:fe:8b:91:75",
            "63:b2:91:d:79:bb",
            "64:b0:a6:f8:74:2b",
            "6b:52:28:54:6b:bd",
            "63:d7:94:dd:db:a8",
            "4b:c7:95:d5:af:5f",
            "70:47:94:73:67:53",
            "31:38:71:8a:a3:f1",
            "dc:f3:79:2c:f4:40",
            "90:f1:57:81:cc:62",
            "76:36:db:70:8a:ed",
            "70:a9:25:9d:c9:73",
            #range 3
            "7a:1c:32:8c:29:cd",
            "43:26:48:a7:85:91",
            "2f:87:2:81:47:25",
            "24:40:4c:c1:aa:3a",
            "1:52:e3:65:98:77",
            "69:7f:21:ca:6b:40",
            "cb:5c:c4:7e:c4:e5",
            "d7:d2:18:3b:22:e9",
            "ea:ce:2c:e7:96:97",
            "e9:d4:d6:9c:96:14",
            "c4:5a:55:fa:c2:b8",
            "21:4a:5:3c:61:e1",
            "19:ae:9b:e5:b0:ed",
            "f5:3b:22:96:47:34",
            "f5:2d:e8:73:5:2f",
            "0:34:6e:30:1a:2a",
            "c4:f5:4e:e0:77:95",
            "1a:73:a5:93:e7:ce",
            "49:b0:2a:bb:57:c0",
            "5b:25:71:ca:e3:a3",
            "53:5b:cf:7:fa:ac",
            "e:4e:a1:b9:cf:2b",
            "19:15:69:46:ca:11",
            "22:6d:13:46:a3:84",
            "f0:99:19:1e:97:d5",
            "79:8f:46:ed:e2:22",
            "70:6f:7e:8a:7:b",
            "54:54:bd:cb:71:34",
            "71:7e:8a:ed:d7:cf",
            "76:ef:68:74:9b:24",
            "78:3f:4b:93:af:df",
            "6b:f4:91:c:55:d3",
            "7e:bc:74:9b:90:2e",
            "1e:31:19:4:ac:68",
            "6f:1f:c:d5:67:74",
            "7e:51:fa:88:d2:80",
            "6b:c4:2:68:55:d0",
            #range 4
            "1f:78:cb:c2:43:64",
            "47:d9:30:7:d:29",
            "1d:38:8f:11:cc:1b",
            "27:23:e8:61:81:9d",
            "1a:55:91:ff:99:c8",
            "6c:c8:e5:3f:2d:59",
            "57:a1:9:f:3b:6e",
            "1d:7f:db:f2:9c:b0",
            "37:5c:2f:ab:f0:54",
            "7f:33:bf:9a:79:e0",
            "5f:3b:84:90:d5:23",
            "7e:53:88:9d:c3:a0",
            "18:11:dc:84:63:32",
            "2d:30:3b:50:24:65",
            "fb:c0:80:f5:42:28",
            "5b:15:c6:f9:e3:90",
            "22:22:50:c2:69:3c",
            "51:fb:15:17:4e:6f",
            "41:6a:51:31:44:e2",
            "6c:1d:1:f5:ec:26",
            "44:b6:19:c9:41:ba",
            "21:88:d0:ed:2e:8",
            "11:68:f6:6b:f1:a6",
            "5:15:d:b:7a:40",
           "64:2c:4e:52:ec:90",
            "ff:3:a7:a6:f9:58",
            "f7:85:dc:34:b2:db",
            "eb:2d:b5:2d:bc:ae",
            "fb:f4:ea:78:c6:a4",
            "c1:36:85:80:59:d9",
            "76:2b:21:fb:37:10",
            "e4:7c:25:10:70:c5",
            "18:f7:c:44:d9:d1",
            "c7:9a:58:1d:71:f3",
            "66:cb:ed:c5:fb:b4",
            "c1:fa:c9:5:a1:6d",
            "a:b6:c9:61:7c:9d",
            "5f:c4:98:bf:7e:6e",
            "59:42:9b:3d:e8:14",
            "7d:d4:d9:32:50:92",
            "62:c8:45:5d:53:fa",
            "6e:41:50:e9:c0:f5",
            "2d:66:7e:36:e:d1",
        ]

        #BLE address lamp connectée => fb:58:1d:b:80:f1
        if device.address not in already_known_ble:
        #if device.address == "f0:78:bc:5e:2f:23":

            #x0, y0, x1, y1
            self.shape = self.canvas.create_oval(
                self.BLE_radar_pos[0], 
                self.BLE_radar_pos[1], 
                self.BLE_radar_pos[2], 
                self.BLE_radar_pos[3], 
                fill = "blue", 
                width = 2
            )
            
            self.txt_shape = self.canvas.create_text(
                self.BLE_radar_pos[0]+12, 
                self.BLE_radar_pos[1]+12,
                text=device.RSSI,
                fill="white"
            )

            #======================================================

            with open("adresses.txt", "a") as f:
                f.write(f"{device.address}\n")

            #======================================================

            self.iotItems_list[device.address] = self.txt_shape

            if self.BLE_radar_pos[0] >= 455:
                self.BLE_radar_pos[1] += 30
                self.BLE_radar_pos[3] += 30

                self.BLE_radar_pos[0] = 5
                self.BLE_radar_pos[2] = 30
            else:
                self.BLE_radar_pos[0] += 30
                self.BLE_radar_pos[2] += 30


            txPower = -20 #puissance de transmition de l'appareil en dBm; -20 est la valeur par défaut
            RSSI= device.RSSI
            PL0 = (txPower - -40) #puissance du signal à une distance de référence de 1m (varie avec la puissance de l'antenne)
            n = 2 #exposant de perte de trajet
            self.distance = 10 ** ((txPower - RSSI - PL0) / (10 * n))

            print(f"{device.address} RSSI => {device.RSSI} -- {round(self.distance, 2)}m")

            ###############POUR LA PROCHAINE FOIS
            #Il faudrait continuer l'équation ci-dessus qui n'est pas super précise 
            #(à 1m de l'antenne, l'équation me renvoie une distance entre 3 et 4m et à 2m, une distance de 1.5m)
            #Il faudrait remettre en place le "update_ble_device" pour ne pas devoir recharger le logiciel
            #a chaque essaie



    def update_ble_device(self, key, field, value):

        key = str(key).split("_")[0]
        

        #print(key in list(self.iotItems_list.keys()))

        if field == "RSSI" and key == "f0:78:bc:5e:2f:23":
            distance = self.rssi_to_distance(value)
            self.canvas.itemconfigure(self.iotItems_list[key], text=str(f"{value}\n{distance}m"))
        
        #print(f"{self.BLE_sniffer.get_devices()}\n\n")
        
        #print(f"update => {key}, {field}, {value}")

    def remove_ble_device(self, key):
        #print(f"remove => {key}")
        pass


    def rssi_to_distance(self, rssi):

        if rssi >= -60:
            distance = f"< 1m => {rssi}"
        elif rssi <= -60 and rssi >= -70:
            distance = f"entre 1m et 2.5mm => {rssi}"
        elif rssi <= -70 and rssi >= -80:
            distance = f"entre 2.5m et 6m => {rssi}"
        else:
            distance = rssi


        print(distance)

        return 1