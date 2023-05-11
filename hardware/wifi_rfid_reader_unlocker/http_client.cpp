#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "http_client.h"
#include "config.h"
#include <ArduinoJson.h>
#include "mqtt.h"
#include "pinctrl.h"
#include "rfid_reader.h"

static uint32_t pingTime = 0;
static uint32_t lifesignTimeout = 0;
static char token[64] = {0};
static bool initialHandshakeDone = false;

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

void HTTPC_reportCode(String code){  
  String serverPath = String(LOCK_SERVER_URL) + "/device_report_nfc_code?token=" + String(token) + "&code=" + code;
  http.begin(client, serverPath.c_str());

  int httpResponseCode = http.GET();
  if (httpResponseCode > 0) { 
    String payload = http.getString();
    if(payload.indexOf("ERROR") > 0){
      Serial.println("Code reporting error:" + payload);      
    }
    if(payload.indexOf("authorized") > 0){
      PINCTRL_trigger();  
      RFID_saveLastCode();  
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

        Serial.print("Token:    ");
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
  if(!initialHandshakeDone){
  
    HTTPC_init();      
    initialHandshakeDone = true;
  
  }else{
    if(pingTime == 0){
      if(MQTT_isConnected()){
        pingServer();
        pingTime = millis();
      }
    }else if((millis() - pingTime) > lifesignTimeout){
      pingServer();
      pingTime = millis();      
    }
  }
}
