#include "logic.h"
#include "send.h"

void handleCommand(const String &cmd) {
    int intensity = 0;
    int duration = 0;

    if (cmd.startsWith("GAU")) {
        sscanf(cmd.c_str(), "GAU %d %d", &intensity, &duration);
        vibrate("GAU", intensity, duration);
    }
    else if (cmd.startsWith("DRO")) {
        sscanf(cmd.c_str(), "DRO %d %d", &intensity, &duration);
        vibrate("DRO", intensity, duration);
    }
    else if (cmd.startsWith("UPP")) {
        sscanf(cmd.c_str(), "UPP %d %d", &intensity, &duration);
        vibrate("UPP", intensity, duration);
    }
    else if (cmd.startsWith("BOT")) {
        sscanf(cmd.c_str(), "BOT %d %d", &intensity, &duration);
        vibrate("BOT", intensity, duration);
    }
    else if (cmd == "STOP") {
        stopAll();
    }
    else {
        Serial.println("Invalid cmd :  " + cmd);
    }
}
