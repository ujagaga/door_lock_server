#include <Arduino.h>
#include <Hash.h>
#include <EEPROM.h>
#include "config.h"


#define EEPROM_SIZE   (CODE_CACHE_SIZE * CODE_LENGTH)
#define CODE_PRINT_DEBOUNCE_TIME  (5000)

String latest_code = "";
int last_code_addr = 0;
uint32_t dump_codes_timestamp = 0;

bool CM_checkCodeSaved(){
  bool code_found_flag = false;
  EEPROM.begin(EEPROM_SIZE);

  for(int c = 0; c < last_code_addr; ++c){
    String read_code = "";
    for(int i = 0; i < CODE_LENGTH; ++i){
      int addr = c * CODE_LENGTH + i;
      read_code += char(EEPROM.read(addr));      
    }

    if(latest_code.equals(read_code)){
      code_found_flag = true;
      break;
    }  
  }
  EEPROM.end();

  return code_found_flag;
}

void CM_showSaved(){
  if((millis() - dump_codes_timestamp) < CODE_PRINT_DEBOUNCE_TIME){
    return;
  }
  
  dump_codes_timestamp = millis();

  EEPROM.begin(EEPROM_SIZE);

  Serial.println("Saved codes:");

  for(int c = 0; c < last_code_addr; ++c){
    String read_code = "";
    for(int i = 0; i < CODE_LENGTH; ++i){
      int addr = c * CODE_LENGTH + i;
      read_code += char(EEPROM.read(addr));      
    }

    Serial.println(read_code);
  }
  EEPROM.end();
}



int CM_getNumberOfSavedCodes(void){
  return last_code_addr;
}


String CM_getUnsavedCode(){
  if(!CM_checkCodeSaved()){
    return latest_code;
  }
  return "";
}


void CM_saveLatestCode(){
  if(!CM_checkCodeSaved()){    
    if((last_code_addr < CODE_CACHE_SIZE) && (latest_code.length() == CODE_LENGTH)){
      EEPROM.begin(EEPROM_SIZE);

      for(int i = 0; i < CODE_LENGTH; ++i){
        int addr = (last_code_addr * CODE_LENGTH) + i;
        EEPROM.write(addr, latest_code[i]);         
      }
      EEPROM.commit();
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


void CM_clearCodes(){
  EEPROM.begin(EEPROM_SIZE);
  for(int c = 0; c < CODE_CACHE_SIZE; ++c){
    for(int i = 0; i < CODE_LENGTH; ++i){
      int addr = c * CODE_LENGTH + i;
      EEPROM.write(addr, 0xff);
    }
  }
  EEPROM.end();
  latest_code = "";
  last_code_addr = 0;
}

void CM_init(void)
{
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
  }
  EEPROM.end();
}

void CM_reportCode(String raw_code){
  String hashed_string = sha1(raw_code + HASH_SALT);
  int end_id = hashed_string.length();
  int start_id = 0;
  if(end_id > CODE_LENGTH){
    start_id = end_id - CODE_LENGTH;
  }

  latest_code = hashed_string.substring(start_id, end_id);           
}
