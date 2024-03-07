#!/bin/bahs

#only run on linux like os
#this file is originaly made for a raspberrypiOS with GUI equiped with a Touch Display
#if you use another os or device, you must make some modifications of the file

#read this if you want to use the software on a raspberry pi
# 1. Download and install the OS with the raspberry software https://www.raspberrypi.com/software/
# 2. You must install the recommanded os for your raspberry pi on an SD card.
#    It's recommanded to use at minimum a 16GB SD card with a minimum speed of 80MB/s in read and/or write
# 3. Download this file (ex : with git) or copy it (ex : via SSH) to you raspberry
# 4. Give the correct execution rights to the file (sudo chmod u+x <filename>)
# 5. Execute the file (./<filename>) and respond to questions

#please specify the user who'll use the software
USER="<myUser>"
ble_antenna=""
wifi_antenna=""
zigbee_antenna=""

#please specify if you use a touch Display (Y/N)
touch_display=Y

#please specify if you want to create a service who'll launch the app at each OS start (only for linux)  (Y/N)
build_service=Y

#Want a beautiful wallpaper (Y/N)
want_wallpaper=Y

sudo apt install xrdp xorg sudo usbutils git curl -y

#delete the pip security who disable the download of external packages
sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED
python3 -m pip install pip --upgrade

#importing the github project
git clone https://github.com/SmAlios/IOTScanner.git

#select the tty* for antennas
echo "/! \\ You may have configured the three antennas before this step /! \\"
echo "If the three antennas are NOT configured, please quit. Otherwise continue"
puseread -n1 -r -p "Press any key to continue..." key

ls /dev/tty* | grep tty[AU].
echo "Connect the BLE antenna and press any key"
puseread -n1 -r -p "Press any key to continue..." key

ls /dev/tty* | grep tty[AU].
echo "Enter the new terminal (tty) who has appeared"
read ble_antenna

echo "Now, connect the wifi antenna and press any key"
ls /dev/tty* | grep tty[AU].
echo "Enter the new terminal (tty) who has appeared"
read wifi_antenna

echo "Finally, connect the zigbee antenna and press any key"
ls /dev/tty* | grep tty[AU].
echo "Enter the new terminal (tty) who has appeared"
read zigbee_antenna

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
    sudo touch /etc/systemd/system/ziotscanner.service

    #complite the file
    echo "[Unit]" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "Description=Use this app to scan the existing networks in the area" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "After=graphical.target" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "After=systemd-user-sessions.service" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "After=rc-local.service" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "Wants=graphical.target" | sudo tee -a /etc/systemd/system/ziotscanner.service

    echo "[Service]" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "Type=simple" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "User=admin" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo 'Environment="DISPLAY=:0"' | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo 'Environment="XAUTHORITY=/home/admin/.Xauthority"' | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "ExecStart=/home/admin/Desktop/IOTScanner/main.py $\DISPLAY $\XAUTHORITY > /tmp/iotlog.log 2>&1" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "Restart=On-Failure" | sudo tee -a /etc/systemd/system/ziotscanner.service

    echo "[Install]" | sudo tee -a /etc/systemd/system/ziotscanner.service
    echo "WantedBy=graphical.target" | sudo tee -a /etc/systemd/system/ziotscanner.service

    #create the service
    sudo chmod 644 /etc/systemd/system/ziotscanner.service
    sudo apt install xorg openbox -y
    sudo systemctl daemon-reload
    sudo systemctl enable iotscanner.service
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
sudo xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor1/workspace0/last-image -s $wallpaper
rm $wallpaper

#modifications on project
sudo mkdir IOTScanner/logs
sudo touch IOTScanner/logs/logs.log
sudo chown -R $USER:$USER IOTScanner/logs

cd IOTScanner
sed -i "52s/.*/        COM_BLESniffer = $ble_antenna/" main.py
sed -i "53s/.*/        COM_ZigBeeSniffer = $zigbee_antenna/" main.py
sed -i "54s/.*/        COM_WiFiSniffer = $wifi_antenna/" main.py
cd ../

#allow the user to restart and shtdown without asking password
sudo echo "$USER ALL=NOPASSWD: /sbin/reboot, /sbin/poweroff" | sudo tee -a /etc/sudoers

echo "By purpuse of security, this script'll delete itself"
sudo shutdown -r +1
rm $0