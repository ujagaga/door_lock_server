#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include "config.h"
#include <DNSServer.h> 


const byte DNS_PORT = 53;
static IPAddress apIP(192, 168, 1, 1);
DNSServer dnsServer;
static uint32_t ap_start_time = 0;

void WIFIC_init(void){ 
  WiFi.mode(WIFI_AP);  
  WiFi.begin();
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  
  String wifi_statusMessage;

  if(WiFi.softAP(AP_NAME, AP_PASS)){
    wifi_statusMessage = "Running in AP mode. SSID: " + String(AP_NAME) + ", IP:" + apIP.toString();  
  }else{
    wifi_statusMessage = "Failed to setup AP";
  }
  Serial.println(wifi_statusMessage); 

  dnsServer.start(DNS_PORT, "*", apIP); // DNS spoofing (Only for HTTP)
  ap_start_time = millis();
}


void WIFIC_startAP(void){    
  if(ap_start_time == 0){
    Serial.println("\nStarting AP");
    WIFIC_init();
  }else{
    ap_start_time = millis();
  }
}


void WIFIC_process(void){
  dnsServer.processNextRequest();
  if((ap_start_time > 0) && ((millis() - ap_start_time) > MAX_AP_TIME)){
    WiFi.mode(WIFI_OFF);
    ap_start_time = 0;
    Serial.println("Shutting down AP."); 
  }
}

