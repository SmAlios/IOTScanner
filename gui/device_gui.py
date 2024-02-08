import tkinter as tk

global colors
colors = [
    "#F8F8F8",
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
    "#525252",
]


class DeviceRow:
    def __init__(
        self, device, row, selected_channel, device_table_frame, add_seized_device_row
    ):
        self.device = device
        self.row = row
        self.selected_channel = selected_channel
        self.device_table_frame = device_table_frame
        self.add_seized_device_row = add_seized_device_row

        self.create_widget()
        self.set_grid()

    def create_widget(self):
        self.color = "#d9d9d9"
        if self.device.type == "WiFi-2.4GHz":
            self.checkbox_var = tk.BooleanVar()
            self.check_button = tk.Checkbutton(
                self.device_table_frame,
                variable=self.checkbox_var,
                command=self.on_checkbox_click,
            )
            self.RSSI_label = tk.Label(
                self.device_table_frame, text=str(self.device.RSSI)
            )
            self.channel_label = tk.Label(
                self.device_table_frame,
                text=str(self.device.channel),
                bg=colors[int(self.device.channel) - 1],
            )
            self.address_label = tk.Label(
                self.device_table_frame, text=str(self.device.address)
            )
            self.timestamp_label = tk.Label(
                self.device_table_frame, text=str(self.device.timestamp)
            )
            self.seize_button = tk.Button(
                self.device_table_frame,
                text="Seize",
                command=self.on_seize_click,
                borderwidth=5,
                relief=tk.RAISED,
                padx=5,
                pady=5,
            )

        elif self.device.type == "BLE":
            self.checkbox_var = tk.BooleanVar()
            self.check_button = tk.Checkbutton(
                self.device_table_frame,
                variable=self.checkbox_var,
                command=self.on_checkbox_click,
            )
            self.RSSI_label = tk.Label(
                self.device_table_frame, text=str(self.device.RSSI)
            )
            self.address_label = tk.Label(
                self.device_table_frame, text=str(self.device.address)
            )
            self.name_label = tk.Label(
                self.device_table_frame, text=str(self.device.name)
            )
            self.timestamp_label = tk.Label(
                self.device_table_frame, text=str(self.device.timestamp)
            )
            self.seize_button = tk.Button(
                self.device_table_frame,
                text="Seize",
                command=self.on_seize_click,
                borderwidth=5,
                relief=tk.RAISED,
                padx=5,
                pady=5,
            )

        elif self.device.type == "ZigBee":
            self.checkbox_var = tk.BooleanVar()
            self.check_button = tk.Checkbutton(
                self.device_table_frame,
                variable=self.checkbox_var,
                command=self.on_checkbox_click,
            )
            self.RSSI_label = tk.Label(
                self.device_table_frame, text=str(self.device.RSSI)
            )

            self.channel_label = tk.Label(
                self.device_table_frame,
                text=str(self.device.channel),
                bg=colors[int(self.device.channel) - 11],
            )
            self.address_label = tk.Label(
                self.device_table_frame, text=str(self.device.address)
            )
            self.extAddress_label = tk.Label(
                self.device_table_frame, text=str(self.device.extAddress)
            )
            self.timestamp_label = tk.Label(
                self.device_table_frame, text=str(self.device.timestamp)
            )
            self.seize_button = tk.Button(
                self.device_table_frame,
                text="Seize",
                command=self.on_seize_click,
                borderwidth=5,
                relief=tk.RAISED,
                padx=5,
                pady=5,
            )

        elif self.device.type == "6LoWPAN":
            self.checkbox_var = tk.BooleanVar()
            self.check_button = tk.Checkbutton(
                self.device_table_frame,
                variable=self.checkbox_var,
                command=self.on_checkbox_click,
            )
            self.RSSI_label = tk.Label(
                self.device_table_frame, text=str(self.device.RSSI)
            )

            self.channel_label = tk.Label(
                self.device_table_frame,
                text=str(self.device.channel),
                bg=colors[int(self.device.channel) - 11],
            )
            self.address_label = tk.Label(
                self.device_table_frame, text=str(self.device.address)
            )
            self.timestamp_label = tk.Label(
                self.device_table_frame, text=str(self.device.timestamp)
            )
            self.seize_button = tk.Button(
                self.device_table_frame,
                text="Seize",
                command=self.on_seize_click,
                borderwidth=5,
                relief=tk.RAISED,
                padx=5,
                pady=5,
            )

    def set_grid(self):
        if (self.selected_channel != -1) and (
            self.selected_channel != self.device.channel
        ):
            return

        if self.device.type == "WiFi-2.4GHz":
            self.check_button.grid(row=self.row, column=0, sticky="nsew")
            self.RSSI_label.grid(row=self.row, column=1, sticky="nsew")
            self.channel_label.grid(row=self.row, column=2, sticky="nsew")
            self.address_label.grid(row=self.row, column=3, sticky="nsew")
            self.timestamp_label.grid(row=self.row, column=4, sticky="nsew")
            self.seize_button.grid(row=self.row, column=5, sticky="nsew")

        elif self.device.type == "BLE":
            self.check_button.grid(row=self.row, column=0, sticky="nsew")
            self.RSSI_label.grid(row=self.row, column=1, sticky="nsew")
            self.address_label.grid(row=self.row, column=2, sticky="nsew")
            self.name_label.grid(row=self.row, column=3, sticky="nsew")
            self.timestamp_label.grid(row=self.row, column=4, sticky="nsew")
            self.seize_button.grid(row=self.row, column=5, sticky="nsew")

        elif self.device.type == "ZigBee":
            self.check_button.grid(row=self.row, column=0, sticky="nsew")
            self.RSSI_label.grid(row=self.row, column=1, sticky="nsew")
            self.channel_label.grid(row=self.row, column=2, sticky="nsew")
            self.address_label.grid(row=self.row, column=3, sticky="nsew")
            self.extAddress_label.grid(row=self.row, column=4, sticky="nsew")
            self.timestamp_label.grid(row=self.row, column=5, sticky="nsew")
            self.seize_button.grid(row=self.row, column=6, sticky="nsew")

        elif self.device.type == "6LoWPAN":
            self.check_button.grid(row=self.row, column=0, sticky="nsew")
            self.RSSI_label.grid(row=self.row, column=1, sticky="nsew")
            self.channel_label.grid(row=self.row, column=2, sticky="nsew")
            self.address_label.grid(row=self.row, column=3, sticky="nsew")
            self.timestamp_label.grid(row=self.row, column=4, sticky="nsew")
            self.seize_button.grid(row=self.row, column=5, sticky="nsew")

    def set_color(self, color):
        if self.color == color:
            return

        self.color = color
        if self.device.type == "WiFi-2.4GHz":
            self.check_button.configure(background=color)
            self.RSSI_label.configure(background=color)
            self.channel_label.configure(
                background=("red", colors[int(self.device.channel) - 1])[color != "red"]
            )
            self.address_label.configure(background=color)
            self.timestamp_label.configure(background=color)
            self.seize_button.configure(background=color)

        elif self.device.type == "BLE":
            self.check_button.configure(background=color)
            self.RSSI_label.configure(background=color)
            self.address_label.configure(background=color)
            self.name_label.configure(background=color)
            self.timestamp_label.configure(background=color)
            self.seize_button.configure(background=color)

        elif self.device.type == "ZigBee":
            self.check_button.configure(background=color)
            self.RSSI_label.configure(background=color)

            self.channel_label.configure(
                background=("red", colors[int(self.device.channel) - 11])[
                    color != "red"
                ]
            )
            self.address_label.configure(background=color)
            self.extAddress_label.configure(background=color)
            self.timestamp_label.configure(background=color)
            self.seize_button.configure(background=color)

        elif self.device.type == "6LoWPAN":
            self.check_button.configure(background=color)
            self.RSSI_label.configure(background=color)

            self.channel_label.configure(
                background=("red", colors[int(self.device.channel) - 11])[
                    color != "red"
                ]
            )
            self.address_label.configure(background=color)
            self.timestamp_label.configure(background=color)
            self.seize_button.configure(background=color)

    def destroy(self):
        if self.device.type == "WiFi-2.4GHz":
            self.check_button.destroy()
            self.RSSI_label.destroy()
            self.channel_label.destroy()
            self.address_label.destroy()
            self.timestamp_label.destroy()
            self.seize_button.destroy()

        elif self.device.type == "BLE":
            self.check_button.destroy()
            self.RSSI_label.destroy()
            self.address_label.destroy()
            self.name_label.destroy()
            self.timestamp_label.destroy()
            self.seize_button.destroy()

        elif self.device.type == "ZigBee":
            self.check_button.destroy()
            self.RSSI_label.destroy()
            self.channel_label.destroy()
            self.address_label.destroy()
            self.extAddress_label.destroy()
            self.timestamp_label.destroy()
            self.seize_button.destroy()

        elif self.device.type == "6LoWPAN":
            self.check_button.destroy()
            self.RSSI_label.destroy()
            self.channel_label.destroy()
            self.address_label.destroy()
            self.timestamp_label.destroy()
            self.seize_button.destroy()

    def forget(self):
        if self.device.type == "WiFi-2.4GHz":
            self.check_button.grid_forget()
            self.RSSI_label.grid_forget()
            self.channel_label.grid_forget()
            self.address_label.grid_forget()
            self.timestamp_label.grid_forget()
            self.seize_button.grid_forget()

        elif self.device.type == "BLE":
            self.check_button.grid_forget()
            self.RSSI_label.grid_forget()
            self.address_label.grid_forget()
            self.name_label.grid_forget()
            self.timestamp_label.grid_forget()
            self.seize_button.grid_forget()

        elif self.device.type == "ZigBee":
            self.check_button.grid_forget()
            self.RSSI_label.grid_forget()
            self.channel_label.grid_forget()
            self.address_label.grid_forget()
            self.extAddress_label.grid_forget()
            self.timestamp_label.grid_forget()
            self.seize_button.grid_forget()

        elif self.device.type == "6LoWPAN":
            self.check_button.grid_forget()
            self.RSSI_label.grid_forget()
            self.channel_label.grid_forget()
            self.address_label.grid_forget()
            self.timestamp_label.grid_forget()
            self.seize_button.grid_forget()

    def unforget(self):
        self.set_grid()

    def on_checkbox_click(self):
        if self.checkbox_var.get():
            self.set_color("red")
        else:
            self.set_color("#f0f0f0")

    def on_seize_click(self):
        self.add_seized_device_row(self.device)

    def __repr__(self):
        row = self.RSSI_label.grid_info()["row"]
        return f"DeviceRow(row: {row}, device: {self.device.__repr__()})"


