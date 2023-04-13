#include <Arduino.h>
#include "config.h"

static unsigned long triggerTime = 0;

void PINCTRL_process(void){
  if(triggerTime > 0){
    if((millis() - triggerTime) < (UNLOCK_DURATION * 1000)){
      digitalWrite(SWITCH_PIN, LOW);
    }else{
      digitalWrite(SWITCH_PIN, HIGH);
      triggerTime = 0;
    }
  }  
}


void PINCTRL_trigger(void){
  triggerTime = millis();
}


void PINCTRL_init(void){
  pinMode(SWITCH_PIN, OUTPUT);
  digitalWrite(SWITCH_PIN, HIGH);
  triggerTime = 0;
}
