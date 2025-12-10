#include "send.h"
#include <Arduino.h>
#include <FastLED.h>

#define LED_PIN     9
#define NUM_LEDS    3
#define BRIGHTNESS  20
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB
CRGB leds[NUM_LEDS];

void setupPins() {
    // ✅ Initialisation FastLED
    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(BRIGHTNESS);

    // ✅ TEST DE VALIDATION MATÉRIEL : allume toutes les LEDs en ROUGE pendant 2 secondes
    fill_solid(leds, NUM_LEDS, CRGB::Red);
    FastLED.show();
    delay(2000);
    
    // ✅ Éteint les LEDs après le test
    stopAll();
    
    Serial.println("[LED] Test de démarrage terminé - LEDs opérationnelles");
}

// Helper: Convertit l'intensité (0-255) en couleur (Vert -> Jaune -> Rouge)
CRGB getColorFromIntensity(int intensity) {
    // Si très faible intensité, éteindre
    if (intensity <= 5) return CRGB::Black; 
    
    // Mapping HSV : 
    // Hue 96 (Vert) -> Hue 0 (Rouge)
    // On mappe 0-255 vers 96-0
    int hue = map(intensity, 0, 255, 96, 0);
    int brightness = map(intensity, 0, 255, 50, 255); // Luminosité variable
    return CHSV(hue, 255, brightness);
}

void stopAll() {
    fill_solid(leds, NUM_LEDS, CRGB::Black);
    FastLED.show();
}

void applyIntensity(int leftVal, int centerVal, int rightVal) {
    // 3 LEDs : une par zone
    // LED 0 = Gauche
    // LED 1 = Centre
    // LED 2 = Droite
    
    leds[0] = getColorFromIntensity(leftVal);   // Gauche
    leds[1] = getColorFromIntensity(centerVal); // Centre
    leds[2] = getColorFromIntensity(rightVal);  // Droite

    FastLED.show();
    
    // ✅ DEBUG : affiche les valeurs appliquées (utile pour diagnostiquer)
    Serial.print("[LED] L:");
    Serial.print(leftVal);
    Serial.print(" C:");
    Serial.print(centerVal);
    Serial.print(" R:");
    Serial.println(rightVal);
}