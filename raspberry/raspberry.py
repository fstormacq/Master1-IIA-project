"""
Main module for Raspberry Pi specific functionality.

The raspberry pi will act as a central hub for various sensors and sensorial outputs.

It will consume data from connected sensors and process it accordingly.
"""

import threading, time, numpy as np

from queue import Empty
from queue_manager import queue_manager, DataType

def heavy_audio_processing(chunk):
    """Heavy processing for audio data"""

    rms = np.sqrt(np.mean(chunk**2))
    
    # Computing dB level
    ref = 1.0      # Reference for dBFS (normalized float audio)
    eps = 1e-12    # Avoid log10(0)
    level = max(rms / ref, eps)
    niveau_db = 20.0 * np.log10(level)
    
    if not np.isfinite(niveau_db):
        niveau_db = -np.inf
    
    # Sound level classification
    if niveau_db < -45:
        sound_label = "Chillax"
    elif niveau_db < -30:
        sound_label = "Some noise"
    elif niveau_db < -15:
        sound_label = "Be Careful"
    else:
        sound_label = "Danger"
    
    # Spectral analysis
    fft_result = np.fft.fft(chunk)
    dominant_freq = np.argmax(np.abs(fft_result[:len(fft_result)//2]))

    print(f"Audio Processing - RMS: {rms:.5f}, dB: {niveau_db:.2f}, Class: {sound_label}, Freq: {dominant_freq} Hz")
    
    return {
        'rms': rms,
        'db_level': niveau_db,
        'sound_classification': sound_label,
        'dominant_frequency': dominant_freq,
        'timestamp': time.time()
    }

def sensor_processing_thread():
    """Thread for sensor data processing"""
    while True:
        try:
            data_type, data = queue_manager.get_sensor_data(timeout=1.0)
            
            if data_type == DataType.MICRO_DATA:
                result = heavy_audio_processing(data)
                
                # Prepare command for Arduino, can be modified as needed
                arduino_command = {
                    'type': 'audio_alert',
                    'db_level': result['db_level'],
                    'classification': result['sound_classification'],
                    'rms': result['rms'],
                    'frequency': result['dominant_frequency']
                }
                queue_manager.put_arduino_data(arduino_command)
                
        except Empty:
            continue
        except Exception as e:
            print(f"Processing error: {e}")

def arduino_communication_thread():
    """Thread for Arduino communication"""
    while True:
        try:
            command = queue_manager.get_arduino_data(timeout=1.0)
            # print(f"Sending to Arduino: {command}")
            # Here: real serial communication
            
        except Empty:
            continue
        except Exception as e:
            print(f"Arduino communication error: {e}")

def start_processing():
    """Function to start all processing threads"""
    print("Starting processing threads...")
    
    processing_thread = threading.Thread(target=sensor_processing_thread, daemon=True)
    # arduino_thread = threading.Thread(target=arduino_communication_thread, daemon=True)
    
    processing_thread.start()
    # arduino_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Processing error: {e}")

# For individual tests
if __name__ == "__main__":
    start_processing()

    