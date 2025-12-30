Title : Adaptative Cane

Nathan Lambrechts
Simon Dourte
Florian Stormacq
Edwyn Eben
Louca Mathieu

# Abstract

People with visual impairments represent a significant proportion of the global population. It is estimated that at least 2.2 billion people have some form of vision impairment. It is therefore essential to develop solutions that meet their needs and improve their independence. With this in mind, this project presents an adaptive connected cane for blind or visually impaired people designed to improve their perception of their surroundings and increase their safety in the face of potential obstacles and dangers. The cane is based on two main sensors: an Intel RealSense D435 depth camera and a USB microphone. The data from these sensors is processed in real time by a Raspberry Pi 3. The microphone assesses the noise level of the environment, while the camera detects the position and distance of obstacles and the recommended area to avoid them. This information is used to determine one of the device's three alert modes. User feedback is provided by three vibrating motors, each associated with a direction. The intensity and duration of the vibrations indicate the proximity of the danger and guide the user as they move. This prototype is therefore an assistance solution aimed at improving the mobility and safety of blind or visually impaired people in their daily lives.

# Introduction

The goal of the project is to develop an adaptive smart cane designed to improve spatial awareness and safety for visually impaired people. The system relies on two main sensors : a depth camera and a microphone to detect obstacles or danger in real lifetime. The data is collected by a Raspberry Pi which analyzes visual and audio information from the environment.

The system focuses entirely on haptic feedback. A set of 3 vibration motors is placed on the cane to provide tactile information to the user. Each motor has an direction which means one direction is missing. Indeed, we have left out the back direction because the camera will be settled as glasses so they can't see behind the user. The vibration intensity and duration reflect the proximity of the danger allowing the user to interpret the environment with the haptic output.

This cane aims to support blind people during a random urban walk or any action that has potential danger to the user.

# State of Art

Recent work has explored the use of haptic feedback to support navigation for visually impaired people. The system presented in article1 (see references) shows that vibration cues can effectly convey spatial information and help users perceive obstacles without relying on vision. However, this approach focuses mainly on haptic modality and does not integrate additional modalities. This limitation highlights the need for devices that combine multiples sources of information to provide a more reliable feedback during navigation. 

# Project architecture (Methodology)

The project is structured into several key components to ensure optimal functionality, performance, and maintainability:

## Sensors

1. **Audio Sensor** (= microphone): To capture ambient sound, we use a USB microphone (“USB PnP Sound Device”). The goal is to continuously record the surrounding audio signal in order to determine the noise level around the user. This allows us to know whether the environment is noisy (e.g., a crowd) or quiet.

2. **Video Sensor** (= intel realsense camera): To capture the image and depth of field, we use a Realsense Depth D435i camera connected to the Raspberry Pi with a USB-C cable. The aim is to continuously record the video stream perceived by the camera, knowing where the danger is and how far away it is, in order to determine which alert mode the cane will be in and where to dodge it.

## Data Capture and Processing

To capture and process data from the sensors in real-time, a Raspberry Pi 3 is used. 

Note: This device is not the initial Raspberry Pi 1 that were fournished at the begining of the project, as it was not powerful enough to handle the processing requirements.

The raspberry pi runs a Python script, which is responsible for capturing and processing the data from the sensors. This process outputs a simple result: specified intensity levels for each vibration motor, as well as the noise level detected.

The output would be added in a queue, which would be read by an Arduino board to actuate the motors accordingly.

The exact implementation details of the Python script will be discussed in the next section.

## Arduino Board

In this project, Arduino will be used as an interface between the central processing (raspberry) and the physical actioners (vibration motors). It receives already - processed instructions that specify how the motors should behave.

First, the raspberry send data divided in 3 with where the danger comes from, the intensity and the duration of the vibration. The arduino receives the information, interprets it and converts it into appropriate signals for the vibration motors.

In the overall architecture, the arduino is responsible for executing the physical output (vibration motors) in real time. It doesn't treat data, it applies the received instructions for the vibration motors.


# Project implementation (Methodology)

A python script is implemented to run on the raspberry pi 3, which captures and processes the data from the sensors in real-time.

Note: As the sensors "produce" data continuously, the script implements a multi-threaded Producer-Consumer architecture to handle the data efficiently.

A main.py file is the entry point of the codebase, which initializes and starts the different components (as the sensors) of the system. 

## Sensors

