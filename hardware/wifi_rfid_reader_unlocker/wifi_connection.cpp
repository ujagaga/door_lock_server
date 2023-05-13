#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include "config.h"
#include <DNSServer.h> 


const byte DNS_PORT = 53;
static IPAddress apIP(192, 168, 1, 1);
DNSServer dnsServer;

void WIFIC_init(void){  
  Serial.println("\nStarting AP");  
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
}


void WIFIC_process(void){
  dnsServer.processNextRequest();
}
