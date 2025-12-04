"""
Main module for Raspberry Pi specific functionality.

The raspberry pi will act as a central hub for various sensors and sensorial outputs.

It will consume data from connected sensors and process it accordingly.
"""

import threading, time, numpy as np

from queue import Empty
from queue_manager import queue_manager
from dataclasses import dataclass
from typing import Optional, Dict, Any
from collections import deque

@dataclass
class SensorData:
    """
    Data structure for sensor data with timestamp
    """
    timestamp: float
    data: Dict[Any, Any]
    source: str  #'audio' ou 'video'

class IntensityCalculator:
    """
    Calculator for intensities based on audio dB levels and video distances/obstacles
    """
    
    @staticmethod
    def audio_to_intensity(db_level: float) -> int:
        """
        Convert dB level to intensity (0-100)
        
        Parameters
        ----------
        db_level : float
            The dB level to convert
        
        Returns
        -------
        int
            The corresponding intensity (0-100)
        """
        if db_level < -45:
            return max(0, int((db_level + 60) * 20 / 15))  #-60 à -45 → 0 à 20
        elif db_level < -30:
            return int(20 + (db_level + 45) * 30 / 15)      #-45 à -30 → 20 à 50
        elif db_level < -15:
            return int(50 + (db_level + 30) * 30 / 15)      #-30 à -15 → 50 à 80
        else:
            return min(100, int(80 + (db_level + 15) * 20 / 10))  #-15+ → 80-100
    
    @staticmethod
    def vision_to_intensity_by_zone(distances: Dict[str, float], obstacles: list) -> Dict[str, int]:
        """Convertit distances et obstacles en intensités par zone"""
        zones = {'gauche': 0, 'centre': 0, 'droite': 0}
        
        for zone in zones.keys():
            distance = distances.get(zone, 5.0)  # 5m par défaut
            
            # Intensité basée sur la distance
            if distance > 2.0:
                base_intensity = max(0, int((3.0 - distance) * 15))  # 0-15 pour >2m
            elif distance > 1.0:
                base_intensity = int(15 + (2.0 - distance) * 55)     # 15-70 pour 1-2m
            else:
                base_intensity = int(70 + (1.0 - distance) * 30)     # 70-100 pour <1m
            
            # Bonus si obstacle détecté
            zone_mapping = {'gauche': 'Gauche', 'centre': 'Centre', 'droite': 'Droite'}
            if zone_mapping[zone] in obstacles:
                base_intensity += 20
                
            zones[zone] = max(0, min(100, base_intensity))
            
        return zones

class LCRMessageGenerator:
    """Générateur de messages L...C...R... pour Arduino"""
    
    def __init__(self):
        self.last_message = "L000C000R000"
        self.message_count = 0
        
    def generate_synchronized_message(self, audio_data=None, video_data=None) -> str:
        """Génère un message LCR basé sur données synchronisées"""
        
        # Intensités par défaut
        left_intensity = 0
        center_intensity = 0
        right_intensity = 0
        
        # Traitement audio (influence globale)
        audio_intensity = 0
        if audio_data:
            audio_intensity = IntensityCalculator.audio_to_intensity(
                audio_data['db_level']
            )
        
        # Traitement vision (influence par zone)
        vision_intensities = {'gauche': 0, 'centre': 0, 'droite': 0}
        if video_data:
            vision_intensities = IntensityCalculator.vision_to_intensity_by_zone(
                video_data['distances'],
                video_data.get('obstacles', [])
            )
        
        # Fusion des intensités - Stratégie : Maximum + Audio global
        left_intensity = max(
            vision_intensities['gauche'],
            int(audio_intensity * 0.7)  # Audio influence réduite sur côtés
        )
        
        center_intensity = max(
            vision_intensities['centre'],
            audio_intensity  # Audio pleine influence au centre
        )
        
        right_intensity = max(
            vision_intensities['droite'],
            int(audio_intensity * 0.7)
        )
        
        # Formatage du message
        message = f"L{left_intensity:03d}C{center_intensity:03d}R{right_intensity:03d}"
        
        self.last_message = message
        self.message_count += 1
        
        return message
    
    def generate_fallback_message(self, audio_only=None, video_only=None) -> str:
        """Génère un message de fallback"""
        if audio_only:
            intensity = IntensityCalculator.audio_to_intensity(audio_only['db_level'])
            return f"L{intensity:03d}C{intensity:03d}R{intensity:03d}"
            
        if video_only:
            intensities = IntensityCalculator.vision_to_intensity_by_zone(
                video_only['distances'],
                video_only.get('obstacles', [])
            )
            return f"L{intensities['gauche']:03d}C{intensities['centre']:03d}R{intensities['droite']:03d}"
            
        return "L000C000R000"  # Repos

