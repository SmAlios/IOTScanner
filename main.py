#!/bin/python3
import tkinter as tk
import signal, os
from gui.gui import GUI
from sniffers.BLE_Sniffer import BLESniffer
from sniffers.WiFi_Sniffer import WiFiSniffer
from sniffers.ZigBee_Sniffer import ZigBeeSniffer

MyBLESniffer = None
MyWiFiSniffer = None
MyZigBeeSniffer = None

#please choose your OS
#choose 0 for Windows                       =>      in dev case
#choose 1 for Raspberry with Touch Pad      =>      use case
supported_os_list = ["win","raspScreen"]
os_used = supported_os_list[0]

#to find the correct tty*, use "ls /dev/tty*" and try to
#deconnect and reconnect the differents antennas
#COM_BLESniffer = "/dev/ttyACM0"
#COM_ZigBeeSniffer = "/dev/ttyACM1"
#COM_WiFiSniffer = "/dev/ttyUSB0"

COM_BLESniffer = "COM6"
COM_ZigBeeSniffer = "COM5"
COM_WiFiSniffer = "COM8"

def signal_handler(sig, frame):
    on_closing()


def on_closing():
    try:
        MyBLESniffer.stop()
    except Exception as e:
        pass
    try:
        MyWiFiSniffer.stop()
    except Exception as e:
        pass
    try:
        MyZigBeeSniffer.stop()
    except Exception as e:
        pass
    os._exit(1)


def main():
    # Create Sniffers
    global MyBLESniffer, MyWiFiSniffer, MyZigBeeSniffer

    MyBLESniffer = BLESniffer(serialport=COM_BLESniffer, baudrate=1000000)
    MyWiFiSniffer = WiFiSniffer(serialport=COM_WiFiSniffer, baudrate=115200)
    MyZigBeeSniffer = ZigBeeSniffer(serialport=COM_ZigBeeSniffer, baudrate=115200)

    signal.signal(signal.SIGINT, signal_handler)

    # Create the main window
    root = tk.Tk()
    root.title("IOTScanner")

    if os_used == 1:
        root.attributes("-fullscreen", True)
    elif os_used == 0:
        root.geometry("800x480")
    else:
        print("ERROR => choosed OS don't exist")
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Create GUI instance
    gui = GUI(root, MyBLESniffer, MyWiFiSniffer, MyZigBeeSniffer, 0)

    root.mainloop()


if __name__ == "__main__":
    main()
