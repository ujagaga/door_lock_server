/* 
 *  Author: Rada Berar
 *  email: ujagaga@gmail.com
 *  
 *  This is the main sketch file. 
 *  It provides a periodic pooling of other services.
 */

#include "http_server.h"
#include "http_client.h"
#include "web_socket.h"
#include "wifi_connection.h"
#include "config.h"
//#include "pinctrl.h"
#include "mqtt.h"


static String statusMessage = "";         /* This is set and requested from other modules. */

void MAIN_setStatusMsg(String msg){
  statusMessage = msg;
}

String MAIN_getStatusMsg(void){
  return statusMessage;
}

void setup(void) {
  /* Need to wait for background processes to complete. Otherwise trouble with gpio.*/
  delay(100);   
  Serial.begin(115200,SERIAL_8N1,SERIAL_TX_ONLY); /* Use only tx, so rx can be used as GPIO */   
  //ESP.eraseConfig();
  pinMode(SWITCH_PIN, OUTPUT);
  // PINCTRL_write(1);  
  WIFIC_init();
  HTTPS_init();
  WS_init();  
  HTTPC_init();
}


void loop(void) {  
  HTTPS_process();  
  WS_process();
//  MQTT_process();
  HTTPC_process();
}
