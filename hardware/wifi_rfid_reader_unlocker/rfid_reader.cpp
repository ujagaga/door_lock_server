#include <SoftwareSerial.h>
#include "config.h"
#include "pinctrl.h"
#include "wifi_connection.h"
#include "code_management.h"


SoftwareSerial RFID(RFID_RX_PIN, 99); // (D1, DISABLED) RX and TX

static String text;
static uint32_t detect_timestamp = 0;
static uint32_t detect_start_timestamp = 0;
static bool card_detected_flag = false;

void RFID_init(void)
{
  RFID.begin(9600);
}


void RFID_process(void){
  if(RFID.available() > 0) {  
    delay(5);
    char ch = RFID.read();

    if(text.length() < 13){
      text += ch;
    }
    
    if((text.length() == 12) && !card_detected_flag){
      detect_start_timestamp = millis();
      String detected_code = text.substring(1, 11);
      card_detected_flag = true; 

      CM_reportCode(detected_code);
            
      if(CM_checkCodeSaved()){
        PINCTRL_beep(true);
        PINCTRL_trigger();
      }else{
        PINCTRL_beep(false);
        WIFIC_startAP();
      }
    }   
  
    detect_timestamp = millis();    
  } 

  if((millis() - detect_timestamp) > 1000){
    text = ""; 
    card_detected_flag = false;    
  }

  if(card_detected_flag && ((millis() - detect_start_timestamp) > 5000)){
    WIFIC_startAP();
  }
}
