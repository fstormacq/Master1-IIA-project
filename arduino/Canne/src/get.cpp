#include "get.h"
#include <Arduino.h>

bool TEST_MODE = false;

String getCommand() {
    if (TEST_MODE) {
        // Exemple de test manuel
        return "L100 C100 R50";
    }

    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        return cmd;
    }

    return "";
}