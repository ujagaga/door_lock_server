/* 
 *  Author: Rada Berar
 *  email: ujagaga@gmail.com
 *  
 *  MQTT client module to anounce itself to iot-portal and accept MQTT commands.
 */
#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include "mqtt.h"
#include "wifi_connection.h"
#include "http_client.h"
#include "config.h"
#include "pinctrl.h"


#define CONNECT_TIMEOUT       (10000ul) 

WiFiClient espClient;
PubSubClient mqttclient(espClient);
static char msgBuffer[256] = {0};
static uint32_t connectAttemptTime = 0;
static char clientName[32] = {0};
static char mqttTopic[256] = {0};
static char mqttTrigger[256] = {0};
static char mqttLifesign[256] = {0};


static void callback(char* topic, byte* payload, unsigned int length) {  

  char textMsg[length + 1] = {0};
  for(int i = 0; i < length; i++){
    textMsg[i] = (char)payload[i];        
  }
  
  if(strcmp(textMsg, mqttLifesign) == 0){
    Serial.println("MQTT lifesign");
    HTTPC_confirmLifesign();
  }else if(strcmp(textMsg, mqttTrigger) == 0){
    Serial.println("MQTT trigger");
    PINCTRL_trigger();
  }else{
    Serial.println("Unexpected MQTT message: " + String(textMsg) + "\n    Re-initializing.");
    HTTPC_init();
  }  
}


void MQTT_setAuthorization(const char* topic, const char* trigger, const char* lifesign){  
  if(mqttclient.connected()){
    mqttclient.unsubscribe(mqttTopic);
  }
  strcpy(mqttTopic, topic);
  strcpy(mqttTrigger, trigger);
  strcpy(mqttLifesign, lifesign);

  Serial.print("Topic:    ");
  Serial.println(mqttTopic);
  Serial.print("Trigger:  ");
  Serial.println(mqttTrigger);
  Serial.print("Lifesign: ");
  Serial.println(mqttLifesign);
  
  if(mqttclient.connected()){
      mqttclient.disconnect();
  }
}


static void mqtt_connect() {
  if(strlen(mqttTopic) == 0){
    Serial.println("ERROR: MQTT topic not set.");   
    return;
  }
    
  mqttclient.setServer(MQTT_SERVER_HOSTNAME, MQTT_PORT);
  mqttclient.setCallback(callback);
  // Attempt to connect
  if (mqttclient.connect(DEV_NAME)) {
    Serial.println("MQTT connected");
    mqttclient.subscribe(mqttTopic);
  } else {
    Serial.print("ERROR: MQTT failed: ");
    Serial.println(mqttclient.state());
  }  
}


void MQTT_process(){
  if (!mqttclient.connected() && ((millis() - connectAttemptTime) > CONNECT_TIMEOUT)) {     
    // Not connected. Try again.
    mqtt_connect();
    connectAttemptTime = millis();
    
    if(mqttclient.connected() && (msgBuffer[0] != 0)){    
      msgBuffer[0] = 0;
    }    
  }
  
  mqttclient.loop();  
}


bool MQTT_isConnected(void){
  return mqttclient.connected();
}
