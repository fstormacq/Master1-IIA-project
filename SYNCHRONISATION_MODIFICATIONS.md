# Modifications pour la Synchronisation Audio-Vidéo et Messages LCR Arduino

## Vue d'ensemble

Ce document détaille les modifications à apporter pour implémenter la synchronisation temporelle entre audio et vidéo, ainsi que la génération de messages structurés `L...C...R...` pour l'Arduino.

## Architecture proposée

### Approche centralisée dans `arduino_communication_thread`
- **Avantage** : Centralise toute la logique de synchronisation et génération LCR
- **Principe** : Le thread Arduino devient responsable de collecter, synchroniser et fusionner les données

---

## 1. Modifications du `QueueManager`

### 1.1 Nouvelles queues pour données traitées

**Fichier :** `queue_manager.py`

**Ajouter dans `__init__()` :**
```python
# Nouvelles queues pour données processées avec timestamp
self.audio_processed_queue = Queue(maxsize=5)
self.video_processed_queue = Queue(maxsize=5)

# Compteurs pour les nouvelles queues
self.dropped_audio_processed_count = 0
self.dropped_video_processed_count = 0
self.total_audio_processed_count = 0
self.total_video_processed_count = 0
```

### 1.2 Nouvelles méthodes de gestion

**Ajouter les méthodes suivantes :**

```python
def put_audio_processed_data(self, data):
    """Ajoute des données audio traitées avec timestamp"""
    self.total_audio_processed_count += 1
    
    try:
        self.audio_processed_queue.put_nowait((data, time.time()))
    except Full:
        self.dropped_audio_processed_count += 1
        # Drop oldest data
        try:
            self.audio_processed_queue.get_nowait()
            self.audio_processed_queue.put_nowait((data, time.time()))
        except Empty:
            pass

def get_audio_processed_data(self, timeout=0.01):
    """Récupère des données audio traitées"""
    result = self.audio_processed_queue.get(timeout=timeout)
    return result[0] if isinstance(result, tuple) else result

def put_video_processed_data(self, data):
    """Ajoute des données vidéo traitées avec timestamp"""
    self.total_video_processed_count += 1
    
    try:
        self.video_processed_queue.put_nowait((data, time.time()))
    except Full:
        self.dropped_video_processed_count += 1
        # Drop oldest data
        try:
            self.video_processed_queue.get_nowait()
            self.video_processed_queue.put_nowait((data, time.time()))
        except Empty:
            pass

def get_video_processed_data(self, timeout=0.01):
    """Récupère des données vidéo traitées"""
    result = self.video_processed_queue.get(timeout=timeout)
    return result[0] if isinstance(result, tuple) else result

def peek_latest_audio(self):
    """Récupère la dernière donnée audio sans la retirer de la queue"""
    if self.audio_processed_queue.empty():
        return None
    # Technique: get puis remet immédiatement
    try:
        data = self.audio_processed_queue.get_nowait()
        self.audio_processed_queue.put_nowait(data)
        return data[0] if isinstance(data, tuple) else data
    except (Empty, Full):
        return None

def peek_latest_video(self):
    """Récupère la dernière donnée vidéo sans la retirer de la queue"""
    if self.video_processed_queue.empty():
        return None
    try:
        data = self.video_processed_queue.get_nowait()
        self.video_processed_queue.put_nowait(data)
        return data[0] if isinstance(data, tuple) else data
    except (Empty, Full):
        return None
```

### 1.3 Mise à jour des statistiques

**Modifier `get_queue_stats()` pour inclure :**
```python
# Ajouter dans le dictionnaire retourné
'audio_processed_queue_size': self.audio_processed_queue.qsize(),
'video_processed_queue_size': self.video_processed_queue.qsize(),
'audio_processed_dropped': self.dropped_audio_processed_count,
'video_processed_dropped': self.dropped_video_processed_count,
'audio_processed_total': self.total_audio_processed_count,
'video_processed_total': self.total_video_processed_count,
```

---

## 2. Modifications de `raspberry.py`

### 2.1 Import et classes utilitaires

**Ajouter en haut du fichier :**

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
from collections import deque
```

### 2.2 Classes de synchronisation

**Ajouter après les imports :**

```python
@dataclass
class SensorData:
    """Structure pour les données de capteur avec timestamp"""
    timestamp: float
    data: Dict[Any, Any]
    source: str  # 'audio' ou 'video'

