#!/bin/python3
import tkinter as tk
import signal, os
import platform
from gui.gui import GUI
from sniffers.BLE_Sniffer import BLESniffer
from sniffers.WiFi_Sniffer import WiFiSniffer
from sniffers.ZigBee_Sniffer import ZigBeeSniffer

MyBLESniffer = None
MyWiFiSniffer = None
MyZigBeeSniffer = None

COM_BLESniffer = ""
COM_ZigBeeSniffer = ""
COM_WiFiSniffer = ""

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
    os_used = platform.system()

    #configured my personal env during dev
    if os_used == "Linux":
        COM_BLESniffer = "/dev/ttyACM1" #acm1
        COM_ZigBeeSniffer = "/dev/ttyACM0" #usb0
        COM_WiFiSniffer = "/dev/ttyUSB0" #acm0
    elif os_used == "Windows":
        COM_BLESniffer = "COM6"
        COM_ZigBeeSniffer = "COM5"
        COM_WiFiSniffer = "COM8"
    else:
        print("Error occure, os unrecognized")

    MyBLESniffer = BLESniffer(serialport=COM_BLESniffer, baudrate=1000000)
    MyWiFiSniffer = WiFiSniffer(serialport=COM_WiFiSniffer, baudrate=115200)
    MyZigBeeSniffer = ZigBeeSniffer(serialport=COM_ZigBeeSniffer, baudrate=115200)

    signal.signal(signal.SIGINT, signal_handler)

    # Create the main window
    root = tk.Tk()
    root.title("IOTScanner")

    #configured for a respberry with a Touch Pad
    if os_used == "Linux":
        root.attributes("-fullscreen", True)
    elif os_used == "Windows":
        root.geometry("800x480")
    else:
        print("Error occure, os unrecognized")
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Create GUI instance
    gui = GUI(root, MyBLESniffer, MyWiFiSniffer, MyZigBeeSniffer, 0)

    root.mainloop()


if __name__ == "__main__":
    main()
