#include <Arduino.h>
#include "get.h"
#include "logic.h"
#include "send.h"

void setup{
    Serial.begin(),
    setupPins();
}

void loop {
    handleVibrationTimer();

}