class DeviceTable:
    def __init__(self, device_table_frame, add_seized_device_row):
        self.device_table_frame = device_table_frame
        self.add_seized_device_row = add_seized_device_row
        self.device_rows = {}  # mapping key to deviceRow
        self.size = 1  # start at one because row 0 for heading
        self.selected_channel = -1  # -1 means all

    def add_row(self, device):
        device_row = DeviceRow(
            device,
            self.size,
            self.selected_channel,
            self.device_table_frame,
            self.add_seized_device_row,
        )
        self.device_rows[device.key] = device_row
        self.size += 1

    def remove_row(self, key):
        device_row = self.device_rows[key]
        device_row.destroy()
        del self.device_rows[key]
        self.size -= 1

    def update_row(self, key, field, value):
        device_row = self.device_rows[key]
        setattr(device_row.device, field, value)
        field_label = field + "_label"
        getattr(device_row, field_label).config(text=str(value))

        if field == "channel":
            channel = int(value)
            getattr(device_row, field_label).config(
                background=("red", colors[channel - 1])[
                    getattr(device_row, field_label)["background"] != "red"
                ]
            )

            if self.selected_channel != -1:
                if channel == self.selected_channel:
                    device_row.unforget()
                else:
                    device_row.forget()

    def filter(self, new_channel):
        self.selected_channel = new_channel
        for device_row in self.device_rows.values():
            if device_row.device.channel == new_channel:
                device_row.unforget()
            else:
                device_row.forget()

    def unfilter(self):
        self.selected_channel = -1
        for device_row in self.device_rows.values():
            device_row.unforget()

    def __repr__(self):
        str = ""
        for values in self.device_rows.values():
            str += values.__repr__()
            str += ",\n"
        return f"DeviceTable( {str} )"

    def get_selected_channel(self):
        return self.selected_channel


