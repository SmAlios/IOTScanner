#!/bin/python3
import tkinter as tk
import signal, os, subprocess, platform
from gui.gui import GUI
from sniffers.BLE_Sniffer import BLESniffer
from sniffers.WiFi_Sniffer import WiFiSniffer
from sniffers.ZigBee_Sniffer import ZigBeeSniffer
from time import sleep

#apply a delay on start (required if want to run on OS start)
#if you don't want that the software automaticaly run on start, set False
delay_on_start = True

MyBLESniffer = None
MyWiFiSniffer = None
MyZigBeeSniffer = None

COM_BLESniffer = ""
COM_ZigBeeSniffer = ""
COM_WiFiSniffer = ""

def init_antennas():
    data_antennas = subprocess.run(["./init_antennas.sh"], capture_output=True, text=True)
    data_antennas = data_antennas.stdout.split("\n")
    
    for antenna in data_antennas:

        if("Bluetooth" in antenna.split("_")):
            COM_BLESniffer = antenna.split(" - ")[0]

        elif("USB" in antenna.split("_")):
            COM_WiFiSniffer = antenna.split(" - ")[0]

        elif("UART" in antenna.split("_")):
            COM_ZigBeeSniffer = antenna.split(" - ")[0]
        else:
            COM_BLESniffer = "/dev/ttyACM1"
            COM_ZigBeeSniffer = "/dev/ttyACM0"
            COM_WiFiSniffer = "/dev/ttyUSB0"

    return [COM_BLESniffer, COM_ZigBeeSniffer, COM_WiFiSniffer]


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
        COM_BLESniffer, COM_ZigBeeSniffer, COM_WiFiSniffer = init_antennas()
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

    #Because of the screen not charging fast enought, with a classical service,
    #the software obtain the error "_tkinter.TclError: couldn't connect to display ':0'"
    #so a delay is the only solution to launch the softwre on start
    if delay_on_start == True:
        sleep(8)

    # Create the main window
    root = tk.Tk()
    root.title("IOTScanner")

    #configured for a respberry with a Touch Pad
    if os_used == "Linux":
        #root.attributes("-fullscreen", True)
        root.geometry("800x480+0+0")
        root.overrideredirect(True)
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