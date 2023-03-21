/* 
 *  Author: Rada Berar
 *  email: ujagaga@gmail.com
 *  
 *  MQTT client module to anounce itself to iot-portal and accept MQTT commands.
 */
#include <PubSubClient.h>
#include <mDNSResolver.h>
#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
//#include "pinctrl.h"
#include "mqtt.h"
#include "wifi_connection.h"
#include "http_client.h"
#include "config.h"

#define CONNECT_TIMEOUT       (10000ul) 

WiFiClient espClient;
PubSubClient mqttclient(espClient);
static char msgBuffer[256] = {0};
static uint32_t connectAttemptTime = 0;
static char clientName[32] = {0};
static IPAddress mqttServerIp;
static char mqttTopic[256] = {0};
static char mqttTrigger[256] = {0};
static char mqttLifesign[256] = {0};


WiFiUDP wifiudp;
mDNSResolver::Resolver resolver(wifiudp);
  
static void resolve_mDNS(){
  mqttServerIp = resolver.search(MQTT_SERVER_HOSTNAME);  
}

static void callback(char* topic, byte* payload, unsigned int length) {  

  char textMsg[length + 1] = {0};
  for(int i = 0; i < length; i++){
    textMsg[i] = (char)payload[i];        
  }

  Serial.println(textMsg);
  
//  StaticJsonDocument<128> doc;
//  DeserializationError error = deserializeJson(doc, textMsg);    
//
//  // Test if parsing succeeds.
//  if (!error) {
//    JsonObject root = doc.as<JsonObject>();
//    
//    if(root.containsKey("current")){
//      JsonArray array = root["current"].as<JsonArray>();
//      for(JsonVariant v : array) {
//          int value = v.as<int>();
//          PINCTRL_write(value); 
//      }
//    }
//  }
}


void MQTT_setAuthorization(const char* topic, const char* trigger, const char* lifesign){  
  if(mqttclient.connected()){
    mqttclient.unsubscribe(mqttTopic);
  }
  strcpy(mqttTopic, topic);
  strcpy(mqttTrigger, trigger);
  strcpy(mqttLifesign, lifesign);

  Serial.print("Topic:");
  Serial.println(mqttTopic);
  Serial.print("Trigger:");
  Serial.println(mqttTrigger);
  Serial.print("Lifesign:");
  Serial.println(mqttLifesign);
  
  if(mqttclient.connected()){
      mqttclient.disconnect();
  }
}



static void mqtt_connect() {
  if(mqttServerIp == IPADDR_NONE){
    resolve_mDNS();
  }

  if(mqttServerIp == IPADDR_NONE){
    Serial.println("ERROR: MQTT server IP could not be resolved.");   
    return;
  }

  if(strlen(mqttTopic) == 0){
    Serial.println("ERROR: MQTT topic not set.");   
    return;
  }
    
  mqttclient.setServer(mqttServerIp, PORT);
  mqttclient.setCallback(callback);
  // Attempt to connect
  if (mqttclient.connect(DEV_NAME)) {
    Serial.println("connected");
    mqttclient.subscribe(mqttTopic);
  } else {
    Serial.print("MQTT failed. Server IP:");   
    Serial.println(mqttServerIp);
    Serial.print("ERROR:");
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
