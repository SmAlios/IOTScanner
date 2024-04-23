#!/bin/bash

# Only run on linux like OS
# This file is made for a raspberrypiOS with GUI equiped with a Touch Display
# If you use another OS or device, you may make some modifications of the file
#
# How to install RaspberrypiOS and use the script :
#  1. Download and install the OS with the raspberry software https://www.raspberrypi.com/software/
#  2. You must install the recommanded OS for your raspberry pi on an SD card.
#     It's recommanded to use at minimum a 16GB SD card with a minimum speed of 80MB/s in read and/or write
#  3. Download this file (ex : with git) or copy it (ex : via SSH) to your raspberry
#  4. Give the correct execution rights to the file (sudo chmod u+x <filename>)
#  5. Execute the file (./<filename>) and respond to questions

# Init setup variables
RED="\e[31m"
GREEN="\e[32m"
ENDCOLOR="\e[0m"

USER=$(whoami)
ble_antenna=""
wifi_antenna=""
zigbee_antenna=""

touch_display=""
build_service=""
want_wallpaper=""

possible_protocols=("WiFi" "BLE" "Zigbee/6loWPAN")
BLE=""
Zigbee=""
WiFi=""

#=============================== functions ==============================

function init_antennas() {
    
    sysdevpath=$(find /sys/bus/usb/devices/usb*/ -name dev | grep -e 'ttyACM' -e 'ttyUSB')
    syspath="${sysdevpath%/dev}"
    devname="$(udevadm info -q name -p $syspath)"
    [[ "$devname" == "bus/"* ]] && exit

    eval "$(udevadm info -q property --export -p $syspath)"
    [[ -z "$ID_SERIAL" ]] && exit

    #echo "/dev/${devname} - ${ID_SERIAL}"
    echo "${ID_SERIAL}"
}

#========================== installation start ==========================

echo -e "\n"
echo "================================================================="
echo "|     IOTscanner linux's installation script starting ...       |"
echo "================================================================="
echo -e "\n"

#========================= questions to respond =========================

echo "You will have to respond to three questions"

# Does the user use a touch display
flag=0
while [[ $touch_display != "y" ]] && [[ $touch_display != "Y" ]] && [[ $touch_display != "n" ]] && [[ $touch_display != "N" ]]
do
    if [[ $flag == 1 ]]; then
        echo "Character not recognized, try again"
    fi
    flag=1
    echo "Does your device use a touch display for screen (Y/N)"
    read touch_display
done

# Does the user want a service for the software
flag=0
while [[ $build_service != "y" ]] && [[ $build_service != "Y" ]] && [[ $build_service != "n" ]] && [[ $build_service != "N" ]]
do
    if [[ $flag == 1 ]]; then
        echo "Character not recognized, try again"
    fi
    flag=1
    echo "Do you want to create a service who'll launch the app at each OS start (Y/N) (recommanded)"
    read build_service
done

# Does the user want a beautiful wallpaper
flag=0
while [[ $want_wallpaper != "y" ]] && [[ $want_wallpaper != "Y" ]] && [[ $want_wallpaper != "n" ]] && [[ $want_wallpaper != "N" ]]
do
    if [[ $flag == 1 ]]; then
        echo "Character not recognized, try again"
    fi
    flag=1
    echo "Do you want a beautiful wallpaper on your desktop (Y/N)"
    read want_wallpaper
done

#========================= Antennas recognition =========================

echo -e "\n"
echo -e "${RED}/! \\ You may have configured all the antennas you want to use before this step /! \\ ${ENDCOLOR}"
echo -e "${RED}Antennas'll be recognized and saved in the software code, please follow thoses steps carefully. ${ENDCOLOR}"
echo "If antennas are NOT configured, please quit (ctrl + c). Otherwise continue"
echo "If you make a configuration error, please restart the installation"
read -r -p "Press any key to continue..." key

# Number of antennas used
echo -e "\n"
echo "Please enter the amount of antennas you'll have"
read -r -p "Enter a number : " nb_antennas
while ! [[ "$nb_antennas" =~ ^[0-9]+$ || "$nb_antennas" =~ ^[-][0-9]+$  ]]
do
    read -r -p "Enter a number : " nb_antennas
done

