/* 
 *  Author: Rada Berar
 *  email: ujagaga@gmail.com
 *  
 *  This is the main sketch file. 
 *  It provides a periodic pooling of other services.
 */

#include "http_server.h"
#include "wifi_connection.h"
#include "config.h"
#include "pinctrl.h"
#include "rfid_reader.h"
#include "code_management.h"
#include "nfc_reader.h"


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
  Serial.println("*******");  
  //ESP.eraseConfig();  
  PINCTRL_init();  
  WIFIC_init();
  HTTPS_init();
  CM_init();
  RFID_init();
  NFC_init();
}


void loop(void) {  
  HTTPS_process();  
  PINCTRL_process();
  RFID_process();
  NFC_process();
  WIFIC_process();
}
