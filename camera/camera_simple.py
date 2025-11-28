"""
Module caméra simple pour tester la queue vidéo
Génère des frames factices pour le moment
"""

import numpy as np
import time
import threading
from queue_manager import queue_manager

def generate_fake_frame():
    """Générer une frame factice pour les tests"""
    # Frame RGB 640x480 avec du bruit aléatoire
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    return frame

def start_video_capture():
    """Fonction pour démarrer la capture vidéo (simulation)"""
    global video_running
    
    print("📹 Starting video capture...")
    print("   Resolution: 640x480")
    print("   FPS: 10 (simulation)")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            frame = generate_fake_frame()
            frame_count += 1
            
            queue_manager.put_video_data(frame)
            
            # Debug: afficher les premières frames
            if frame_count <= 5 or frame_count % 50 == 0:
                print(f"📦 Video frame #{frame_count} sent (shape: {frame.shape})")
            
            # Simuler 10 FPS
            time.sleep(0.1)
            
            # Stats périodiques
            elapsed = time.time() - start_time
            if elapsed > 0 and frame_count % 100 == 0:
                fps = frame_count / elapsed
                print(f"📊 Video: {frame_count} frames in {elapsed:.1f}s ({fps:.1f} FPS)")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Video capture stopped")
        print(f"   Total frames: {frame_count}")
    except Exception as e:
        print(f"❌ Video capture error: {e}")

# Variable globale pour éviter les doubles lancements
video_running = False

def start_video_capture_safe():
    """Version sécurisée qui évite les doubles lancements"""
    global video_running
    
    if video_running:
        print("Video capture already running, skipping.")
        return
    
    video_running = True
    start_video_capture()

# Pour les tests individuels
if __name__ == "__main__":
    start_video_capture_safe()