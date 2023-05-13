#include <Arduino.h>
#include "config.h"

static unsigned long triggerTime = 0;
static unsigned long beepTime = 0;


void PINCTRL_trigger(void){
  if(triggerTime == 0){
    triggerTime = millis();
  }
}


void PINCTRL_init(void){
  pinMode(SWITCH_PIN, OUTPUT);
  digitalWrite(SWITCH_PIN, LOW);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  
  triggerTime = 0;
}


void PINCTRL_process(void){
  if(triggerTime > 0){
    if((millis() - triggerTime) < (UNLOCK_DURATION * 1000)){
      digitalWrite(SWITCH_PIN, HIGH);
      digitalWrite(LED_PIN, LOW);
    }else{
      digitalWrite(SWITCH_PIN, LOW);
      digitalWrite(LED_PIN, HIGH);
      triggerTime = 0;
    }
  }  
}