class SyncBuffer:
    """Buffer de synchronisation temporelle"""
    
    def __init__(self, max_age_ms=150):
        self.audio_buffer = deque(maxlen=5)
        self.video_buffer = deque(maxlen=5)
        self.max_age = max_age_ms / 1000.0
        
    def add_audio(self, audio_result):
        """Ajoute données audio avec timestamp"""
        sensor_data = SensorData(
            timestamp=time.time(),
            data=audio_result,
            source='audio'
        )
        self.audio_buffer.append(sensor_data)
        
    def add_video(self, video_result):
        """Ajoute données vidéo avec timestamp"""
        sensor_data = SensorData(
            timestamp=time.time(),
            data=video_result,
            source='video'
        )
        self.video_buffer.append(sensor_data)
        
    def cleanup_old_data(self, current_time):
        """Nettoie les données trop anciennes"""
        while self.audio_buffer and (current_time - self.audio_buffer[0].timestamp) > self.max_age:
            self.audio_buffer.popleft()
            
        while self.video_buffer and (current_time - self.video_buffer[0].timestamp) > self.max_age:
            self.video_buffer.popleft()
        
    def get_synchronized_pair(self):
        """Trouve la paire audio/vidéo la plus proche temporellement"""
        current_time = time.time()
        self.cleanup_old_data(current_time)
        
        if not self.audio_buffer or not self.video_buffer:
            return None
            
        best_pair = None
        min_time_diff = float('inf')
        
        for audio_data in self.audio_buffer:
            for video_data in self.video_buffer:
                time_diff = abs(audio_data.timestamp - video_data.timestamp)
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    best_pair = (audio_data, video_data)
                    
        # Seuil de synchronisation acceptable (50ms)
        if best_pair and min_time_diff < 0.05:
            return best_pair
            
        return None
    
    def get_latest_audio(self):
        """Récupère la donnée audio la plus récente"""
        return self.audio_buffer[-1] if self.audio_buffer else None
    
    def get_latest_video(self):
        """Récupère la donnée vidéo la plus récente"""
        return self.video_buffer[-1] if self.video_buffer else None

