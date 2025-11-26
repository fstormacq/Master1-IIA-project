import numpy as np
import sounddevice as sd
import time
from queue_manager import queue_manager, DataType

DEVICE_NAME = "USB PnP Sound Device"
CHUNK_DURATION = 0.1
SAMPLE_RATE = 44100
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

audio_buffer = []
audio_running = False


def audio_callback(indata, frames, time_info, status):
    global audio_buffer
    audio_buffer.extend(indata.flatten())

    while len(audio_buffer) >= CHUNK_SIZE:
        chunk = np.array(audio_buffer[:CHUNK_SIZE])
        audio_buffer = audio_buffer[CHUNK_SIZE:]
        queue_manager.put_sensor_data(DataType.MICRO_DATA, chunk)


def start_audio_capture(device_id=None):
    global audio_running

    if audio_running:
        print("Audio capture already running, skipping second start.")
        return

    audio_running = True

    print(f"Starting audio capture on device {device_id}...")

    with sd.InputStream(device=device_id,
                        channels=1,
                        samplerate=SAMPLE_RATE,
                        blocksize=2048,
                        callback=audio_callback):

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Audio stopped.")
        except Exception as e:
            print(f"Audio capture error: {e}")
        finally:
            audio_running = False


if __name__ == "__main__":
    devices = sd.query_devices() 
    device_id = None
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and DEVICE_NAME in dev['name']:
            device_id = i
            break

    if device_id is None:
        raise RuntimeError(f"{DEVICE_NAME} can't be found.")
    
    sd.default.device = (device_id, None)

    start_audio_capture(device_id)