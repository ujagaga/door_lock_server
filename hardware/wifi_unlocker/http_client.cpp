#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "http_client.h"
#include "config.h"
#include <ArduinoJson.h>
#include "mqtt.h"


static uint32_t lifesignTriggered = 0;
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
      token[0] = 0;
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
  String serverPath = String(LOCK_SERVER_URL) + "/device_login?name=ulazlt19&password=svetapetka";
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
  if(millis() > 10000){
    if((strlen(token) > 20) && (millis() - lifesignTriggered) > (LIFESIGN_TIMEOUT * 1000)){ 
      pingServer();
    }else{
      HTTPC_init();
    }
    lifesignTriggered = millis();
  }
}
