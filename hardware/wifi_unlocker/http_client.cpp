#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "http_client.h"
#include "config.h"
#include <ArduinoJson.h>
#include "mqtt.h"


static uint32_t pingTime = 0;
static uint32_t lifesignTimeout = 0;
static char token[64] = {0};

WiFiClient client;
HTTPClient http;


void pingServer(void){  
  String serverPath = String(LOCK_SERVER_URL) + "/device_ping?token=" + String(token);
  http.begin(client, serverPath.c_str());

  int httpResponseCode = http.GET();
  if (httpResponseCode > 0) { 
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
}

void HTTPC_confirmLifesign(void){  
  String serverPath = String(LOCK_SERVER_URL) + "/device_lifesign_confirm?token=" + String(token);
  http.begin(client, serverPath.c_str());

  int httpResponseCode = http.GET();
  if (httpResponseCode > 0) { 
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
}

void HTTPC_init(void){  
  String serverPath = String(LOCK_SERVER_URL) + "/device_login?name=" + DEV_NAME + "&password=" + DEV_PASSWORD;
  http.begin(client, serverPath.c_str());

  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String payload = http.getString();
    
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, payload);    

    if(error) {
      Serial.print("Failed to parse JSON response.");
      Serial.println(error.f_str());
    }else{    
      const char* status = doc["status"];
        
      if(strcmp(status, "OK") == 0){
        strcpy(token, doc["token"]);

        Serial.print("Token:\t");
        Serial.println(token);
        
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
  if(pingTime == 0){
    if((millis() - pingTime) > 2000){
      HTTPC_init();
      pingTime = millis();
    }
  }else{
    if((millis() - pingTime) > lifesignTimeout){
      pingServer();
      pingTime = millis();
    }
  }
}
