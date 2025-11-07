#include "get.h"

String getCommand() {
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        return cmd;
    }
    return "";
}