class SeizedDeviceRow:
    def __init__(self, device_table_frame, device):
        self.device_table_frame = device_table_frame
        self.device = device

        channel = str(device.channel) if device.channel != None else ""
        self.channel_label = tk.Label(self.device_table_frame, text=channel)
        self.address_label = tk.Label(self.device_table_frame, text=str(device.address))
        self.type_label = tk.Label(self.device_table_frame, text=str(device.type))

    def set_grid(self, new_row):
        new_row = new_row + 1  # offset because row 0 reserved for heading
        self.channel_label.grid(row=new_row, column=0, sticky="nsew")
        self.address_label.grid(row=new_row, column=1, sticky="nsew")
        self.type_label.grid(row=new_row, column=2, sticky="nsew")

    def __repr__(self):
        row = self.address_label.grid_info()["row"]
        return f"SeizedDeviceRow(row: {row}, device: {self.device.__repr__()})"


class SeizedDeviceTable:
    def __init__(self, device_table_frame):
        self.device_table_frame = device_table_frame

        self.device_rows = {}  # mapping key to deviceRow
        self.size = 0

    def add_row(self, device):
        device_row = SeizedDeviceRow(self.device_table_frame, device)
        device_row.set_grid(self.size)
        self.device_rows[device.address] = device_row
        self.size += 1

    def __repr__(self):
        str = ""
        for values in self.device_rows.values():
            str += values.__repr__()
            str += ",\n"
        return f"SeizedDeviceTable( {str} )"
