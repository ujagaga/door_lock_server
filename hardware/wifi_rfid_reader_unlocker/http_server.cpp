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
#include "code_management.h"


static const char HTML_BEGIN[] PROGMEM = R"(
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta name = "viewport" content = "width = device-width, initial-scale = 1.0, maximum-scale = 1.0, user-scalable=0">
<title>RFID Door Lock</title>
<style>
  body { background-color: white; font-family: Arial, Helvetica, Sans-Serif; Color: #000000; text-align: center;}
  .container{width: 100%;}.center_div{margin:0 auto; max-width: 400px;position:relative;}
  .button{width:200px; padding:5px; border-radius:5px; background-color: orange; text-decoration: none;
  text-align: center; margin: 10px auto;}
  .button a{text-decoration: none; color:white;display:block;}
</style>
</head>
<body>
<div class="container">
<div class="center_div">
<h1>RFID Lock</h1>
)";

static const char HTML_SAVE_BUTTON[] PROGMEM = R"(
<p class="button"><a href="/save_code">Save</a></p>
)";

static const char HTML_CLEAR_BUTTON[] PROGMEM = R"(
<p class="button"><a href="/clear_codes">Clear All Codes</a></p>
)";

static const char HTML_END[] PROGMEM = R"(
</div>
</div>
</body>
</html>
)";


/* Declaring a web server object. */
static ESP8266WebServer webServer(80);


static void showNotFound(void){
  webServer.send(404, "text/plain", "Page not found!");
}


static void showHome(void){
  String response = FPSTR(HTML_BEGIN);

  String unsaved_code = CM_getUnsavedCode();
  int numOfSaved = CM_getNumberOfSavedCodes();

  if(unsaved_code.length() > 10){
    response += unsaved_code;
    response += FPSTR(HTML_SAVE_BUTTON);
  }

  if(numOfSaved > 0){
    response += "<hr><p>Number of saved codes: " + String(numOfSaved) + "</p>";
    response += FPSTR(HTML_CLEAR_BUTTON);
  }
  
  response += FPSTR(HTML_END);
  webServer.send(200, "text/html", response);   
}


static void clearCodes(void){
  CM_clearCodes();
  webServer.sendHeader("Location", String("/?timestamp=" + String(millis())), true);
  webServer.send( 302, "text/plain", "");  
}


static void saveLastCode(void){
  CM_saveLatestCode();
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
