#include <Arduino.h>
#include "config.h"

static unsigned long triggerTime = 0;

void PINCTRL_process(void){
  if(triggerTime > 0){
    if((millis() - triggerTime) < (UNLOCK_DURATION * 1000)){
      digitalWrite(SWITCH_PIN, HIGH);
    }else{
      digitalWrite(SWITCH_PIN, LOW);
      triggerTime = 0;
    }
  }  
}


void PINCTRL_trigger(void){
  triggerTime = millis();
}

bool PINCTRL_reset_requested(void){
  return (digitalRead(WIFI_RESET_PIN) == LOW);
}


void PINCTRL_init(void){
  pinMode(SWITCH_PIN, OUTPUT);
  digitalWrite(SWITCH_PIN, HIGH);

  pinMode(ADDITIONAL_GND, OUTPUT);
  digitalWrite(ADDITIONAL_GND, LOW);

  pinMode(WIFI_RESET_PIN, INPUT_PULLUP);
  
  triggerTime = 0;
}
