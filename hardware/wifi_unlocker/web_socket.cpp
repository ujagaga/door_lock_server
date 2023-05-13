/* 
 *  Author: Rada Berar
 *  email: ujagaga@gmail.com
 *  
 *  WebSocket server provides realtime synchronization between all connected clients and accepts web browser commands.
 */
#include <ArduinoJson.h>
#include <WebSocketsServer.h>
#include "wifi_connection.h"
#include "http_server.h"
#include "wifi_unlocker.h"


WebSocketsServer wsServer = WebSocketsServer(81);


void WS_process(){  
  wsServer.loop();   
}


void WS_broadcast(String msg){
  wsServer.broadcastTXT(msg); 
}


static void serverEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length)
{ 
  if(type == WStype_TEXT){
    //Serial.printf("[%u] get Text: %s\r\n", num, payload);
    char textMsg[length];
    for(int i = 0; i < length; i++){
      textMsg[i] = payload[i];          
    }
        
    DynamicJsonDocument doc(128);
    DeserializationError error = deserializeJson(doc, textMsg);    

    // Test if parsing succeeds.
    if (!error) {
      JsonObject root = doc.as<JsonObject>();            
            
      if(root.containsKey("APLIST")){  
        String APList = "{\"APLIST\":\"" + WIFIC_getApList() + "\"}";
        wsServer.sendTXT(num, APList);   
      }
      
      if(root.containsKey("STATUS")){
        String msg = "{\"STATUS\":\"" + MAIN_getStatusMsg() + "\"}";      
        wsServer.broadcastTXT(msg);          
      }      
    }      
  } 
}


void WS_init(){
  wsServer.begin(); 
  wsServer.onEvent(serverEvent);  
}
