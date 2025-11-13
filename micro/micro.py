"""
Microphone sound level monitoring script

Author: Louca Mathieu
        Florian Stormacq

Optimizations:
    1. RMS calculation optimized using matrix multiplication via np.dot instead of element-wise operations.
    2. Reduced blocksize to 2048 samples to decrease latency and improve responsiveness. (Possible to adjust based on needs, e.g. higher for less CPU usage; 4096, 8192, etc.)
    3. Precised data type for audio input to 'float32' to ensure consistency and potentially improve performance.
    4. Adjust the audia frequency to 16kHz


Other optimizations:
    - Remove print statements in the audio callback to avoid blocking the audio stream.
    - Implement a Producer-Consumer pattern
    - Secure the DB calculation against NaN, inf, negative log inputs

I think we should also test the latency of the processing in the callback to be sure that we are not exceeding the block duration. That would avoid to be warned for a past problem.
"""

import sounddevice as sd
import numpy as np
import time

frequence = 44_100 # The only frequencies supported by the micro are 44100 and 48000 Hz
bloc_duree = 0.3      
device_name = "USB PnP Sound Device"  #This is the micro that we have to test but we can change it

devices = sd.query_devices() 
device_id = None
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0 and device_name in dev['name']:
        device_id = i
        break

if device_id is None:
    raise RuntimeError(f"{device_name} can' be find.")

print("We use: ", sd.query_devices(device_id)['name'])
print("Now, we have to press Ctrl+C to stop the program.")

def audio_callback(indata, frames, time_info, status): #main function
    if status:
        print(status)
    
    # rms = np.sqrt(np.mean(indata**2)) #calculate RMS --- IGNORE ---
    rms = np.sqrt(np.dot(indata.T, indata)[0, 0] / len(indata)) # Optimise RMS calculation with matrix multiplication via np.dot
    niveau_db = 20 * np.log10(rms + 1e-10)  
    
    if niveau_db < -45:
        label = "Chillax"
    elif niveau_db < -30:
        label = "Some noise"
    elif niveau_db < -15:
        label = "Be Careful"
    else:
        label = "Danger"
    
    bar_length = int(np.clip((niveau_db + 60) / 2, 0, 30))
    bar = "█" * bar_length
    
    print(f"\r{niveau_db:6.1f} dB {bar:<30} {label:<15}", end="")

with sd.InputStream(device=device_id,
                    channels=1,
                    samplerate=frequence,
                    blocksize=2048,
                    dtype='float32',
                    callback=audio_callback):
    try:
        while True:
            time.sleep(bloc_duree)
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")
