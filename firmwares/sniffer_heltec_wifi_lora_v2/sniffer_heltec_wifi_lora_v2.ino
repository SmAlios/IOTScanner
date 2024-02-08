// WiFi Network Discovery inspired by the available example in the library Arduino ESP32: https://github.com/espressif/arduino-esp32/tree/master/libraries/WiFi/examples/WiFiScan
// WiFi Packet Sniffing inspired by the provided code: https://github.com/ESP-EOS/ESP32-WiFi-Sniffer
// ESP32 documentation available at: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/
#include "driver/gpio.h"
#include "esp_wifi.h"
#include "esp_wifi_types.h"
#include "esp_system.h"
#include "esp_event.h"
#include "esp_event_loop.h"
#include "freertos/FreeRTOS.h"
#include "nvs_flash.h"
#include "WiFi.h"

#include "esp_netif.h"

#define WIFI_SCAN_MIN_PERIOD (30000) // [ms]
#define WIFI_CHANNEL_MIN_SWITCH_INTERVAL (500) // [ms]
#define WIFI_CHANNEL_MAX_SWITCH_INTERVAL (700) // [ms]
#define WIFI_CHANNEL_MAX (13)

/* = GLOBAL VARIABLES ====================================================================== */
bool channel_hopping_mode = true;
long last_scan_millis = 0;
long scan_period = 0;
uint8_t channel = 1;
static wifi_country_t wifi_country = { .cc = "CN", .schan = 1, .nchan = 13 };

/* = STRUCTURES ============================================================================ */
// Data Frame Header Structure
typedef struct { 
  unsigned frame_ctrl : 16;
  unsigned duration_id : 16;
  uint8_t addr1[6];
  uint8_t addr2[6];  
  uint8_t addr3[6];  
  unsigned sequence_ctrl : 16;
  uint8_t addr4[6];  
} wifi_ieee80211_mac_data_hdr_t;

// Management Frame Header Structure
typedef struct { 
  unsigned frame_ctrl : 16;
  unsigned duration_id : 16;
  uint8_t addr1[6]; // < destination address  
  uint8_t addr2[6]; // < source address  
  uint8_t BSSID[6];  
  unsigned sequence_ctrl : 16;
} wifi_ieee80211_mac_mgmt_hdr_t;

// Frame Header Structure
typedef struct{
  union{
    wifi_ieee80211_mac_mgmt_hdr_t mgmt;
    wifi_ieee80211_mac_data_hdr_t data;
  }header;
}wifi_ieee80211_mac_hdr_t;

// Frame Structure
typedef struct {
  wifi_ieee80211_mac_hdr_t hdr; // header
  uint8_t payload[0];  // paylaod
} wifi_ieee80211_frame_t;

/* Promiscious Info Structure
typedef struct {
  wifi_pkt_rx_ctrl_t rx_ctrl; // < metadata from PHY layer 
  uint8_t payload[0];         // < frame
} wifi_promiscuous_pkt_t;
*/

/* = WIFI SCAN FUNCTIONS =================================================================== */
void wifi_network_formater(int networkItem) {
  // channel, RSSI, SSID, BSSID
  printf("N,%d,%d,%s,%s\n",
         WiFi.channel(networkItem),
         WiFi.RSSI(networkItem),
         WiFi.SSID(networkItem).c_str(),
         WiFi.BSSIDstr(*(WiFi.BSSID(networkItem))).c_str());
}

/* = WIFI SNIFFER FUNCTIONS ================================================================ */
esp_err_t event_handler(void *ctx, system_event_t *event) {
  return ESP_OK;
}

void setup_wifi_sniffer(void) {
  nvs_flash_init();
  esp_netif_init();
  ESP_ERROR_CHECK(esp_event_loop_init(event_handler, NULL));
  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  esp_wifi_init(&cfg);
  esp_wifi_set_country(&wifi_country);
  esp_wifi_set_storage(WIFI_STORAGE_RAM);
  esp_wifi_set_mode(WIFI_MODE_NULL);
  esp_wifi_start();
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_promiscuous_rx_cb(&wifi_frame_handler);  
}

