#ifndef SEND_H
#define SEND_H

#pragma once
#include <Arduino.h>

extern int upperPin;
extern int rightPin;
extern int leftPin;

void setupPins();
void stopAll();
void startTimedVibration(unsigned long durationMs);
void handleVibrationTimer();


#endif