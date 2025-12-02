#include <Arduino.h>
#include "get.h"
#include "logic.h"
#include "send.h"
#include "command_queue.h"

void setup() {
    Serial.begin(115200);   
    setupPins();
}

void loop() {
    // Récupère une commande (FAKE si TEST_MODE = true)
    String cmd = getCommand();

    // Si la commande n'est pas vide, traite-la
    if (cmd.length() > 0) {
        parseAndEnqueue(cmd);
    }

    // Gère l'arrêt automatique après la durée
    consumeQueue();
}