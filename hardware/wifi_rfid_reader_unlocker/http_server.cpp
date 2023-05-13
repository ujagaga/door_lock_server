/* 
 *  Author: Rada Berar
 *  email: ujagaga@gmail.com
 *  
 *  HTTP server which generates the web browser pages. 
 */
 
#include <ESP8266WebServer.h>
#include <EEPROM.h>
#include <ESP8266HTTPClient.h>
#include <pgmspace.h>
#include "http_server.h"
#include "wifi_connection.h"
#include "config.h"
#include "rfid_reader.h"


static const char HTML_BEGIN[] PROGMEM = R"(
<!DOCTYPE HTML>
<html>
  <head>
    <meta name = "viewport" content = "width = device-width, initial-scale = 1.0, maximum-scale = 1.0, user-scalable=0">
    <title>RFID Door Lock</title>
    <style>
      body { background-color: white; font-family: Arial, Helvetica, Sans-Serif; Color: #000000; }
      .contain{width: 100%;}.center_div{margin:0 auto; max-width: 400px;position:relative;}
    </style>
  </head>
  <body>
  <h1>RFID Door Lock</h1>
)";

static const char HTML_END[] PROGMEM = "</body></html>";


/* Declaring a web server object. */
static ESP8266WebServer webServer(80);


static void showNotFound(void){
  webServer.send(404, "text/plain", "Page not found!");
}


static void showHome(void){
  String response = FPSTR(HTML_BEGIN);
  response += RFID_getUnsavedCode();
  response += FPSTR(HTML_END);
  webServer.send(200, "text/html", response);   
}


static void clearCodes(void){
  RFID_clearCodes();
  webServer.sendHeader("Location", String("/?timestamp=" + String(millis())), true);
  webServer.send( 302, "text/plain", "");  
}


static void saveLastCode(void){
  RFID_saveLastCode();
  webServer.sendHeader("Location", String("/?timestamp=" + String(millis())), true);
  webServer.send( 302, "text/plain", "");  
}


void HTTPS_process(void){
  webServer.handleClient(); 
}


void HTTPS_init(void){ 
  webServer.on("/", showHome);
  webServer.on("/clear_codes", clearCodes);
  webServer.on("/save_code", saveLastCode);
  webServer.on("/favicon.ico", showNotFound);  
  webServer.onNotFound(showNotFound);
  
  webServer.begin();
}