def heavy_audio_processing(chunk, debug=False):
    '''
    Heavy processing for microphone audio data.

    Parameters
    ----------
    chunk : np.ndarray
        The audio data chunk to be processed
    debug : bool
        If True, enables debug mode with verbose logging.

    Returns
    -------
    dict
        The processing results including RMS, dB level, classification, dominant frequency, and timestamp
    '''

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
    
    # Main frequency detection
    fft_result = np.fft.fft(chunk)
    dominant_freq = np.argmax(np.abs(fft_result[:len(fft_result)//2]))
    if debug:
        print(f"Audio Processing - RMS: {rms:.5f}, dB: {niveau_db:.2f}, Class: {sound_label}, Freq: {dominant_freq} Hz")
    
    return {
        'rms': rms,
        'db_level': niveau_db,
        'sound_classification': sound_label,
        'dominant_frequency': dominant_freq,
        'timestamp': time.time()
    }

def heavy_video_processing(video_data, debug=False):
    """
    Heavy processing for video data.

    Parameters
    ----------
    video_data : dict
        The video data to be processed
    debug : bool
        If True, enables debug mode with verbose logging.

    Returns
    -------
    dict
        The processing results including mode, obstacle info, avoid direction, danger level, risk classification,
        distances, obstacles count, frame number, and timestamp

    Notes
    -----
    The video data needs to arrive pre-processed with obstacle detection and distance estimation.
    """
    
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
    
    # Need to minimize the data sent to Arduino
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

def micro_processing_thread(debug=False):
    """
    Processing thread dedicated to microphone audio data

    Parameters
    ----------
    debug : bool
        If True, enables debug mode with verbose logging.

    Notes
    -----
    This thread continuously fetches audio data from the queue, processes it, and sends commands to the Arduino based on the results.
    """
    processing_count = 0
    
    while True:
        try:
            chunk = queue_manager.get_micro_data()
            processing_count += 1
            
            # Traitement audio lourd
            result = heavy_audio_processing(chunk, debug)
            
            """
            # Commande Arduino pour l'audio
            arduino_command = {
                'type': 'audio_alert',
                'db_level': result['db_level'],
                'classification': result['sound_classification'],
                'rms': result['rms'],
                'frequency': result['dominant_frequency']
            }
            queue_manager.put_arduino_data(arduino_command)"""
            
            # NOUVEAU: Envoyer vers la queue de données traitées
            queue_manager.put_audio_processed_data(result)
            
            # Debug
            if debug:
                print(f"Audio #{processing_count}: {result['db_level']:.1f}dB - {result['sound_classification']}")
                
        except Empty:
            continue
        except Exception as e:
            print(f"Micro processing error: {e}")

def video_processing_thread(debug=False):
    """
    Processing thread dedicated to video data

    Parameters
    ----------
    debug : bool
        If True, enables debug mode with verbose logging.

    Notes
    -----
    This thread continuously fetches video data from the queue, processes it, and sends commands to the Arduino based on the results.
    """
    processing_count = 0
    
    while True:
        try:
            video_data = queue_manager.get_video_data(timeout=1.0)
            processing_count += 1
            
            result = heavy_video_processing(video_data, debug)

            """arduino_command = {
                'type': 'vision_alert',
                'mode': result['mode'],
                'danger_level': result['danger_level'],
                'risk_classification': result['risk_classification'],
                'obstacle_info': result['obstacle_info'],
                'avoid_direction': result['avoid_direction'],
                'distances': result['distances']
            }
            
            queue_manager.put_arduino_data(arduino_command)"""
            
            # NOUVEAU: Envoyer vers la queue de données traitées
            queue_manager.put_video_processed_data(result)
            
            if debug:
                distances = result['distances']
                print(f"📹 Video #{processing_count}: {result['mode']} | Obstacles: {result['obstacle_info']} | "
                        f"G={distances['gauche']:.2f}m C={distances['centre']:.2f}m D={distances['droite']:.2f}m")
                
        except Empty:
            continue
        except Exception as e:
            print(f"Video processing error: {e}")

"""def arduino_communication_thread(debug=False):
    
    Processing thread dedicated to Arduino communication

    Parameters
    ----------
    debug : bool
        If True, enables debug mode with verbose logging.

    Notes
    -----
    This thread continuously fetches commands from the queue and sends them to the Arduino.
    
    while True:
        try:
            command = queue_manager.get_arduino_data(timeout=1.0)
            # print(f"Sending to Arduino: {command}")
            # Here: real serial communication
            
        except Empty:
            continue
        except Exception as e:
            print(f"Arduino communication error: {e}")"""
            
def arduino_communication_thread(debug=False):
    """
    Thread centralisé pour synchronisation et communication Arduino
    
    Ce thread :
    1. Collecte les données audio/vidéo traitées
    2. Les synchronise temporellement  
    3. Génère les messages LCR
    4. Envoie vers Arduino
    """
    sync_buffer = SyncBuffer(max_age_ms=150)
    message_generator = LCRMessageGenerator()
    last_send_time = 0
    send_interval = 1.0 / 25.0  # 25 Hz max
    
    print("🤖 Arduino communication thread started with synchronization")
    
    while True:
        try:
            current_time = time.time()
            
            # Collecter nouvelles données audio
            try:
                audio_result = queue_manager.get_audio_processed_data(timeout=0.01)
                sync_buffer.add_audio(audio_result)
            except Empty:
                pass
            
            # Collecter nouvelles données vidéo  
            try:
                video_result = queue_manager.get_video_processed_data(timeout=0.01)
                sync_buffer.add_video(video_result)
            except Empty:
                pass
            
            # Limiter la fréquence d'envoi Arduino (25Hz max)
            if (current_time - last_send_time) < send_interval:
                time.sleep(0.001)  # Petite pause
                continue
                
            # Tentative de synchronisation
            sync_pair = sync_buffer.get_synchronized_pair()
            
            if sync_pair:
                # Données synchronisées disponibles
                audio_data, video_data = sync_pair
                message = message_generator.generate_synchronized_message(
                    audio_data.data, video_data.data
                )
                
                sync_quality = 'synced'
                if debug:
                    time_diff = abs(audio_data.timestamp - video_data.timestamp)
                    print(f"🔄 SYNC {message} (Δt={time_diff*1000:.1f}ms)")
                    
            else:
                # Fallback avec données disponibles
                latest_audio_sensor = sync_buffer.get_latest_audio()
                latest_video_sensor = sync_buffer.get_latest_video()
                
                latest_audio = latest_audio_sensor.data if latest_audio_sensor else None
                latest_video = latest_video_sensor.data if latest_video_sensor else None
                
                message = message_generator.generate_fallback_message(
                    audio_only=latest_audio,
                    video_only=latest_video
                )
                
                sync_quality = 'fallback'
                if debug and (latest_audio or latest_video):
                    source = "audio" if latest_audio and not latest_video else \
                            "video" if latest_video and not latest_audio else "both_unsync"
                    print(f"[WARNING] FALLBACK {message} (source: {source})")
            
            # Préparer commande Arduino
            arduino_command = {
                'type': 'LCR_command',
                'message': message,
                'timestamp': current_time,
                'sync_quality': sync_quality
            }
            
            # Envoi série Arduino (à implémenter)
            if debug:
                print(f"➡️  Arduino: {message}")
            # TODO: Ajouter ici la communication série réelle
            # serial_port.write(message.encode() + b'\n')
            
            last_send_time = current_time
            
        except Exception as e:
            print(f"Arduino communication error: {e}")
            time.sleep(0.01)

def start_processing(no_audio=False, no_video=False, debug=False):
    """
    Function to start all processing threads

    Parameters
    ----------
    no_audio : bool
        If True, audio processing is disabled.
    no_video : bool
        If True, video processing is disabled.
    debug : bool
        If True, enables debug mode with verbose logging.
    """
    print("Starting processing threads...")
    
    # Initialize thread variables
    micro_thread = None
    video_thread = None
    
    if not no_audio:
        micro_thread = threading.Thread(target=micro_processing_thread, args=(debug,), daemon=True)
    
    if not no_video:
        video_thread = threading.Thread(target=video_processing_thread, args=(debug,), daemon=True)
    
    arduino_thread = threading.Thread(target=arduino_communication_thread, args=(debug,), daemon=True)
    
    if not no_audio and micro_thread:
        micro_thread.start()
        print("Micro processing thread started")
    
    if not no_video and video_thread:
        video_thread.start()
        print("Video processing thread started")
    
    arduino_thread.start()
    print("Arduino communication thread started")
    
    try:
        while True:
            time.sleep(5)
            queue_manager.print_stats()
    except Exception as e:
        print(f"Processing error: {e}")

# For individual tests
if __name__ == "__main__":
    start_processing()