1. **Audio Sensor** (= microphone): A Python script in the micro folder is used to capture the data recorded by the microphone. Audio capture relies on the sounddevice library, which creates an audio stream that captures samples in real time. The signal is retrieved as chunks, then sent into a queue to be processed.
To achieve this, the script first searches for the desired audio device. Then, it defines various parameters (chunk size, chunk duration, etc). After that, audio capture is performed through an audio stream (InputStream) associated with a callback function. Each time new data is received, the samples are added to an internal buffer. As soon as this buffer contains enough samples to form a complete chunk, the chunk is extracted and converted into a NumPy array before being sent into a queue for processing.

2. **Video Sensor** (= intel realsense camera): Video capture is based on the pyrealsense2 library, which is Intel Realsense's official library, as well as other imports such as numpy, cv2 and deque for image processing and data history management.

After initialising the camera and its settings, the script launches a pipeline in depth mode, retrieves the depth to convert the raw values into metres and prepares a history for each direction.
It then divides the image into three areas and calculates the median for each area, then saves them in the corresponding history.

The script then defines the danger level, but only takes into account the area in front (below one metre: alert, between 1 and 2 metres: caution, beyond: peaceful area).
In addition, the script detects where obstacles are located and indicates the recommended area to avoid danger.
Finally, the script displays the information.

All these operations are performed continuously in an infinite loop, which allows the stream to be processed in real time and the histories to be constantly updated in order to avoid sudden variations and obtain a more stable distance for each area.

Both sensor data are captured in separate threads, which act as separate "Producers" in the architecture. However, in the current ideal version of the code, the two producers would share the same queue and will add data into a shared tuple [(microphone data, camera data),...]. This ideal version is not yet implemented, but this would ensure that the data from both sensors are synchronized.

## Raspberry Pi Script

The raspberry Pi script ensures the following functionalities:

1. The audio processing: Consumes the audio data from the microphone producer thread and computes the necessary audio features (e.g., rms, noise level, etc.).
2. The video processing: Consumes the video data from the camera producer thread, computes the necessary features (not yet implemented in the current version).
3. Add the computed features into a queue, which will be read by the Arduino board to actuate the motors accordingly.

The current version of the code only implements the audio processing part, while the video processing, the synchronization and the data communication with the Arduino board are yet to be implemented.

### Limitations of the Raspberry Pi

Several problems were encountered when using the Raspberries.

1. **Performance Issue**: The initial Raspberry Pi 1 was not powerful enough to handle the processing requirements of the audio and video data in real-time. Time were lost trying to optimize the code to run on this device. Eventually, it was decided to switch to a more powerful Raspberry Pi 3,
2. **Configuration Issue**: Setting up the Raspberry Pi with the necessary libraries, configurations and dependecnies for the sensors (particularly the Intel Realsense camera) proved to be more challenging than anticipated. Significant time was spent to configure the device properly. However, for reproducibility purposes, all the steps followed to set up the Raspberry Pi 3 are documented in a separate installation guide.
   A particular note can be made about the installation of the Intel Realsense python library, which required to clone the library from GitHub and build it from source, as the pre-compiled binaries were not compatible with the Raspberry Pi architecture. This process involved lots of ressources and time.
3. Is assume that the synchronization of the data from both sensors will be challenging.

## Arduino Board

The Arduino implementation is structured in two main parts. The first part is the initialization phase where the necessary functions are prepared so they can be reused across different folders of the project. The second part consists of the main program logic where the code is executed.

The main loop continuously receives data from the Raspberry Pi and applies the instructions to the output pins. These instructions determine which vibration motor should be activated, at what intensity and for how long.

For now, the vibration motors have temporarily been replaced with LEDs for testing purposes due to a voltage issue between the arduino and the vibration motors. This allows the output logic to verified and fixes the potential problems.

On the raspberry part, my neighbour has switched to a producer - consumer architecture to handle receiving data from the camera and the micro. The next step for the arduino will be to stay in agreement with the raspberry so it is essential to have a producer - consumer in the arduino part too.

# Contribution

...

# What's next

On the raspberry part, we have to finish the receipt of danger from the two modalities and finish the producer - consumer architecture. Same for arduino where the PC architecture has to be implemented.

To follow an happy end of the project, we will need to translate our report into the final structure of the report. We have to add the evaluation and conclusion part. These parts require the project to be over and so it will be done right after the project's end.

# References

Article1 : https://dl.acm.org/doi/abs/10.1145/3711931