"""
Main module for Raspberry Pi specific functionality.

The raspberry pi will act as a central hub for various sensors and sensorial outputs.

It will consume data from connected sensors and process it accordingly.
"""

import threading, time, numpy as np

from queue import Empty
from queue_manager import queue_manager

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

def heavy_video_processing(video_data):
    """Heavy processing pour les données vidéo RealSense"""
    # Les données arrivent déjà analysées depuis camera.py
    # On peut faire du traitement supplémentaire ici
    
    mode = video_data['mode']
    obstacles = video_data['obstacles']
    distances = video_data['distances_smooth']
    
    # Analyse de sécurité
    danger_level = 0
    if 'Centre' in obstacles:
        danger_level = 3  # Danger critique
    elif len(obstacles) > 1:
        danger_level = 2  # Danger élevé 
    elif len(obstacles) == 1:
        danger_level = 1  # Attention
    
    # Classification du risque
    risk_classification = "safe"
    if danger_level == 3:
        risk_classification = "critical"
    elif danger_level == 2:
        risk_classification = "high"
    elif danger_level == 1:
        risk_classification = "medium"
    
    return {
        'mode': mode,
        'obstacle_info': video_data['obstacle_info'],
        'avoid_direction': video_data['avoid_direction'],
        'danger_level': danger_level,
        'risk_classification': risk_classification,
        'distances': distances,
        'obstacles_count': len(obstacles),
        'frame_number': video_data['frame_number'],
        'timestamp': video_data['timestamp']
    }

def micro_processing_thread():
    """Thread dédié au traitement audio"""
    processing_count = 0
    
    while True:
        try:
            chunk = queue_manager.get_micro_data(timeout=1.0)
            processing_count += 1
            
            # Traitement audio lourd
            result = heavy_audio_processing(chunk)
            
            # Commande Arduino pour l'audio
            arduino_command = {
                'type': 'audio_alert',
                'db_level': result['db_level'],
                'classification': result['sound_classification'],
                'rms': result['rms'],
                'frequency': result['dominant_frequency']
            }
            queue_manager.put_arduino_data(arduino_command)
            
            # Debug
            if processing_count % 20 == 0:
                print(f"🎤 Audio #{processing_count}: {result['db_level']:.1f}dB - {result['sound_classification']}")
                
        except Empty:
            continue
        except Exception as e:
            print(f"Micro processing error: {e}")

def video_processing_thread():
    """Thread dédié au traitement vidéo"""
    processing_count = 0
    
    while True:
        try:
            video_data = queue_manager.get_video_data(timeout=1.0)
            processing_count += 1
            
            # Traitement vidéo lourd
            result = heavy_video_processing(video_data)
            
            # Commande Arduino pour la vidéo
            arduino_command = {
                'type': 'vision_alert',
                'mode': result['mode'],
                'danger_level': result['danger_level'],
                'risk_classification': result['risk_classification'],
                'obstacle_info': result['obstacle_info'],
                'avoid_direction': result['avoid_direction'],
                'distances': result['distances']
            }
            queue_manager.put_arduino_data(arduino_command)
            
            # Debug
            if processing_count % 10 == 0:
                distances = result['distances']
                print(f"📹 Video #{processing_count}: {result['mode']} | Obstacles: {result['obstacle_info']} | "
                      f"G={distances['gauche']:.2f}m C={distances['centre']:.2f}m D={distances['droite']:.2f}m")
                
        except Empty:
            continue
        except Exception as e:
            print(f"Video processing error: {e}")

def sensor_processing_thread():
    """Thread for sensor data processing - DEPRECATED"""
    # Cette fonction est maintenant remplacée par micro_processing_thread et video_processing_thread
    pass

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
    """Fonction pour démarrer tous les threads de traitement"""
    print("Starting processing threads...")
    
    # Thread pour traitement audio
    micro_thread = threading.Thread(target=micro_processing_thread, daemon=True)
    
    # Thread pour traitement vidéo
    video_thread = threading.Thread(target=video_processing_thread, daemon=True)
    
    # Thread pour communication Arduino
    arduino_thread = threading.Thread(target=arduino_communication_thread, daemon=True)
    
    micro_thread.start()
    print("✅ Micro processing thread started")
    
    video_thread.start()
    print("✅ Video processing thread started")
    
    arduino_thread.start()
    print("✅ Arduino communication thread started")
    
    # Garder ce thread actif et afficher les stats
    try:
        while True:
            time.sleep(5)
            queue_manager.print_stats()
    except Exception as e:
        print(f"Processing error: {e}")

# For individual tests
if __name__ == "__main__":
    start_processing()