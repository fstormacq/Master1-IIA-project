#include "logic.h"
#include "command_queue.h"
#include "send.h"

unsigned long vibrationEnd = 0;

void parseAndEnqueue(String msg) {
    Serial.println("[PARSE] msg = " + msg);

    String pos;
    int intensity = 0;
    int duration = 0;

    // Décomposer la string : POS intensité durée
    int ok = sscanf(msg.c_str(), "%3s %d %d", 
                    (char*)malloc(4), &intensity, &duration);

    if(ok != 3) {
        Serial.println("[ERROR] Invalid command format");
        return;
    }

    pos = msg.substring(0, 3);

    VibrationCommand cmd = {0, 0, 0, duration};

    if(pos == "UPP") {
        cmd.upp = intensity;
    }
    else if(pos == "GAU") {
        cmd.gau = intensity;
    }
    else if(pos == "DRO") {
        cmd.dro = intensity;
    }
    else {
        Serial.println("[ERROR] Unknown POS: " + pos);
        return;
    }

    if(!cmdQueue.enqueue(cmd)) {
        Serial.println("[QUEUE] FULL — command dropped");
    } else {
        Serial.println("[QUEUE] Added command ✓");
    }
}


void consumeQueue() {
    // Si une vibration est en cours → attendre
    if(millis() < vibrationEnd)
        return;

    if(millis() >= vibrationEnd && vibrationEnd != 0) {
        stopAll();
        vibrationEnd = 0;
    }
    
    if(cmdQueue.isEmpty()) 
        return;

    VibrationCommand cmd = cmdQueue.dequeue();

    Serial.print("[EXEC] UPP=");
    Serial.print(cmd.upp);
    Serial.print(" GAU=");
    Serial.print(cmd.gau);
    Serial.print(" DRO=");
    Serial.print(cmd.dro);
    Serial.print(" DUR=");
    Serial.println(cmd.duration);

    analogWrite(upperPin, cmd.upp);
    analogWrite(leftPin,  cmd.gau);
    analogWrite(rightPin, cmd.dro);

    vibrationEnd = millis() + cmd.duration;
}