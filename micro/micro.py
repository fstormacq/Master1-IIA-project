import numpy as np
import sounddevice as sd
import time
from queue_manager import queue_manager, DataType

CHUNK_DURATION = 0.1
SAMPLE_RATE = 44100
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

audio_buffer = []

def audio_callback(indata, frames, time_info, status):
    global audio_buffer
    
    audio_buffer.extend(indata.flatten())
    
    while len(audio_buffer) >= CHUNK_SIZE:
        chunk = np.array(audio_buffer[:CHUNK_SIZE])
        audio_buffer = audio_buffer[CHUNK_SIZE:]
        
        queue_manager.put_sensor_data(DataType.MICRO_DATA, chunk)

def start_audio_capture():
    """Function to start audio capture"""
    
    print("Starting audio capture...")
    
    with sd.InputStream(channels=1, samplerate=SAMPLE_RATE, 
                       blocksize=2048, callback=audio_callback):
        try:
            while True:
                time.sleep(0.1)  # Keep main thread alive
        except Exception as e:
            print(f"Audio capture error: {e}")

# For individual tests
if __name__ == "__main__":
    start_audio_capture()