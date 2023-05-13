#ifndef WIFI_CONNECTION_H
#define WIFI_CONNECTION_H

extern void WIFIC_init(void);
extern void WIFIC_stationMode(void);
extern void WIFIC_APMode(void);
extern void WIFIC_setStSSID(String new_ssid);
extern void WIFIC_setStPass(String new_pass);
extern String WIFIC_getApList(void);
extern String WIFIC_getStSSID(void);
extern String WIFIC_getStPass(void);
extern IPAddress WIFIC_getApIp(void);
extern char* WIFIC_getDeviceName(void);
extern void WIFIC_process(void);

#endif
