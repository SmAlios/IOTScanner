import tkinter as tk

global colors
colors = [    "#F8F8F8",
    "#ECECEC",
    "#E1E1E1",
    "#D6D6D6",
    "#CBCBCB",
    "#C0C0C0",
    "#B5B5B5",
    "#AAAAAA",
    "#9F9F9F",
    "#949494",
    "#898989",
    "#7E7E7E",
    "#737373",
    "#686868",
    "#5D5D5D",
    "#525252"]


class NetworkRow:

    def __init__(self, network, row, network_table_frame, device_table, Sniffer, get_network_rows, set_network_rows):
        self.network = network
        self.row = row
        self.network_table_frame = network_table_frame
        self.device_table = device_table
        self.Sniffer = Sniffer
        self.get_network_rows = get_network_rows
        self.set_network_rows = set_network_rows
        
        self.create_widgets()
        self.set_grid()
        
        # Add the current NetworkRow in the network_rows dictionary
        self.set_network_rows(network.key, self)
    
    def create_widgets(self):
        self.color = "#d9d9d9"
        if (self.network.type == "WiFi-2.4GHz"):
            self.checkbox_var = tk.BooleanVar()
            self.check_button = tk.Checkbutton(self.network_table_frame, variable=self.checkbox_var, command=lambda: self.on_checkbox_click(self.check_button, self.checkbox_var))
            self.RSSI_label = tk.Label(self.network_table_frame, text=str(self.network.RSSI))
            self.channel_label = tk.Label(self.network_table_frame, text=str(self.network.channel), bg=colors[int(self.network.channel)-1])
            self.ID_label = tk.Label(self.network_table_frame, text=str(self.network.ID))
            self.BSSID_label = tk.Label(self.network_table_frame, text=str(self.network.BSSID))
            self.timestamp_label = tk.Label(self.network_table_frame, text=str(self.network.timestamp))

        elif (self.network.type == "ZigBee"):
            self.checkbox_var = tk.BooleanVar()
            self.check_button = tk.Checkbutton(self.network_table_frame, variable=self.checkbox_var, command=lambda: self.on_checkbox_click(self.check_button, self.checkbox_var))
            self.RSSI_label = tk.Label(self.network_table_frame, text=str(self.network.RSSI))
            self.channel_label = tk.Label(self.network_table_frame, text=str(self.network.channel), bg=colors[int(self.network.channel)-11])
            self.ID_label = tk.Label(self.network_table_frame, text=str(self.network.ID))
            self.timestamp_label = tk.Label(self.network_table_frame, text=str(self.network.timestamp))

    def set_grid(self):
        if (self.network.type == "WiFi-2.4GHz"):
            self.check_button.grid(row=self.row, column=0, sticky="nsew")
            self.RSSI_label.grid(row=self.row, column=1, sticky="nsew")
            self.channel_label.grid(row=self.row, column=2, sticky="nsew")
            self.ID_label.grid(row=self.row, column=3, sticky="nsew")
            self.BSSID_label.grid(row=self.row, column=4, sticky="nsew")
            self.timestamp_label.grid(row=self.row, column=5, sticky="nsew")

        elif (self.network.type == "ZigBee"):
            self.check_button.grid(row=self.row, column=0, sticky="nsew")
            self.RSSI_label.grid(row=self.row, column=1, sticky="nsew")
            self.channel_label.grid(row=self.row, column=2, sticky="nsew")
            self.ID_label.grid(row=self.row, column=3, sticky="nsew")
            self.timestamp_label.grid(row=self.row, column=4, sticky="nsew")

    def set_color(self, color):
        if(color == self.color):
            return
        
        self.color = color
        if (self.network.type == "WiFi-2.4GHz"):
            self.check_button.configure(background=color)
            self.RSSI_label.configure(background=color)
            self.channel_label.configure(background=("red", colors[int(self.network.channel)-1])[color != "red"])
            self.ID_label.configure(background=color)
            self.BSSID_label.configure(background=color)
            self.timestamp_label.configure(background=color)
        elif (self.network.type == "ZigBee"):
            self.check_button.configure(background=color)
            self.RSSI_label.configure(background=color)
            self.channel_label.configure(background=("red", colors[int(self.network.channel)-11])[color != "red"])
            self.ID_label.configure(background=color)
            self.timestamp_label.configure(background=color)

    def destroy(self):
        if (self.network.type == "WiFi-2.4GHz"):
            self.check_button.destroy()
            self.RSSI_label.destroy()
            self.channel_label.destroy()
            self.ID_label.destroy()
            self.BSSID_label.destroy()
            self.timestamp_label.destroy()
        elif (self.network.type == "ZigBee"):
            self.check_button.destroy()
            self.RSSI_label.destroy()
            self.channel_label.destroy()
            self.ID_label.destroy()
            self.timestamp_label.destroy()

    def on_checkbox_click(self, button, variable):
        for network_row in self.get_network_rows().values():
            # if current button is the one being checked
            if network_row.check_button == button:
                # if not already checked
                if(variable.get()):
                    self.device_table.filter(self.network.channel)
                    network_row.check_button.select()
                    self.set_color("red")
                    if (self.network.type == "WiFi-2.4GHz"):
                        self.Sniffer.serial.write(str(self.network.channel).encode('utf-8'))
                    elif (self.network.type == "ZigBee"):
                        self.Sniffer.setChannel(self.network.channel)
                # if already clicked
                else:
                    self.device_table.unfilter()
                    network_row.check_button.deselect()
                    self.set_color('#d9d9d9')
                    if (self.network.type == "WiFi-2.4GHz"):
                        self.Sniffer.serial.write(str(-1).encode('utf-8'))
                    elif (self.network.type == "ZigBee"):
                        self.Sniffer.unsetChannel()
            # current checkbutton not clicked
            else:
                network_row.check_button.deselect()
                network_row.set_color('#d9d9d9')

    def __repr__(self):
        row = self.RSSI_label.grid_info()['row']
        return f'NetworkRow(row: {row}, network: {self.network.__repr__()})'


class NetworkTable:

    def __init__(self, network_table_frame, Sniffer, device_table):
        self.network_table_frame = network_table_frame
        self.Sniffer = Sniffer
        self.device_table = device_table
        self.network_rows = {}  # mapping key to NetworkRow
        self.size = 1 # start at one because row 0 for heading

    def add_row(self, network):
        network_row = NetworkRow(network, self.size, self.network_table_frame, self.device_table, self.Sniffer, self.get_network_rows, self.set_network_rows)
        self.network_rows[network.key] = network_row
        self.size += 1

    def remove_row(self, key):
        network_row = self.network_rows[key]
        network_row.destroy()
        del self.network_rows[key]
        self.size -= 1

    def update_row(self, key, field, value):
        network_row = self.network_rows[key]
        setattr(network_row.network, field, value)
        field_label = field + "_label"
        getattr(network_row, field_label).config(text=str(value))

    def __repr__(self):
        str = ""
        for values in self.network_rows.values():
            str += values.__repr__()
            str += ",\n"
        return f'NetworkTable( {str} )'

    # ====================
    # Getters and setters
    # ====================
    def get_network_rows(self):
        return self.network_rows
    
    def set_network_rows(self, key, value):
        self.network_rows[key] = value