#include <Arduino.h>
#include "logic.h"
#include "send.h"
#include "get.h"

unsigned long lastCmdTime = 0;

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(50); // Timeout court pour la lecture série
    setupPins();
}

void loop() {
    // Lire la dernière commande envoyée par le Raspberry
    String cmd = getCommand();

    if (cmd.length() > 0) {
        parseAndApply(cmd);
        lastCmdTime = millis();
    } else if (millis() - lastCmdTime > 200) {
        stopAll();
    }
}