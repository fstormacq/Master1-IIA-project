#include "send.h"


int upperPin = 10;
int rightPin = 11;
int leftPin = 12;

void setupPins() {
    pinMode(upperPin, OUTPUT);
    pinMode(rightPin, OUTPUT);
    pinMode(leftPin, OUTPUT);

    stopAll();
}

unsigned long vibrationEndTime = 0;
bool timedMode = false;

void stopAll() {
    analogWrite(upperPin, 0);
    analogWrite(rightPin, 0);
    analogWrite(leftPin, 0);
    timedMode = false;
    vibrationEndTime = 0;
}

void handleVibrationTimer() {
    if (timedMode && millis() > vibrationEndTime) {
        stopAll();
    }
}

void startTimedVibration(unsigned long durationMs) {
    timedMode = true;
    vibrationEndTime = millis() + durationMs;
}