#include <SoftwareSerial.h>
#include <Hash.h>
#include "http_client.h"
#include "config.h"
#include "pinctrl.h"


SoftwareSerial RFID(RFID_RX_PIN, 99); // (D1, DISABLED) RX and TX

String text;
uint32_t detect_timestamp = 0;
char c;
bool card_detected_flag = false;

void RFID_init(void)
{
  RFID.begin(9600);
}

void RFID_process(void){
  if(RFID.available() > 0) {  
    delay(5);
    c = RFID.read();

    if(text.length() < 13){
      text += c;
    }
    
    if((text.length() == 12) && !card_detected_flag){
      String card_id = text.substring(1, 11) + HASH_SALT; 
      card_detected_flag = true; 

      String hashedCode = sha1(card_id);
      PINCTRL_beep();
      HTTPC_reportCode(hashedCode);
    }   
  
    detect_timestamp = millis();    
  } 

  if((millis() - detect_timestamp) > 1000){
    text = ""; 
    card_detected_flag = false;    
  }
}
