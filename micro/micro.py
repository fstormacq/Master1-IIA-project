import numpy as np
import sounddevice as sd
from queue import Queue, Empty

q = Queue(maxsize=20)

# Audio callback: Ultra-fast processing
def audio_callback(indata, frames, time_info, status):
    """Callback ultra-rapide : juste calculer RMS et envoyer"""
    if status:
        # Log les overflows mais ne pas print ici
        pass
    
    try:
        rms = np.sqrt(np.dot(indata.T, indata)[0, 0] / len(indata)) # Optimized RMS calculation
        rms_val = float(rms) if np.isfinite(rms) else 0.0 # Handle non-finite RMS
    except Exception:
        rms_val = 0.0
    
    try:
        q.put_nowait(rms_val) # Avoid blocking if queue is full
    except:
        pass

# Main thread: Slower processing and display
with sd.InputStream(channels=1, samplerate=44100, blocksize=2048, callback=audio_callback):
    ref = 1.0      # Reference for dBFS (normalized float audio)
    eps = 1e-12    # Avoid log10(0)
    
    while True:
        try:
            rms_val = q.get(timeout=1.0)
        except Empty:
            continue
        
        # Safe dB calculation
        level = max(rms_val / ref, eps)
        niveau_db = 20.0 * np.log10(level)
        
        if not np.isfinite(niveau_db):
            niveau_db = -np.inf
        
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
        
        # Display logic (can take time here)
        print(f"\r{niveau_db:6.1f} dB {bar:<30} {label:<15}", end="")