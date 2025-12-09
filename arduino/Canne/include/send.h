#pragma once

extern int upperPin;
extern int rightPin;
extern int leftPin;

void setupPins();
void stopAll();
void applyIntensity(int leftVal, int centerVal, int rightVal);