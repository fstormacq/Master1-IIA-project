#ifndef LOGIC_H
#define LOGIC_H

#pragma once
#include <Arduino.h>

// gère les commandes reçues
void handleCommand(const String &cmd);
void parseAndEnqueue(String msg);
void consumeQueue();

#endif