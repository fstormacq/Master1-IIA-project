# Adaptive Cane - Assistive Navigation System

**Embodied and Augmented Interfaces Project 2025-2026**

---

## Project Description

This project implements an intelligent assistive cane system for visually impaired individuals that combines vision and audio sensing to provide real-time haptic feedback about environmental obstacles. The system uses multimodal data fusion to deliver comprehensive spatial awareness through LED-based visual feedback. The initial prototype of the system were supposed to use vibration motors, but due to technical constraints, we opted for a simpler LED strip output.

## System Architecture

The system follows a **Producer-Consumer** architecture with three main components:

### 1. Sensing Layer (Producers)
- **Intel RealSense D435 Camera**: Provides depth sensing for obstacle detection in three zones (left, center, right)
- **USB Microphone**: Captures ambient audio to detect potential auditory hazards

### 2. Processing Layer (Raspberry Pi)
The Raspberry Pi acts as the central hub, running multiple processing threads:

- **Audio Processing Thread**: Analyzes audio chunks for volume levels and classifies sound intensity (dB levels)
- **Video Processing Thread**: Processes depth frames to detect obstacles and calculate distances
- **Synchronization Buffer**: Temporally aligns audio and video data (±50ms threshold)
- **Arduino Communication Thread**: Generates LCR (Left-Center-Right) messages combining multimodal data

### 3. Output Layer (Arduino + LED Strip)
- **Arduino Microcontroller**: Receives LCR intensity commands via serial (115200 baud)
- **WS2812B LED Strip**: Displays 3 LEDs with color-coded warnings:
  - **Green**: Safe (low intensity)
  - **Yellow**: Warning (medium intensity)  
  - **Red**: Danger (high intensity)

## Hardware Components

**Required Setup:**
- Raspberry Pi (tested on Pi 3)
- Intel RealSense D435 depth camera
- USB microphone (PnP Sound Device)
- Arduino (Uno/Nano compatible)
- WS2812B LED strip (3 LEDs minimum)
- USB cables for serial communication

## Software Features

### Multi-threaded Queue System
- Separate queues for audio, video, and Arduino commands
- Automatic queue overflow handling (drops oldest data)
- Real-time statistics monitoring

### Intelligent Data Fusion
- **Weighted average**: 80% vision + 20% audio influence
- Zone-based intensity calculation (left, center, right)
- Distance-to-intensity mapping (0-100 scale)
- Obstacle detection with configurable alert thresholds (1m alert, 2m attention)

### Simulation Mode
- Full simulation support for development on systems without hardware
- Fake serial port with optional real-time plotting
- Simulated depth and audio data generation

### Monitoring & Debugging
- Serial monitor for Arduino output (`monitor_serial.py`)
- Queue statistics reporting
- Synchronization quality tracking
- FPS and throughput monitoring

## Installation & Usage

### Prerequisites
```bash
# Python 3.13+ with UV package manager
# Install dependencies
uv sync
```

### Running the System

**Full system with monitoring:**
```bash
./start.sh
```

**Manual start with options:**
```bash
# Normal operation
uv run main.py

# Disable audio input
uv run main.py --no-audio

# Disable video input
uv run main.py --no-video

# Enable debug logging
uv run main.py --debug

# Simulation mode (no hardware required)
uv run main.py --simulate
```

### Arduino Setup
1. Upload code from `arduino/Canne/` using PlatformIO
2. Install FastLED library
3. Connect LED strip to pin 9
4. Ensure serial port is `/dev/ttyACM0` (or adjust in code)

## Target Use Case

**Urban navigation assistance for visually impaired individuals**

The system provides real-time spatial awareness through a compact, multimodal feedback mechanism. The LED-based visual output can be mounted on the cane handle, providing immediate directional guidance about obstacles in the user's path. As initialy planned, vibration motors would have offered tactile feedback, but the LED strip serves as a simpler alternative for prototype validation.

## Project Structure

```
├── main.py                      # Main entry point, thread orchestration
├── queue_manager.py             # Central queue management system
├── monitor_serial.py            # Arduino serial monitor utility
├── start.sh                     # Convenience script to start system with monitoring
├── camera/
│   ├── camera.py               # RealSense camera capture and processing
│   └── camera_initial.py       # Initial prototype (legacy)
├── micro/
│   └── micro.py                # Audio capture and processing
├── raspberry/
│   ├── raspberry.py            # Main processing logic and Arduino communication
│   ├── sync_buffer.py          # Temporal synchronization buffer
│   ├── intensity_calculator.py # Converts sensor data to LED intensities
│   ├── lcr_message_generator.py # Generates LCR protocol messages
│   ├── sensor_data.py          # Data structures for sensor information
│   └── fake_serial.py          # Serial port simulator with plotting
└── arduino/
    ├── src/
    │   ├── main.cpp            # Arduino main loop
    │   ├── get.cpp             # Serial command parsing
    │   ├── logic.cpp           # Command processing logic
    │   └── send.cpp            # LED control with FastLED
    └── include/                # Header files
```

## Communication Protocol

### LCR Message Format
```
L<intensity>C<intensity>R<intensity>\n
```
- Intensity values: 000-100 (mapped to 0-255 PWM internally)
- Example: `L045C080R020` means Left=45%, Center=80%, Right=20%
- Sent at max 25Hz to avoid overwhelming the Arduino

### Serial Configuration
- Baud rate: 115200
- Port: `/dev/ttyACM0` (adjustable)
- Protocol: Newline-terminated ASCII strings

## Development Notes

### Camera Configuration
- Resolution: 640x480
- FPS: 15 (optimal for Raspberry Pi processing)
- Zones: 3 equal-width vertical sections (left, center, right)
- Margins: 10% top/bottom, 10% left/right

### Queue Sizes
- Micro/Video queues: 10 items (input buffers)
- Arduino queue: 5 items (output buffer)
- Processed data queues: 5 items (intermediate)

### Performance Considerations
- Audio chunk duration: 1/15 second (66.7ms)
- Video frame rate: 15 FPS
- Arduino send interval: 40ms (25Hz max)
- Synchronization tolerance: 50ms

## Team Members

- Nathan Lambrechts
- Edwyn Eben
- Louca Mathieu
- Simon Dourte
- Florian Stormacq

## Documentation

Additional documentation available in:
- `raspberry/RASPBERRY-PI.md` - Raspberry Pi setup guide
- `raspberry/pi-realsense.md` - RealSense camera setup on Raspberry Pi
- `UV.md` - UV package manager usage guide
- `doc/` - Project report and figures

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.