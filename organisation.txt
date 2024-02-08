IoT Hound



# Code Organization
``` text
IoT Hound
├── devices/                    
│   ├── device.py               << class representation of a device
│   └── network.py              << class representation of a network
├── firmwares/   
│   ├── LICENCE.txt                     
│   ├── sniffer_heltec_wifi_lora_v2.ino              << firmware for sniffing WiFi frames  
│   ├── sniffer_nrf52840dongle_802154.hex            << firmware for sniffing IEEE 802.15.4 frames 
│   └── sniffer_nrf52840dongle_ble.hex               << firmware for sniffing BLE frames for Nordic Semiconductors device
|   └── nrf_sniffer_for_bluetooth_le_v4.1.1.uf2      << firmware for sniffing BLE frames for Makerdiary device
├── gui/                        
│   ├── device_gui.py           << contain DeviceRow, DeviceTable, SeizedDeviceRow and SeizedDeviceTable classes  
│   ├── gui.py                  << GUI elements
│   ├── network_gui.py          << contain NetworkRow and NetworkTable classes
│   └── scrollable_frame.py     << custom scrollable frame widget
├── logs/    
│   ├── logger.py               << logger implementation
│   └── logs.log                << log file
├── sniffers/                   
│   ├── BLE_Sniffer.py          << class representation of a BLE Sniffer
│   ├── Sniffer.py              << class representation of a Sniffer
│   ├── WiFi_Sniffer.py         << class representation of a WiFi Sniffer
│   └── ZigBee_Sniffer.py       << class representation of a ZigBee Sniffer
├── utils/
│   ├── Exceptions.py           << from Sniffer API 
│   ├── Filelock.py             << from Sniffer API 
│   ├── LICENCE.txt             << from Sniffer API
│   ├── Notifications.py        << from Sniffer API 
│   ├── Packet.py               << from Sniffer API 
│   ├── Types.py                << from Sniffer API 
│   └── UART.py                 << from Sniffer API 
└── main.py                     << entry point
```

