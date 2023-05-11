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

String card_id = "";

char code_cache[CODE_CACHE_SIZE][16] = {0};
int wrId = 0;

bool check_code_cached(){
  for(int i = 0; i < CODE_CACHE_SIZE; ++i){
    if(code_cache[i][0] == 0){
      return false;
    }
    
    String test_code = String(code_cache[i]);
    if (test_code.equals(card_id)){
      return true;
    }
  }
  return false;
}

void RFID_clear_cache(){
  for(int i = 0; i < CODE_CACHE_SIZE; ++i){
    code_cache[i][0] = 0;   
  } 
}

void RFID_saveLastCode(){
  if(!check_code_cached() && (wrId < CODE_CACHE_SIZE)){
    card_id.toCharArray(code_cache[wrId], 15);
    wrId++;
  }
}

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
      card_id = text.substring(1, 11);
      card_detected_flag = true; 

      PINCTRL_beep();
      
      if(check_code_cached()){
        Serial.println("Cached");
        PINCTRL_trigger();
      }else{
        Serial.println("Reported");
        String hashedCode = sha1(card_id + HASH_SALT);
        HTTPC_reportCode(hashedCode);
      }
    }   
  
    detect_timestamp = millis();    
  } 

  if((millis() - detect_timestamp) > 1000){
    text = ""; 
    card_detected_flag = false;    
  }
}
