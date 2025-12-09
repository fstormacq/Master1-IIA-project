#include "get.h"
#include <Arduino.h>

bool TEST_MODE = false;

String getCommand() {
    if (TEST_MODE) {
        return "L020C100R50";
    }

    String lastCmd = "";
    
    while (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd.length() > 0) {
            lastCmd = cmd;
        }
    }

    return lastCmd;
}