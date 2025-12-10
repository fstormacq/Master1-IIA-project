#include "send.h"
#include <Arduino.h>
#include <FastLED.h>

#define LED_PIN     9
#define NUM_LEDS    12
#define BRIGHTNESS  64
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB
CRGB leds[NUM_LEDS];

int upperPin = 10;
int rightPin = 11;
int leftPin  = 12;   

void setupPins() {
    pinMode(upperPin, OUTPUT);
    pinMode(rightPin, OUTPUT);
    pinMode(leftPin,  OUTPUT);

    // Initialisation FastLED
    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(BRIGHTNESS);

    stopAll();
}

// Helper: Convertit l'intensité (0-100) en couleur (Vert -> Jaune -> Rouge)
CRGB getColorFromIntensity(int intensity) {
    // Si très faible intensité, on peut éteindre ou mettre du vert très faible
    if (intensity <= 5) return CRGB::Green; 
    
    // Mapping HSV : 
    // Hue 96 (Vert) -> Hue 0 (Rouge)
    // On mappe 0-100 vers 96-0
    int hue = map(intensity, 0, 100, 96, 0);
    return CHSV(hue, 255, 255);
}

void stopAll() {
    analogWrite(upperPin, 0);
    analogWrite(rightPin, 0);
    analogWrite(leftPin,  0);

    fill_solid(leds, NUM_LEDS, CRGB::Black);
    FastLED.show();
}

void applyIntensity(int leftVal, int centerVal, int rightVal) {
    // Vibration (PWM)
    analogWrite(leftPin,   leftVal);
    analogWrite(upperPin,  centerVal);
    analogWrite(rightPin,  rightVal);

    // Gestion des LEDs (suppose un bandeau de 12 LEDs divisé en 3 zones)
    int zoneSize = NUM_LEDS / 3;

    // Zone Gauche
    CRGB colorL = getColorFromIntensity(leftVal);
    for(int i=0; i<zoneSize; i++) leds[i] = colorL;

    // Zone Centre
    CRGB colorC = getColorFromIntensity(centerVal);
    for(int i=zoneSize; i<zoneSize*2; i++) leds[i] = colorC;

    // Zone Droite
    CRGB colorR = getColorFromIntensity(rightVal);
    for(int i=zoneSize*2; i<NUM_LEDS; i++) leds[i] = colorR;

    FastLED.show();
}