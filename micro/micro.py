import numpy as np
import sounddevice as sd
import time
from queue_manager import queue_manager

DEVICE_NAME = "USB PnP Sound Device"
CHUNK_DURATION = 1.0 / 15 
SAMPLE_RATE = 44100
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

audio_buffer = []
audio_running = False

def audio_callback(indata, frames, time_info, status):
    """
    Callback function for audio input stream.

    Parameters
    ----------
    indata : np.ndarray
        The recorded audio data
    frames : int
        Number of frames
    time_info : dict
        Time information
    status : sd.CallbackFlags
        Status of the audio stream
    """
    global audio_buffer
    audio_buffer.extend(indata.flatten())

    while len(audio_buffer) >= CHUNK_SIZE:
        chunk = np.array(audio_buffer[:CHUNK_SIZE])
        audio_buffer = audio_buffer[CHUNK_SIZE:]
        queue_manager.put_micro_data(chunk)
        
        
def simulate_audio_chunk():
    """
    Simulate an audio chunk for testing purposes.

    Returns
    -------
    np.ndarray
        Simulated audio data chunk
    """
    return np.random.uniform(-1.0, 1.0, CHUNK_SIZE).astype(np.float32)



def start_audio_capture(debug=False, device_id=None, simulate=False):
    """
    Start capturing audio from the specified device.

    Parameters
    ----------
    debug : bool
        If True, enables debug mode with verbose logging.
    device_id : int or None
        The ID of the audio input device to use. If None, will search for the default device.
    simulate : bool
        If True, simulates audio data instead of capturing from a device.
    """
    global audio_running

    if audio_running:
        if debug:
            print("Audio capture already running, skipping second start.")
        return

    audio_running = True
    
    if simulate:
        if debug:
            print("[WARNING] Microphone not found, starting audio simulation...")
        try:
            while True:
                chunk = simulate_audio_chunk()
                queue_manager.put_micro_data(chunk)
                time.sleep(CHUNK_DURATION)
        except KeyboardInterrupt:
            print("Simulated audio stopped.")
        finally:
            audio_running = False
        return

    # If no device_id provided, search for the device
    if device_id is None:
        devices = sd.query_devices() 
        
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0 and DEVICE_NAME in dev['name']:
                device_id = i
                break

        if device_id is None:
            raise RuntimeError(f"{DEVICE_NAME} can't be found.")
        
        if debug:
            print(f"Found audio device: {devices[device_id]['name']} (ID: {device_id})")

    if debug:
        print(f"Starting audio capture on device {device_id}...")

    with sd.InputStream(device=device_id, channels=1, samplerate=SAMPLE_RATE, blocksize=2048, callback=audio_callback):
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
    start_audio_capture()