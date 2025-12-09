#include "logic.h"
#include "send.h"
#include <Arduino.h>

void parseAndApply(String msg) {
    Serial.println("[CMD] " + msg);

    int L = 0, C = 0, R = 0;

    // Extraction des valeurs
    int ok = sscanf(msg.c_str(), "L%dC%dR%d", &L, &C, &R);

    if (ok != 3) {
        Serial.println("[ERROR] Invalid format. Expected: Lxx Cxx Rxx");
        return;
    }

    // Saturation (valeurs 0–100 max)
    L = constrain(L, 0, 100);
    C = constrain(C, 0, 100);
    R = constrain(R, 0, 100);

    // Conversion 0–100 → 0–255
    int pwmL = map(L, 0, 100, 0, 255);
    int pwmC = map(C, 0, 100, 0, 255);
    int pwmR = map(R, 0, 100, 0, 255);

    // Application immédiate → remplace toute ancienne commande
    applyIntensity(pwmL, pwmC, pwmR);
}