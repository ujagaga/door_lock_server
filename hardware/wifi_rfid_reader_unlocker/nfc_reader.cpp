#include <SPI.h>
#include <MFRC522.h>
#include "config.h"
#include "pinctrl.h"
#include "wifi_connection.h"
#include "code_management.h"


MFRC522 rfid(NFC_SS_PIN, NFC_RST_PIN);
MFRC522::MIFARE_Key key;

byte nuidPICC[4];


String byteIdToString(){
  String result = "";
  String hexstring = "";

  for(int i = 0; i < 4; i++) {
    if(nuidPICC[i] < 0x10) {
      hexstring += '0';
    }

    hexstring += String(nuidPICC[i], HEX);
  }

  // Serial.println(hexstring);

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

}

void NFC_process(){
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()){
    MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);

    if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI && piccType != MFRC522::PICC_TYPE_MIFARE_1K && piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
      Serial.println(F("Your tag is not of type MIFARE Classic."));
      return;
    }

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
  
}



