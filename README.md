# IOTScanner
This project is an upgrade and port of igorferro1/IoT-Hound's project on Raspberry Raspberry pi 4 with a Touch Display. The purpose of the project is to permeit to detect IOT devices.

prefer to use the "portable version" of the project. Otherwise, you'll need to perform the software directly on a computer.

## Version
Last stable version is 1.0.8

## Features
- detecting BLE devices
- detecting ZigBee devices and networks
- detecting 6loWPAN devices
- detecting WiFi devices and networks
- display signal force (RSSI)
- compress the gathered data in an archive
- compatible with windows and linux

## How to use
The software automatically run on OS startup.
If you start a scan, the progressbar'll start to load until the ZigBee networks scan is complete.
During the initial scan, you can move to other tabs but they are not refresh automatically with the data.
When the data are display on a table, the signal power is update constantely.

At any time, you can stop the scan. It'll create archive with the collected data in {project directory}/archives.

## road map
In the next updates could come those features :
- screen with a radar to display the distance from IOT devices
- triangulate the IOT devices position with a GPS beacon
- 3D plan of a case for the Raspberry

## Needed hardware
You need some hardware to perform the software.

Needed for any project version :
- two Dongle nRF52840 antennas
- an Heltec LoRa 32 antenna

For the portable version :
- the antennas specified before
- a Raspberry pi 4 with 8GB RAM. The software hasn't been tested on lower Raspberry versions
- at minimum a 16Gb SD card. Prefer to have a minimum speed of 80Mb/s in read and/or write
- a Raspberry pi Touch Display

## Installation
This project is made to run on Linux like and Windows machines but it require some configurations befor run.

### Antennas configuration
Follow this to configure the antennas. Prefer to make thoses configurations on a Windows machine.
You'll need to configure two Dongle antennas and a Heltec antenna.

You can draw something on the Dongel antenna's label to be able to deference the two

Here are the firmwares files :
- the first Dongle'll scan BLE : [BLE firmwares file](https://github.com/SmAlios/IOTScanner/blob/main/firmwares/sniffer_nrf52840dongle_ble.hex)
- the second Dongle'll scan ZigBee : [ZigBee firmwares file](https://github.com/SmAlios/IOTScanner/blob/main/firmwares/sniffer_nrf52840dongle_802154.hex)
- the Heltec'll scan WiFi : [WiFi firmwares file](https://github.com/SmAlios/IOTScanner/blob/main/firmwares/sniffer_heltec_wifi_lora_v2/sniffer_heltec_wifi_lora_v2.ino)

#### Dongle nRF52840 antennas
- install the [nrf connect for desktop](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-desktop/download) software
- run the software, scroll down the apps list until you find the "Programmer" app and install it
- insert a Dongle antenna in an USB port of your computer
- open the "Programmer" app
- select the antenna
- drag and drop the firmwares file (see previous section) in the "file memory layout" section
- click on the "write" button
- the antenna is ready
- repeat the five last steps for the second Dongle antenna

#### Heltac antenna
- install the [antenna driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads) for windows
- install [arduino software](https://www.arduino.cc/en/software)
- follow this [tutorial](https://github.com/HelTecAutomation/Heltec_ESP32) but use the file specified in the previous section

### For a linux version (required for the portable version)
If you want to use the project on Windows, you don't need to do nothing. But please, pay attention that some functionalities won't operate normally (like the reboot and shutdown button on home screen). If you use the portable version, please follow those steps.

- download and install the OS with the [Raspberry pi imager software](https://www.raspberrypi.com/software/)
- insert your SD cart in your computer and start the Raspberry software.
- select the Raspberry pi machine you're using
- select the recommanded os for your Raspberry pi
- select your SD card and start the installation
- click "modify settings"
- in the "general" tab, tick "define a username and password" and define it. You must remember the username and password !!!
- in the "services" tab, tick "enable SSH". The option "Use a password for authentification" must be ticked
- save changes
- click "yes" and wait to the OS to be installed
- during the installation, connect the Raspberry Touch Display to the Raspberry. [Here](https://youtu.be/MQF3eQTiIpI) is a tutorial explaining how to do it.
- once the installation is finished, connect the SD card on the Raspberry
- connect an Ethernet cable and a power cable to the Raspberry (it should start it)
- connect an USB hub with a mouse and a keyboard to control the Raspberry (or use SSH)
- launch the terminal
- copy and paste this line and enter
```bash
sudo apt install git wget -y; curl https://raw.githubusercontent.com/SmAlios/IOTScanner/main/os_modifications.sh --output 'os_modifications.sh'; sudo chmod +x os_modifications.sh; ./os_modifications.sh
```
- respond to the differents questions asked
- if everything went well, the Raspberry should restart after a few minutes and the software should launch automatically after a few seconds

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update the readme.me as appropriate.