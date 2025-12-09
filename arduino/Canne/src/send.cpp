#include "send.h"
#include <Arduino.h>
#include <FastLED.h>

#define NUM_LEDS 3
#define DATA_PIN 10

CRGB leds[NUM_LEDS];

void setupPins() {
    // Initialisation du ruban de LED
    // Utilisation de WS2812B, ordre des couleurs GRB (très courant)
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(200); // Luminosité globale fixée à 200

    stopAll();
}

void stopAll() {
    fill_solid(leds, NUM_LEDS, CRGB::Black);
    FastLED.show();
}

void applyIntensity(int leftVal, int centerVal, int rightVal) {
    // leftVal, centerVal, rightVal sont entre 0 et 255
    // 0 -> Vert (HUE_GREEN = 96)
    // 255 -> Rouge (HUE_RED = 0)
    
    leds[0] = CHSV(map(leftVal, 0, 255, HUE_GREEN, HUE_RED), 255, 255);
    leds[1] = CHSV(map(centerVal, 0, 255, HUE_GREEN, HUE_RED), 255, 255);
    leds[2] = CHSV(map(rightVal, 0, 255, HUE_GREEN, HUE_RED), 255, 255);

    FastLED.show();
}