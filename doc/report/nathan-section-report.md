# Arduino Implementation
The arduino is used as a hardware interface between the Raspberry Pi and the output devices. Its role is limited to receiving commands sent by the Raspberry Pi in real time and applying them to the vibration motors.

The arduino communicates with the Raspberry Pi via a serial connection configured at 115200 baud. Commands are transmitted using a simple and robust format : LxxxCyyyRzzz where each value represents the intensity of the danger expressed between 0 and 100. The letters stand for left, center and right directions.

Upon reception, each command is directly delivered to the Arduino side. The received values in the range of 0 - 100 are converted to an 8 bit scale (0 - 255) required for the good interpretation of the arduino. In this part, there is no buffer or queue, each new command immediately replaces the previous output state. This choice ensures that the feedback always reflects the most recent perception of the environment.

Originally, the system was designed to welcome three vibration motors, one for each spatial direction. Due to a hardware and voltage constraints, these motors were first replaced by simple LEDs. However, the brightness of the single color of the leds was not fully reliable because the intensity values were difficult to distinguish visually making it hard to verify whether the Arduino was interpreting well the intensity of the danger. To overcome this limitation, rgb LEDs are used as a visual proxy to the haptic feedback. Each led corresponds to one direction and its color and brightness simulate the vibration intensity. The color can smoothly transition from green (safe) through yellow and orange (increasing risk) into red (critical danger) providing a clearer and more intuitive representation of the intensity level.

The arduino code is structured into multiple C++ files :  
- A main file is used to handle initialization and the main execution of the loop.
- A get file that manages the serial input.
- The logic file is here to parse and convert the intensity values. The rgb architecture is also present.
- The send file is used to abstract the hardware control of the output devices.

In addition, three 3 corresponding files (get.h, logic.h and send.h) are used so that the functions of these files can be used across the different files of the project.

Last but no least, several hardware considerations had to be considered. Indeed, directly powering vibration motors from the arduino was unsafe due to limitations and voltage mismatches which shall damage the arduino board. Using LEDs as a placeholder allowed functional testing of the communication from the Raspberry Pi to the outputs and control logic while avoiding electrical risks and hardware damages. Integrating proper motor drivers remains future work as well as environment tests.