#ifndef SEND_H
#define SEND_H

#include <Arduino.h>

// Envoyer des vibrations à la position souhaitée
void vibrate(String position, int intensity, int duration);
void stopAll();
void handleVibrationTimer();

#endif