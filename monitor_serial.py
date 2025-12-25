import serial
import sys

# Monitor serial output from Arduino
# Author: Claude Sonnet 4.5, reviewed by Florian Stormacq

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    print("📡 Monitoring Arduino on /dev/ttyACM0 at 115200 baud...")
    print("Press Ctrl+C to exit\n")
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(line)
except KeyboardInterrupt:
    print("\n👋 Monitoring stopped")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
