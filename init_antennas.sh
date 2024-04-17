#!/bin/bash

# Get the tty used by the antennas

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

for sysdevpath in $(find /sys/bus/usb/devices/usb*/ -name dev); do
    (
        syspath="${sysdevpath%/dev}"
        devname="$(udevadm info -q name -p $syspath)"
        [[ "$devname" == "bus/"* ]] && exit
        eval "$(udevadm info -q property --export -p $syspath)"
        [[ -z "$ID_SERIAL" ]] && exit
        echo "/dev/$devname - $ID_SERIAL"
    )
done