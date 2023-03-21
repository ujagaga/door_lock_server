#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "http_client.h"
#include "config.h"
#include <ArduinoJson.h>
#include "mqtt.h"


static uint32_t lifesignTriggered = 0;
static uint32_t lifesignTimeout = 0;
static char token[64] = {0};

WiFiClient client;
HTTPClient http;


void pingServer(void){  
  String serverPath = String(LOCK_SERVER_URL) + "/device_ping?token=" + String(token);
  http.begin(client, serverPath.c_str());

  int httpResponseCode = http.GET();
  if (httpResponseCode>0) { 
    String payload = http.getString();
    if(payload.indexOf("ERROR") > 0){
      Serial.println("Ping error:" + payload);
      lifesignTimeout = 0;
    }    
  }
  else {
    Serial.print(serverPath + "\nError code: ");        
    Serial.println(httpResponseCode);
  }
  // Free resources
  http.end();

  lifesignTriggered = millis();
  
}

void HTTPC_init(void){  
  String serverPath = String(LOCK_SERVER_URL) + "/device_login?name=" + DEV_NAME + "&password=" + DEV_PASSWORD;
  http.begin(client, serverPath.c_str());

  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String payload = http.getString();
    Serial.println(payload);
    
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, payload);    

    if(error) {
      Serial.print("Failed to parse JSON response.");
      Serial.println(error.f_str());
    }else{    
      const char* status = doc["status"];
        
      if(strcmp(status, "OK") == 0){
        strcpy(token, doc["token"]);
        lifesignTimeout = doc["timeout"];
        lifesignTimeout *= 1000;

        MQTT_setAuthorization(doc["topic"], doc["trigger"], doc["lifesign"]);
      }
    }
  }else {
    Serial.print(serverPath + "\nError code: ");    
    Serial.println(httpResponseCode);
  }
  // Free resources
  http.end();
}

void HTTPC_process(void){
  if(lifesignTimeout == 0){
    if((millis() - lifesignTriggered) > 2000){
      HTTPC_init();
      lifesignTriggered = millis();
    }
  }else{
    if((millis() - lifesignTriggered) > lifesignTimeout){
      pingServer();
      lifesignTriggered = millis();
    }
  }
}
