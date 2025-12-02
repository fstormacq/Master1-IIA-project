#include "get.h"

#include "get.h"

bool TEST_MODE = true;

String getCommand() {
    static int step = 0;

    if (TEST_MODE) {
        switch(step) {
            case 0:
                step++;
                return "UPP 255 5000";   
            case 1:
                step++;
                return "DRO 180 7000";   
            case 2:
                step++;
                return "UPP 80 3000";    
            case 3:
                step++;
                return "DRO 255 10000";
            case 4:
                step++;
                return "UPP 150 5000";   
        }

        return "";
    }

    // Mode normal : communication série
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        return cmd;
    }

    return "";
}