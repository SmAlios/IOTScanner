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

# Init sniffer var
MyBLESniffer = None
MyWiFiSniffer = None
MyZigBeeSniffer = None

# init sniffer's COM var
COM_BLESniffer = ""
COM_ZigBeeSniffer = ""
COM_WiFiSniffer = ""

# <protocol>:<part of antenna name> can be change and is used to set a tty to a protocol
# In the protocol section, type the protocol name. In the second, type the/a part of the antenna name
antennas_dic = {
    "BLE":"Bluetooth_LE",
    "Zigbee":"nRF52_USB",
    "WiFi":"USB_to_UART"
}

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
    
    tty = []
    antenna_name = []
    conn_antennas_dic = {}

    for antenna in antennas_list:

        # Only get attended format of data
        try:
            a, b = antenna.split("-")
            a = a.split(" ")[0]

            print(antenna)

            # Create a list of tty and a antenna_name list 
            tty.append(a)
            antenna_name.append(b)
        except:
            pass

    # Create a [antenna_name: tty] disctionnary containing the currently connected antennas
    i = 0
    for name in antenna_name:
        for  key, element in antennas_dic.items():
            if element in name:
                conn_antennas_dic[key] = tty[i]

        i += 1

    # Return the dictionnary containing the connected and recognized antennas
    return conn_antennas_dic

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

    # Get the list of used antennas
    dic_used_antennas = {}

    # If the os used is Linux, init_antennas() will detect automatically which
    # antenna's output to link with the right tty. If the os used is Windows,
    # it's your job to find the good OM to use (dont use Windows, Linux is better). 
    if os_used == "Linux":

        d = init_antennas()
        for protocol, tty in d.items():
            
            if protocol == "BLE":
                MyBLESniffer = BLESniffer(serialport=tty, baudrate=1000000)
                dic_used_antennas['BLE'] = (MyBLESniffer)
            elif protocol == "WiFi":
                MyWiFiSniffer = WiFiSniffer(serialport=tty, baudrate=115200)
                dic_used_antennas['WiFi'] = (MyWiFiSniffer)
            elif protocol == "Zigbee":
                MyZigBeeSniffer = ZigBeeSniffer(serialport=tty, baudrate=115200)
                dic_used_antennas['Zigbee'] = (MyZigBeeSniffer)
            else:
                print("ERROR : a critical error occure")
                exit()

    elif os_used == "Windows":
        MyBLESniffer = BLESniffer(serialport="COM6", baudrate=1000000)
        MyWiFiSniffer = WiFiSniffer(serialport="COM8", baudrate=115200)
        MyZigBeeSniffer = ZigBeeSniffer(serialport="COM5", baudrate=115200)

        dic_used_antennas = {
            "BLE": MyBLESniffer, 
            "WiFi": MyWiFiSniffer, 
            "Zigbee": MyZigBeeSniffer
        }
    else:
        print("Error occure, OS unrecognized")


    # Will detect if the software's window is close
    signal.signal(signal.SIGINT, signal_handler)

    # To provent the error "_tkinter.TclError: couldn't connect to display ':0'",
    # a delay is the only solution found to launch the softwre on start. 8 seconds
    # is alittle more tah the time generaly needed by the screen the finish it start
    if delay_on_start == True:
        #sleep(8)
        sleep(0)

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
    gui = GUI(root, dic_used_antennas)

    root.mainloop()


if __name__ == "__main__":
    main()