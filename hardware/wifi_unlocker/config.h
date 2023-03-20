#ifndef CONFIG_H
#define CONFIG_H

#define WIFI_PASS_EEPROM_ADDR   (0)
#define WIFI_PASS_SIZE          (32)
#define SSID_EEPROM_ADDR        (WIFI_PASS_EEPROM_ADDR + WIFI_PASS_SIZE)
#define SSID_SIZE               (32)
#define EEPROM_SIZE             (WIFI_PASS_SIZE + SSID_SIZE)   

/* 19 characters maximum. When we append MAC addr, it will be 31. 
The device fails to create an AP if total AP name is longer than 31 character. */
#define AP_NAME_PREFIX          "LT19_Lock"
#define SWITCH_PIN               2 /* D4 */   
#define UNLOCK_DURATION          (20)
#define LOCK_SERVER_URL         "http://ulaz.drslavica.com"
#define LIFESIGN_TIMEOUT        (60)

#endif
