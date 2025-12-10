#include "send.h"
#include <Arduino.h>

int upperPin = 10;
int rightPin = 11;
int leftPin  = 12;   

void setupPins() {
    pinMode(upperPin, OUTPUT);
    pinMode(rightPin, OUTPUT);
    pinMode(leftPin,  OUTPUT);

    stopAll();
}

void stopAll() {
    analogWrite(upperPin, 0);
    analogWrite(rightPin, 0);
    analogWrite(leftPin,  0);
}

void applyIntensity(int leftVal, int centerVal, int rightVal) {
    analogWrite(leftPin,   leftVal);
    analogWrite(upperPin,  centerVal);
    analogWrite(rightPin,  rightVal);
}