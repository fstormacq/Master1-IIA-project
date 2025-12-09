#include <Arduino.h>
#include "logic.h"
#include "send.h"
#include "get.h"

void setup() {
    Serial.begin(115200);
    setupPins();
}

void loop() {
    // Lire la dernière commande envoyée par le Raspberry
    String cmd = getCommand();

    if (cmd.length() > 0) {
        parseAndApply(cmd);   // traite immédiatement et écrase l’ancienne
    }

    // Rien d’autre à gérer : la vibration reste active tant qu’on reçoit des commandes
}