void wifi_frame_handler(void *buff, wifi_promiscuous_pkt_type_t type) {
  if(type == WIFI_PKT_CTRL || type == WIFI_PKT_MISC){
    return;
  }
  const wifi_promiscuous_pkt_t *raw_data = (wifi_promiscuous_pkt_t *)buff;
  const wifi_pkt_rx_ctrl_t *metadata = &raw_data->rx_ctrl;
  const wifi_ieee80211_frame_t *frame = (wifi_ieee80211_frame_t*) raw_data->payload;
  if(type == WIFI_PKT_MGMT){
    const wifi_ieee80211_mac_mgmt_hdr_t* header = (const wifi_ieee80211_mac_mgmt_hdr_t*) &frame->hdr;
    printf("H,%u,%d,%02x:%02x:%02x:%02x:%02x:%02x,MGMT\n", metadata->channel, (int8_t)metadata->rssi, header->addr2[0], header->addr2[1], header->addr2[2],header->addr2[3], header->addr2[4], header->addr2[5]);
  }
  else if (type == WIFI_PKT_DATA) {
    const wifi_ieee80211_mac_data_hdr_t *header = (const wifi_ieee80211_mac_data_hdr_t*)&frame->hdr;
    printf("H,%u,%d,%02x:%02x:%02x:%02x:%02x:%02x,DATA\n", metadata->channel, (int8_t)metadata->rssi, header->addr2[0], header->addr2[1], header->addr2[2],header->addr2[3], header->addr2[4], header->addr2[5]);
  } 
}


/* = SETUP ========================================================================= */
// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(115200);
  setup_wifi_sniffer();
  delay(1000);
}

/* = LOOP ========================================================================= */
// the loop function runs over and over again forever
void loop() {

  // -------------------
  // SERIAL READ 
  // -------------------
  // check if there is data comming in the serial
  if (Serial.available()) {  
    int i = Serial.parseInt();
    if (i > 0 && i <= WIFI_CHANNEL_MAX) {  // sniff a specific channel in the range [1, 13]
      channel = (uint8_t)i;
      esp_wifi_set_channel(channel, WIFI_SECOND_CHAN_NONE);
      channel_hopping_mode = false;
    } else if (i == -1) {  // sniff all channels
      channel_hopping_mode = true;
    }
    delay(10);
  }

  // -------------------
  // CHANNEL HOPPING
  // -------------------
  // check if  channel hopping mode enabled
  if (channel_hopping_mode) {
    long random_switch_interval = random(WIFI_CHANNEL_MIN_SWITCH_INTERVAL, WIFI_CHANNEL_MAX_SWITCH_INTERVAL);
    vTaskDelay(random_switch_interval / portTICK_PERIOD_MS);
    esp_wifi_set_channel(channel, WIFI_SECOND_CHAN_NONE);
    channel = (channel % WIFI_CHANNEL_MAX) + 1; 
  }

  // -------------------
  // WIFI NETWORKS SCAN
  // -------------------
  // regularly trigger Wi-Fi network scan (between 30 and 35 [s])
  long current_millis = millis();
  if (current_millis - last_scan_millis > scan_period) {
    WiFi.scanNetworks(true /*async*/, true /*show_hidden*/, true /*passive_scan*/, 500 /*max_ms_per_chan*/, 0 /*channel*/, nullptr /*ssid*/, nullptr /*bssid*/);
    last_scan_millis = current_millis;
    scan_period = random(WIFI_SCAN_MIN_PERIOD, 5000);  // Add some randomness in the scan period
  }
  // check if Wi-Fi network scan completed
  int n = WiFi.scanComplete();  // return scan state in Async mode: -1 if scan not finished, -2 if scan not triggered
  if (n >= 0) {
    for (int i = 0; i < n; i++) {
      wifi_network_formater(i);
    }
    WiFi.scanDelete();  // delete last scan result from RAM
    esp_wifi_set_channel(channel, WIFI_SECOND_CHAN_NONE); // set back the channel before network scan started
  }
}