class IntensityCalculator:
    """Calculateur d'intensités pour les messages LCR"""
    
    @staticmethod
    def audio_to_intensity(db_level: float) -> int:
        """Convertit le niveau dB en intensité 0-100"""
        if db_level < -45:
            return max(0, int((db_level + 60) * 20 / 15))  # -60 à -45 → 0 à 20
        elif db_level < -30:
            return int(20 + (db_level + 45) * 30 / 15)      # -45 à -30 → 20 à 50
        elif db_level < -15:
            return int(50 + (db_level + 30) * 30 / 15)      # -30 à -15 → 50 à 80
        else:
            return min(100, int(80 + (db_level + 15) * 20 / 10))  # -15+ → 80-100
    
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
```

### 2.3 Modification des threads de traitement

**Modifier `micro_processing_thread()` :**

```python
def micro_processing_thread(debug=False):
    """Processing thread dedicated to microphone audio data"""
    processing_count = 0
    
    while True:
        try:
            chunk = queue_manager.get_micro_data()
            processing_count += 1
            
            # Traitement audio lourd
            result = heavy_audio_processing(chunk, debug)
            
            # NOUVEAU: Envoyer vers la queue de données traitées
            queue_manager.put_audio_processed_data(result)
            
            # Debug
            if debug:
                print(f"Audio #{processing_count}: {result['db_level']:.1f}dB - {result['sound_classification']}")
                
        except Empty:
            continue
        except Exception as e:
            print(f"Micro processing error: {e}")
```

**Modifier `video_processing_thread()` :**

```python
def video_processing_thread(debug=False):
    """Processing thread dedicated to video data"""
    processing_count = 0
    
    while True:
        try:
            video_data = queue_manager.get_video_data(timeout=1.0)
            processing_count += 1
            
            result = heavy_video_processing(video_data, debug)
            
            # NOUVEAU: Envoyer vers la queue de données traitées
            queue_manager.put_video_processed_data(result)
            
            if debug:
                distances = result['distances']
                print(f"Video #{processing_count}: {result['mode']} | Obstacles: {result['obstacle_info']} | "
                        f"G={distances['gauche']:.2f}m C={distances['centre']:.2f}m D={distances['droite']:.2f}m")
                
        except Empty:
            continue
        except Exception as e:
            print(f"Video processing error: {e}")
```

### 2.4 Remplacement complet d'`arduino_communication_thread()`

**Remplacer la fonction existante par :**

```python
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
```

---

## 3. Avantages de cette approche

### 3.1 Centralisation intelligente
- ✅ **Une seule responsabilité** : `arduino_communication_thread` gère tout
- ✅ **Pas de thread supplémentaire** : réutilise l'existant
- ✅ **Logique claire** : synchronisation + génération + envoi au même endroit

### 3.2 Performance optimisée
- ✅ **Fréquence contrôlée** : 25Hz max, pas de spam Arduino
- ✅ **Buffer temporel intelligent** : 150ms de fenêtre de synchronisation
- ✅ **Fallback robuste** : fonctionne même si une source manque

### 3.3 Debugging et monitoring
- ✅ **Traces détaillées** : qualité de sync, timestamps, sources
- ✅ **Statistiques étendues** : nouvelles queues dans le monitoring
- ✅ **Messages LCR lisibles** : `L042C087R023` 

---

## 4. Séquence de mise en œuvre

### Étape 1 : QueueManager
1. Ajouter les nouvelles queues et méthodes dans `queue_manager.py`
2. Tester les nouvelles fonctions isolément

### Étape 2 : Classes utilitaires
1. Ajouter les classes `SensorData`, `IntensityCalculator`, etc. dans `raspberry.py`
2. Tester les calculs d'intensité avec des données fictives

### Étape 3 : Modification des threads
1. Modifier `micro_processing_thread()` pour utiliser `put_audio_processed_data()`
2. Modifier `video_processing_thread()` pour utiliser `put_video_processed_data()`
3. Tester que les données arrivent bien dans les nouvelles queues

### Étape 4 : Arduino thread
1. Remplacer complètement `arduino_communication_thread()`
2. Tester la synchronisation et génération LCR
3. Ajouter la communication série réelle

### Étape 5 : Tests et calibrage
1. Ajuster les seuils d'intensité selon vos besoins
2. Optimiser les paramètres de synchronisation (fenêtre, fréquence)
3. Valider avec des données réelles

---

## 5. Configuration et paramètres

### Paramètres ajustables
```python
# Dans SyncBuffer
max_age_ms = 150          # Fenêtre de synchronisation

# Dans arduino_communication_thread  
send_interval = 1.0 / 25.0  # Fréquence d'envoi (25Hz)

# Dans LCRMessageGenerator
audio_side_factor = 0.7   # Influence audio sur côtés
sync_threshold = 0.05     # Seuil sync (50ms)
```

### Seuils d'intensité audio
- `< -45 dB` → 0-20 (Calme)
- `-45 à -30 dB` → 20-50 (Bruit léger)  
- `-30 à -15 dB` → 50-80 (Attention)
- `> -15 dB` → 80-100 (Danger)

### Seuils d'intensité vision
- `> 2m` → 0-15 (Sûr)
- `1-2m` → 15-70 (Prudence)
- `< 1m` → 70-100 (Danger)
- `+20` si obstacle détecté dans la zone

---

## 6. Messages Arduino finaux

### Format
`L{000-100}C{000-100}R{000-100}`

### Exemples
- `L000C000R000` : Repos total
- `L023C087R012` : Obstacle centre, bruit ambiant  
- `L075C045R080` : Obstacles gauche/droite, audio modéré
- `L100C100R100` : Danger critique partout

Cette architecture vous donnera une synchronisation robuste et des messages Arduino cohérents ! 🚀