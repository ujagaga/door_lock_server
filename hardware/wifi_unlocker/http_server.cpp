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
#include <LittleFS.h>
#include "http_server.h"
#include "wifi_connection.h"
#include "web_socket.h"
#include "config.h"
 #include "wifi_unlocker.h"
// #include "pinctrl.h"


/* Declaring a web server object. */
static ESP8266WebServer webServer(80);

static String getContentType(String filename) { // convert the file extension to the MIME type
  String retType = "text/plain";
  
  if (filename.endsWith(".html")){
    retType = "text/html";
  }else if (filename.endsWith(".css")){
    retType = "text/css";
  }else if (filename.endsWith(".js")){
    retType = "application/javascript";
  }else if (filename.endsWith(".ico")){
    retType = "image/x-icon";
  }else if (filename.endsWith(".png")){
    retType = "image/png";
  }else if (filename.endsWith(".gif")){
    retType = "image/gif";
  }
  return retType;
}

static bool handleFileRead(String path) { // send the right file to the client (if it exists)
  bool retVal = false;
  //Serial.println("handleFileRead: " + path);
  String originalPath = path;
  
  if (path.endsWith("/")){
    // If a folder is requested, send the index file
    path += "index.html";         
  }else if(path.equals("/generate_204") || path.equals("/gen_204")){
    // Sign in request from smartphone
    path = "/index.html";     
  }
  
  String contentType = getContentType(path);            // Get the MIME type
  
  if (LittleFS.exists(path)) {                            // If the file exists
    File file = LittleFS.open(path, "r");                 // Open it
    size_t sent = webServer.streamFile(file, contentType); // And send it to the client
    file.close();                                       // Then close the file again
    
    retVal = true;
  }else{
    Serial.println("LittleFS ERROR: " + originalPath + " not found!");
    
    retVal = false;
  }
  
  return retVal;                                        
}

static void showNotFound(void){
  if (!handleFileRead("/not_found.html")){
    webServer.send(404, "text/plain", "Page not found!");      
  }
}

static void showStatusPage() {    
  Serial.println("showStatusPage");
  String response = "Connection Status:" + MAIN_getStatusMsg();
  webServer.send(200, "text/plain", response);   
}

static void showRedirectPage(void){
  if (!handleFileRead("/redirect.html")){
     showNotFound();        
  }   
}

static void showHome(void){
  if (!handleFileRead("/select_ap.html")){
     showNotFound();        
  }   
}

/* Saves wifi settings to EEPROM */
static void saveWiFi(void){
  String ssid = webServer.arg("s");
  String pass = webServer.arg("p");
  
  if((ssid.length() > 63) || (pass.length() > 63)){
      MAIN_setStatusMsg("Sorry, this module can only remember SSID and a PASSWORD up to 63 bytes long.");
      showRedirectPage(); 
      return;
  } 

  String st_ssid = "";
  String st_pass = "";

  if(ssid.length() > 0){
    bool cmpFlag = true;

    st_ssid = WIFIC_getStSSID();
    st_pass = WIFIC_getStPass();

    if(st_ssid.equals(ssid) && st_pass.equals(pass)){
      MAIN_setStatusMsg("All parameters are already set as requested.");
      showRedirectPage();      
      return;
    }   
  }
  
  WIFIC_setStSSID(ssid);
  WIFIC_setStPass(pass);

  String http_statusMessage;
  
  if(ssid.length() > 3){    
    http_statusMessage = "Saving settings and connecting to SSID: ";
    http_statusMessage += ssid;
  }else{       
    http_statusMessage = "Saving settings and switching to AP mode only.";    
  }
  http_statusMessage += "<br>If you can not connect to this device 20 seconds from now, please, reset it.";

  MAIN_setStatusMsg(http_statusMessage);
  showStatusPage();

  volatile int i;

  /* Keep serving http to display the status page*/
  for(i = 0; i < 100000; i++){
    webServer.handleClient(); 
    ESP.wdtFeed();
  } 

  /* WiFI config changed. Restart to apply. 
   Note: ESP.restart is buggy after programming the chip. 
   Just reset once after programming to get stable results. */
  ESP.restart();
}

void HTTPS_process(void){
  webServer.handleClient(); 
}

void HTTPS_init(void){ 
  webServer.on("/", showHome);
  webServer.on("/favicon.ico", showNotFound);
  webServer.on("/wifisave", saveWiFi);
  
  webServer.onNotFound([]() {                             
    if (!handleFileRead(webServer.uri())){
       showNotFound();        
    }      
  });
  
  webServer.begin();

  if(!LittleFS.begin()){
    Serial.println("LittleFS Initialization failed. Did you enable LittleFS in \"Tools/Flash size\"?");
  }

  Serial.println("\tListing files...");
  Dir dir = LittleFS.openDir("/");
  while (dir.next()) {
      Serial.println(dir.fileName());      
  }
  Serial.println("\tEnd of file list...");
}
