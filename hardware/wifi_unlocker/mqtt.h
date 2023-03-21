#ifndef MQTT_H
#define MQTT_H

extern void MQTT_process(void);
extern void MQTT_setAuthorization(const char* topic, const char* trigger, const char* lifesign);

#endif
