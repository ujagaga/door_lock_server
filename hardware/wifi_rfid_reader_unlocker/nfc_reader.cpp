#include <SPI.h>
#include <MFRC522.h>
#include "config.h"
#include "pinctrl.h"
#include "wifi_connection.h"
#include "code_management.h"

#define REINIT_TIMEOUT  (6*60*60*1000)

MFRC522 rfid(NFC_SS_PIN, NFC_RST_PIN);
MFRC522::MIFARE_Key key;

byte nuidPICC[4];
static uint32_t detect_timestamp = 0;
static uint32_t init_timestamp = 0;

String byteIdToString(){
  String result = "";
  String hexstring = "";

  for(int i = 0; i < 4; i++) {
    if(nuidPICC[i] < 0x10) {
      hexstring += '0';
    }

    hexstring += String(nuidPICC[i], HEX);
  }

  Serial.println(hexstring);

  return hexstring;
}


void NFC_init(void)
{
  SPI.begin();
  rfid.PCD_Init();
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  Serial.println();
  Serial.print(F("NFC Reader :"));
  rfid.PCD_DumpVersionToSerial();

  init_timestamp = millis();
}

void NFC_process(){
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()){    

    detect_timestamp = millis(); 

    // MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);

    // if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI && piccType != MFRC522::PICC_TYPE_MIFARE_1K && piccType != MFRC522::PICC_TYPE_MIFARE_4K && piccType != MFRC522::PICC_TYPE_ISO_14443_4) {
    //   Serial.println(F("Your tag is not of type MIFARE Classic."));
    //   return;
    // }

    if (rfid.uid.uidByte[0] != nuidPICC[0] || rfid.uid.uidByte[1] != nuidPICC[1] || rfid.uid.uidByte[2] != nuidPICC[2] || rfid.uid.uidByte[3] != nuidPICC[3] ) {
      for (byte i = 0; i < 4; i++) {
        nuidPICC[i] = rfid.uid.uidByte[i];
      }

      String detected_code = byteIdToString();

      CM_reportCode(detected_code);
      if(CM_checkCodeSaved()){
        PINCTRL_beep(true);
        PINCTRL_trigger();
      }else{
        PINCTRL_beep(false);
        WIFIC_startAP();
      }
    }

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }
  
  if((millis() - detect_timestamp) > 1000){
    nuidPICC[0] = 0;
    nuidPICC[3] = 0;

    if((millis() - init_timestamp) > REINIT_TIMEOUT){
      NFC_init();
    }
  }   
}



