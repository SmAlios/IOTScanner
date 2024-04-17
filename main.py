#!/bin/python3
import tkinter as tk
import signal, os, subprocess, platform
from gui.gui import GUI
from sniffers.BLE_Sniffer import BLESniffer
from sniffers.WiFi_Sniffer import WiFiSniffer
from sniffers.ZigBee_Sniffer import ZigBeeSniffer
from time import sleep



# Apply a delay on start (required if want to run on OS start)
delay_on_start = True

MyBLESniffer = None
MyWiFiSniffer = None
MyZigBeeSniffer = None

COM_BLESniffer = ""
COM_ZigBeeSniffer = ""
COM_WiFiSniffer = ""

#===================================================================#
#                                                                   #
#   Function used to initialize antennas if on Linux.               #
#   No matter the usb slot used, this function is cappable to       #
#   link the right antenna's output to the right Linux's tty.       #
#                                                                   #
#   def : A tty is a Linux terminal. There is numberous tty on      #
#   Linux and can be listed with "ls -l /dev/tty*"                  #
#                                                                   #
#   @return List - teh three antennas's output correctly linked     #
#                                                                   #
#===================================================================#

def init_antennas():
    # Get the return of the scrip init_antennas.sh and delete the "\n" at the end of line.
    # The script return all the possible antennas matching with the tty expected syntax.
    antennas_list = subprocess.run(["./init_antennas.sh"], capture_output=True, text=True)
    antennas_list = antennas_list.stdout.split("\n")

    #===========================================================================#
    #                                                                           #
    #   Here is the architecture of the script's return :                       #
    #                                                                           #
    #   /dev/ttyACM0 - ZEPHYR_nRF_Sniffer_for_Bluetooth_LE_XXXXXXXXXXX          #
    #   /dev/ttyACM1 - Nordic_Semiconductor_nRF52_USB_Product_XXXXXXXXXXX       #
    #   /dev/ttyUSB0 - Silicon_Labs_XXXXXX_USB_to_UART_Bridge_Controller_0001   #
    #          ^                            ^                                   #
    #          |                            |                                   #
    #   Path to the tty linked with the     |                                   #
    #   antenna. It'll be used later to     |                                   #
    #   get the antenna's outputs           |                                   #
    #                                       |                                   #
    #           Name set by the firmware. It'll be used to confirm that         #
    #           the right antenna's output is link with the right tty.          #
    #                                                                           #
    #===========================================================================#

    i = 0
    usb_tty_list = []
    acm_tty_list = []

    # Create two lists of possible antenna's tty
    for antenna in antennas_list:
        if("USB" in antenna):
            usb_tty_list.append(antenna)
        if("ACM" in antenna):
            acm_tty_list.append(antenna)

    # Link BLE and ZigBee antenna's outputs with the right from the list created above
    for antenna in acm_tty_list:
        if("Bluetooth_LE" in antenna):
            COM_BLESniffer = antenna.split(" - ")[0]
        elif("Nordic_Semiconductor" in antenna):
            COM_ZigBeeSniffer = antenna.split(" - ")[0]
        else:
            i += 1
            print("ERROR => No right ttyACM* antenna detected, can't run")

    # Link WiFi antenna's output with tty from the list created above.
    # Because of the used tty syntax for the Wifi antenna, only one tty is expected.
    # If an error occure, the  default tty is given.
    list_lenght = len(usb_tty_list)
    if(list_lenght == 1):
        COM_WiFiSniffer = usb_tty_list[0]
    elif(list_lenght > 1):
        for antenna in usb_tty_list:
            if("Silicon_Labs" in antenna):
                COM_WiFiSniffer = antenna.split(" - ")[0]
    else:
        i += 1
        COM_WiFiSniffer = "/dev/ttyUSB0"
        print("ERROR => No right ttyUSB* antenna detected, default data given")

    # If two antennas or more aren't recognized, the default conf is used
    if(i >= 2):
        COM_BLESniffer = "/dev/ttyACM1"
        COM_ZigBeeSniffer = "/dev/ttyACM0"
        COM_WiFiSniffer = "/dev/ttyUSB0"

        print("ERROR => too many antennas error, default antenna's terminals given")

    return [COM_BLESniffer, COM_ZigBeeSniffer, COM_WiFiSniffer]


#===============================#
#                               #
#   Force the software to stop  #
#                               #
#===============================#

def signal_handler(sig, frame):
    on_closing()


#=======================================#
#                                       #
#   Interrupt the antenna's process     #
#   and exit software.                  #
#                                       #
#=======================================#

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


#===================================================#
#                                                   #
#   Initialize the GUI and initialize the antennas  #
#    used by the software.                          #
#                                                   #
#===================================================#

def main():
    # Global variables
    global MyBLESniffer
    global MyWiFiSniffer
    global MyZigBeeSniffer

    # Detect the os used by the host machine
    os_used = platform.system()

    # If the os used is Linux, init_antennas() will detect automatically which
    # antenna's output to link with the right tty. If the os used is Windows,
    # it's your job to find the good OM to use (dont use Windows, Linux is better). 
    if os_used == "Linux":
        COM_BLESniffer, COM_ZigBeeSniffer, COM_WiFiSniffer = init_antennas()
    elif os_used == "Windows":
        COM_BLESniffer = "COM6"
        COM_ZigBeeSniffer = "COM5"
        COM_WiFiSniffer = "COM8"
    else:
        print("Error occure, os unrecognized")

    # Initialize the communication between antenna's firwares and the software
    MyBLESniffer = BLESniffer(serialport=COM_BLESniffer, baudrate=1000000)
    MyWiFiSniffer = WiFiSniffer(serialport=COM_WiFiSniffer, baudrate=115200)
    MyZigBeeSniffer = ZigBeeSniffer(serialport=COM_ZigBeeSniffer, baudrate=115200)

    # Will detect if the software's window is close
    signal.signal(signal.SIGINT, signal_handler)

    # To provent the error "_tkinter.TclError: couldn't connect to display ':0'",
    # a delay is the only solution found to launch the softwre on start. 8 seconds
    # is alittle more tah the time generaly needed by the screen the finish it start
    if delay_on_start == True:
        sleep(8)

    # Create the main window
    root = tk.Tk()
    root.title("IOTScanner")

    # Configure the screen's settings for Windows or Linux.
    # The Linux settings are set to run on a respberry with a Touch Pad
    if os_used == "Linux":
        root.geometry("800x480+0+0")
        root.overrideredirect(True)
    elif os_used == "Windows":
        root.geometry("800x480")
    else:
        print("Error occure, os unrecognized")

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Create GUI instance
    gui = GUI(root, MyBLESniffer, MyWiFiSniffer, MyZigBeeSniffer)

    root.mainloop()


if __name__ == "__main__":
    main()