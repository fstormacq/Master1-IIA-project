#pragma once
#include <Arduino.h>

struct VibrationCommand {
    int upp;
    int gau;
    int dro;
    int duration;
};

#define QUEUE_SIZE 5

class CommandQueue {
public:
    VibrationCommand buffer[QUEUE_SIZE];
    int head = 0;
    int tail = 0;

    bool isEmpty() {
        return head == tail;
    }

    bool isFull() {
        return (tail + 1) % QUEUE_SIZE == head;
    }

    bool enqueue(VibrationCommand cmd) {
        if (isFull()) return false;
        buffer[tail] = cmd;
        tail = (tail + 1) % QUEUE_SIZE;
        return true;
    }

    VibrationCommand dequeue() {
        VibrationCommand empty = {0,0,0,0};
        if (isEmpty()) return empty;

        VibrationCommand cmd = buffer[head];
        head = (head + 1) % QUEUE_SIZE;
        return cmd;
    }
};

extern CommandQueue cmdQueue;