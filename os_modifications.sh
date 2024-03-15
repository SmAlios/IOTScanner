#!/bin/bash

#only run on linux like os
#this file is originaly made for a raspberrypiOS with GUI equiped with a Touch Display
#if you use another os or device, you must make some modifications of the file
#
#read this if you want to use the software on a raspberry pi
# 1. Download and install the OS with the raspberry software https://www.raspberrypi.com/software/
# 2. You must install the recommanded os for your raspberry pi on an SD card.
#    It's recommanded to use at minimum a 16GB SD card with a minimum speed of 80MB/s in read and/or write
# 3. Download this file (ex : with git) or copy it (ex : via SSH) to you raspberry
# 4. Give the correct execution rights to the file (sudo chmod u+x <filename>)
# 5. Execute the file (./<filename>) and respond to questions

RED="\e[31m"
GREEN="\e[32m"
ENDCOLOR="\e[0m"

USER=$(whoami)
ble_antenna=""
wifi_antenna=""
zigbee_antenna=""

#init setup variables
touch_display=""
build_service=""
want_wallpaper=""

echo "You will have to respond to three questions"

#does the user use a touch display
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

#does the user want a service for the software
flag=0
while [[ $build_service != "y" ]] && [[ $build_service != "Y" ]] && [[ $build_service != "n" ]] && [[ $build_service != "N" ]]
do
    if [[ $flag == 1 ]]; then
        echo "Character not recognized, try again"
    fi
    flag=1
    echo "Do you want to create a service who'll launch the app at each OS start (Y/N)"
    read build_service
done

#does the user want a beautiful wallpaper
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

cd Desktop
sudo apt install xrdp xorg sudo usbutils git curl -y

#delete the pip security who disable the download of external packages
sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED
python3 -m pip install pip --upgrade

#importing the github project
git clone https://github.com/SmAlios/IOTScanner.git

#select the tty* for antennas
echo -e "\n\n"
echo -e "${RED}/! \\ You may have configured the three antennas before this step /! \\ ${ENDCOLOR}"
echo "If the three antennas are NOT configured, please quit (ctrl + c). Otherwise continue"
read -r -p "Press any key to continue..." key

echo -e "\n"
echo -e "\n${GREEN}Please connect the antennas on the USB slots, no matter the order ${ENDCOLOR}"
read -r -p "When it's done, press any key to continue..." key

#config for the touch display

#You can see this video who explain how to connect the screen https://youtu.be/MQF3eQTiIpI
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

#service creation
if [[ $build_service -eq "Y" ]]
then
    #the service name begin with a "z" to be in the last services to start (old systemv rule)
    sudo rm /etc/systemd/system/ziotscanner.service
    sudo touch /etc/systemd/system/ziotscanner.service

    #complite the file
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

#change wallpaper
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

#project modifications
cd /home/$USER/Desktop/IOTScanner/
touch logs/logs.log
sudo chown -R $USER:$USER logs
sudo chmod +x main.py
sudo chmod +x init_antennas.sh
cd

#allow the user to restart and shtdown without asking password
sudo echo "$USER ALL=NOPASSWD: /sbin/reboot, /sbin/poweroff" | sudo tee -a /etc/sudoers

echo -e "\n${GREEN}By purpuse of security, this script'll delete itself"
echo -e "Installation is now complete and device'll restart ${ENDCOLOR}"
sudo shutdown -r +1
rm $0