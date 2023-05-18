#include <SoftwareSerial.h>
#include <Hash.h>
#include <EEPROM.h>
#include "config.h"
#include "pinctrl.h"
#include "wifi_connection.h"


#define EEPROM_SIZE   (CODE_CACHE_SIZE * CODE_LENGTH)

SoftwareSerial RFID(RFID_RX_PIN, 99); // (D1, DISABLED) RX and TX

String text;
uint32_t detect_timestamp = 0;
uint32_t detect_start_timestamp = 0;
bool card_detected_flag = false;
int last_code_addr = 0;

String card_id = "";


static void setLastSavedCodeLocation(){
  EEPROM.begin(EEPROM_SIZE);

  last_code_addr = 0;
  bool blank_found = false;
  for(int c = 0; (c < CODE_CACHE_SIZE) && !blank_found; ++c){
    String read_code = "";
    for(int i = 0; i < CODE_LENGTH; ++i){
      int addr = c * CODE_LENGTH + i;
      read_code += char(EEPROM.read(addr));
      if((i == 2) && (read_code[0] == 0xff) && (read_code[1] == 0xff) && (read_code[2] == 0xff) ){
        // This is a blank location
        last_code_addr = c;
        blank_found = true;
        break;
      }
    }

    if(last_code_addr != 0){

    }
  }
  EEPROM.end();
}


static bool checkCodeSaved(){
  bool code_found_flag = false;
  EEPROM.begin(EEPROM_SIZE);

  for(int c = 0; c < last_code_addr; ++c){
    String read_code = "";
    for(int i = 0; i < CODE_LENGTH; ++i){
      int addr = c * CODE_LENGTH + i;
      read_code += char(EEPROM.read(addr));      
    }

    if(card_id.equals(read_code)){
      code_found_flag = true;
      break;
    }  
  }
  EEPROM.end();

  return code_found_flag;
}


bool RFID_isEepromClear(void){
  return last_code_addr == 0;
}


String RFID_getUnsavedCode(){
  if(!checkCodeSaved()){
    return card_id;
  }
  return "";
}


void RFID_saveLastCode(){
  if(!checkCodeSaved()){    
    if((last_code_addr < CODE_CACHE_SIZE) && (card_id.length() == CODE_LENGTH)){
      EEPROM.begin(EEPROM_SIZE);

      for(int i = 0; i < CODE_LENGTH; ++i){
        int addr = last_code_addr + i;
        EEPROM.write(addr, card_id[i]); 
      }       

      EEPROM.end();
      last_code_addr++;   
      Serial.println("Saved code.");   
    }else{
      Serial.println("Error: memory full.");      
    }
  }else{
    Serial.println("Error: code already saved.");
  }
}


void RFID_clearCodes(){
  EEPROM.begin(EEPROM_SIZE);
  for(int c = 0; c < CODE_CACHE_SIZE; ++c){
    for(int i = 0; i < CODE_LENGTH; ++i){
      int addr = c * CODE_LENGTH + i;
      EEPROM.write(addr, 0xff);
    }
  }
  EEPROM.end();
  card_id = "";
  last_code_addr = 0;
}

void RFID_init(void)
{
  setLastSavedCodeLocation();
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

      String hashed_string = sha1(detected_code + HASH_SALT);
      int end_id = hashed_string.length();
      int start_id = 0;
      if(end_id > CODE_LENGTH){
        start_id = end_id - CODE_LENGTH;
      }

      card_id = hashed_string.substring(start_id, end_id);     
      
      if(checkCodeSaved()){
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
