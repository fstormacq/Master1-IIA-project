#include "send.h"


const int upperPin = 10;
const int rightPin = 11;
const int bottomPin = 12;
const int leftPin = 13;

void setupPins() {
    pinMode(upperPin, OUTPUT);
    pinMode(rightPin, OUTPUT);
    pinMode(bottomPin, OUTPUT);
    pinMode(leftPin, OUTPUT);

    stopAll();
}

unsigned long vibrationEndTime = 0;
int activepin = -1;


void vibrate(String position, int intensity, int duration){
    stopAll();

    if (position == "UPP") {
        analogWrite(upperPin, intensity);
        activepin = upperPin;
    }
    else if (position == "DRO") {
        analogWrite(rightPin, intensity);
        activepin = rightPin;
    }
    else if (position == "BOT") {
        analogWrite(bottomPin, intensity);        
        activepin = bottomPin;
    }
    else if (position == "GAU") {
        analogWrite(leftPin, intensity);
        activepin = leftPin;
    }

    vibrationEndTime = millis() + duration;

}

void stopAll() {
    analogWrite(upperPin, 0);
    analogWrite(rightPin, 0);
    analogWrite(bottomPin, 0);
    analogWrite(leftPin, 0);
    activePin = -1;
    vibrationEndTime = 0;
}

void handleVibrationTimer() {
    if (activePin != -1 && millis() > vibrationEndTime) {
        analogWrite(activePin, 0);
        activePin = -1;
    }
}