# Get antenna's name
i=0
while ! [[ $i == $nb_antennas ]]
do
    echo -e "\n${GREEN}Please connect an antenna on the USB slot ${ENDCOLOR}"
    read -r -p "When it's done, press any key to continue..." key
    
    echo -e "\nSelect the protocol for the connected antenna :"

    # Display a sentence of selectable protocols
    y=1
    sentence="| "
    for protocol in ${possible_protocols[@]}; do
        sentence+="${y}. ${protocol} | "
        y=$((y+1))
    done
    echo $sentence
    
    # Choose a protocol
    echo -e "\n"
    echo "Choose a protocol by entering a number"
    test=1
    while [[ $test == 1 ]]
    do
        read -r -p "Enter a number : " selected_protocol

        if ! [[ "$selected_protocol" =~ ^[0-9]+$ || "$selected_protocol" =~ ^[-][0-9]+$ ]]; then
            test=1
        else
            test=0
        fi

        if ! [[ $selected_protocol -le ${#possible_protocols[@]} ]]; then
            test=1
        else
            test=$((test+0))
        fi
    done

    # Get antenna name
    antenna_name=$(init_antennas)

    # Assign antenna name to a protocol (1.WiFi, 2.BLE, 3.Zigbee/6loWPAN)
    if [[ $selected_protocol == 1 ]]; then
        WiFi="${antenna_name}"
        p="WiFi"
    elif [[ $selected_protocol == 2 ]]; then
        BLE="${antenna_name}"
        p="BLE"
    elif [[ $selected_protocol == 3 ]]; then
        Zigbee="${antenna_name}"
        p="Zigbee/6loWPAN"
    else
        echo "ERROR => selected_protocol var's value not recognized"
        echo "Script is stopping ..."
        exit
    fi

    echo -e "${GREEN}\nProtocol ${p} get antenna ${antenna_name} ${ENDCOLOR}"

    echo -e "\nAntenna is configured, now deconnect it"
    echo "If another antenna must be configure, this step'll restart. Please enter a new antenna when asked"
    read -r -p "Press any key to continue..." key

    i=$((i+1))
done

#========================= Os configuration =========================

cd Desktop
sudo apt install xrdp xorg sudo usbutils git curl -y

# Delete the pip security who disable the download of external packages
sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED
python3 -m pip install pip --upgrade

# Importing the github project
git clone https://github.com/SmAlios/IOTScanner.git

# Config for the touch display
# You can see this video who explain how to connect the screen https://youtu.be/MQF3eQTiIpI
if [[ $touch_display -eq "Y" ]]
then
    sudo apt update
    sudo apt upgrade -y
    sudo apt dist-upgrade -y
    sudo apt install raspberrypi-ui-mods -y
    sudo apt install raspberrypi-net-mods -y
else
    echo "You, ve choose to not use a touch display"
fi

# Service creation
if [[ $build_service -eq "Y" ]]
then
    # The service name begin with a "z" to be in the last services to start (old systemv rule)
    sudo rm /etc/systemd/system/ziotscanner.service
    sudo touch /etc/systemd/system/ziotscanner.service

    # Complite the file
    echo "[Unit]" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "Description=Use this app to scan the existing networks in the area" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "After=graphical.target" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "After=systemd-user-sessions.service" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "After=rc-local.service" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "Wants=graphical.target" | sudo tee -a /etc/systemd/system/ziotscanner.service

    echo -e "\n[Service]" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "Type=simple" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "User=$USER" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo 'Environment="DISPLAY=:0"' | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "Environment='XAUTHORITY=/home/$USER/.Xauthority'" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "ExecStart=/home/$USER/Desktop/IOTScanner/main.py $(echo '$')DISPLAY $(echo '$')XAUTHORITY > /tmp/iotlog.log 2>&1" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "WorkingDirectory=/home/$USER/Desktop/IOTScanner" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "Restart=On-Failure" | sudo tee -a /etc/systemd/system/ziotscanner.service

    echo -e "\n[Install]" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "WantedBy=graphical.target" | sudo tee -a /etc/systemd/system/ziotscanner.service

    #create the service
    sudo chmod 644 /etc/systemd/system/ziotscanner.service
    sudo apt install xorg openbox -y
    sudo systemctl daemon-reload
    sudo systemctl enable ziotscanner.service
else
    echo "You, ve choose to not use a service for the app"
fi

# Change wallpaper
if [[ $want_wallpaper -eq "Y" ]]
then
    curl https://raw.githubusercontent.com/SmAlios/IOTScanner/main/wallpaper/rccu.png --output "rccu.png"
    wallpaper="rccu.png"
else
    curl https://www.flixist.com/wp-content/uploads/2020/09/Borat_two_title.jpg --output "very_nice.jpg"
    wallpaper="very_nice.jpg"
fi

cp $wallpaper /home/$USER/Documents/$wallpaper
cd /home/$USER/Documents/
sudo ln -sf /home/$USER/Documents/$wallpaper /etc/alternatives/desktop-background

#========================= Project modifications =========================

cd /home/$USER/Desktop/IOTScanner/
touch logs/logs.log
sudo chown -R $USER:$USER logs
sudo chmod +x main.py
sudo chmod +x init_antennas.sh

# Set tha antennas name. LINES NUMBER CAN CHANGE FOR OTHER SOFTWARE VERSIONS
sed -i "26i\'BLE':'${BLE}'" main.py
sed -i "27i\'Zigbee':'${Zigbee}'" main.py
sed -i "28i\'WiFi':'${WiFi}'" main.py
cd

# Allow the user to restart and shtdown without asking password
sudo echo "$USER ALL=NOPASSWD: /sbin/reboot, /sbin/poweroff" | sudo tee -a /etc/sudoerssed -i "5i\mytext" test.txt

echo -e "\n${GREEN}By purpuse of security, this script'll delete itself"
echo -e "Installation is now complete and device'll restart ${ENDCOLOR}"
sudo shutdown -r +1
rm $0