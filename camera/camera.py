#note a faire changer les noms des variables en francais pour etre cohérent avec le reste du code
#note changer le gauhe droite devant car le gauche est devant le milieu est guche et droite est droite 
#prendre en compte que seul la zone au milieu est prise en compte pour le mode si il y'a du dangerq

import pyrealsense2 as rs # type: ignore
import numpy as np 
import cv2
import time
from collections import deque
from queue_manager import queue_manager

Distance_Area_Attention = 2.0
Distance_Area_Alert = 1.0
Nbr_frames_max_history = 5     
Rectangle_Margin_Y = 0.10
Rectangle_Margin_X = 0.10
W = 640
H = 480
FPS = 10 

# Variables globales pour le système
camera_running = False
pipeline = None
depth_scale = None

# function that gives the median distance in meters for a given area
def median_calculator(zone_pixels): 
    array = zone_pixels.astype(np.float32) * depth_scale 
    valid_array = array[array > 0] 
    if valid_array.size == 0: 
        return np.nan 
    return float(np.median(valid_array))

# Give the mode according to the distance
def Danger_zone(distance):
    if np.isnan(distance):
        return "paisible"
    if distance < Distance_Area_Alert:
        return "alerte y a un truc a moins d 1 metre"
    if distance <= Distance_Area_Attention:
        return "attention y a un truc a moins d 2 metre"
    
    return "paisible"

# function that gives the median distance in meters for a given area
def median_calculator(zone_pixels): 
    array = zone_pixels.astype(np.float32) * depth_scale 
    valid_array = array[array > 0] 
    if valid_array.size == 0: 
        return np.nan 
    return float(np.median(valid_array))

# Give the mode according to the distance
def Danger_zone(distance):
    if np.isnan(distance):
        return "paisible"
    if distance < Distance_Area_Alert:
        return "alerte y a un truc a moins d 1 metre"
    if distance <= Distance_Area_Attention:
        return "attention y a un truc a moins d 2 metre"
    
    return "paisible"

def process_frame(depth_frame):
    """Traiter une frame et retourner les données analysées"""
    depth = np.asanyarray(depth_frame.get_data()) 
    h, w = depth.shape 
    y1, y2 = int(Rectangle_Margin_Y*h), int((1-Rectangle_Margin_Y)*h)        
    x1, x2 = int(Rectangle_Margin_X*w), int((1-Rectangle_Margin_X)*w)

    third = (x2 - x1) // 3 
    zone_left  = depth[y1:y2, x1 : x1+third]
    zone_center= depth[y1:y2, x1+third : x1+2*third]
    zone_right = depth[y1:y2, x1+2*third : x2]
    
    distance_left   = median_calculator(zone_left)
    distance_center = median_calculator(zone_center)
    distance_right  = median_calculator(zone_right)
    
    return {
        'raw_depth': depth,
        'distances': {
            'gauche': distance_left,
            'centre': distance_center,
            'droite': distance_right
        },
        'zones': {
            'left': zone_left,
            'center': zone_center,
            'right': zone_right
        },
        'timestamp': time.time()
    }

def start_video_capture():
    """Fonction principale de capture vidéo avec RealSense"""
    global camera_running, pipeline, depth_scale
    
    if camera_running:
        print("Camera already running, skipping.")
        return
    
    camera_running = True
    
    print("📹 Starting RealSense camera capture...")
    print(f"   Resolution: {W}x{H}")
    print(f"   FPS: {FPS}")
    
    # Initialisation du pipeline
    pipeline = rs.pipeline() 
    config = rs.config() 
    config.enable_stream(rs.stream.depth, W, H, rs.format.z16, FPS) 
    
    try:
        camera = pipeline.start(config) 
        depth_scale = camera.get_device().first_depth_sensor().get_depth_scale()
        print(f"   Depth scale: {depth_scale}")
        
        # Historiques pour le lissage
        history_center = deque(maxlen=Nbr_frames_max_history)  
        history_left   = deque(maxlen=Nbr_frames_max_history) 
        history_right  = deque(maxlen=Nbr_frames_max_history)
        
        frame_count = 0
        start_time = time.time()
        
        print("🎬 Camera capture started...")
        
        while camera_running:
            frame = pipeline.wait_for_frames() 
            depth_frame = frame.get_depth_frame() 
            if not depth_frame:
                continue
                
            frame_count += 1
            
            # Traiter la frame
            frame_data = process_frame(depth_frame)
            
            # Ajouter à l'historique pour le lissage
            history_left.append(frame_data['distances']['gauche'])
            history_center.append(frame_data['distances']['centre'])
            history_right.append(frame_data['distances']['droite'])
            
            # Calculer les distances lissées
            distance_left_smooth   = np.nanmedian(history_left) 
            distance_center_smooth = np.nanmedian(history_center)
            distance_right_smooth  = np.nanmedian(history_right)
            
            # Analyser la scène
            mode = Danger_zone(distance_center_smooth)
            distance = {'Gauche': distance_left_smooth, 'Centre': distance_center_smooth, 'Droite': distance_right_smooth}
            
            obstacle = []
            if distance_left_smooth <= Distance_Area_Alert:
                obstacle.append('Gauche')
            if distance_center_smooth <= Distance_Area_Alert:
                obstacle.append('Centre')
            if distance_right_smooth <= Distance_Area_Alert:
                obstacle.append('Droite')
           
            if len(obstacle) == 0:
                obstacle_info = "Aucun"
            elif len(obstacle) == 1:
                obstacle_info = obstacle[0]
            else:
                obstacle_info = ' et '.join(obstacle)

            avoid_danger = max(distance, key=lambda k: np.nan_to_num(distance[k], nan=-1.0))
            
            # Créer les données complètes à envoyer
            video_data = {
                'frame_number': frame_count,
                'mode': mode,
                'obstacle_info': obstacle_info,
                'avoid_direction': avoid_danger,
                'distances_raw': frame_data['distances'],
                'distances_smooth': {
                    'gauche': distance_left_smooth,
                    'centre': distance_center_smooth,
                    'droite': distance_right_smooth
                },
                'obstacles': obstacle,
                'timestamp': frame_data['timestamp']
            }
            
            # Envoyer à la queue
            queue_manager.put_video_data(video_data)
            
            # Debug: afficher les premières frames
            if frame_count <= 5 or frame_count % 50 == 0:
                print(f"📦 Video frame #{frame_count}: {mode}, Obstacles: {obstacle_info}")
            
            # Stats périodiques
            elapsed = time.time() - start_time
            if elapsed > 0 and frame_count % 100 == 0:
                fps = frame_count / elapsed
                print(f"📊 Video: {frame_count} frames in {elapsed:.1f}s ({fps:.1f} FPS)")
                print(f"     Current: {mode}, Distances: G={distance_left_smooth:.2f}m C={distance_center_smooth:.2f}m D={distance_right_smooth:.2f}m")
        
    except KeyboardInterrupt:
        print("\n🛑 Camera capture stopped by user")
    except Exception as e:
        print(f"❌ Camera capture error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if pipeline:
            pipeline.stop()
        camera_running = False
        print(f"📹 Camera stopped. Total frames: {frame_count}")

# Pour les tests individuels
if __name__ == "__main__":
    try:
        start_video_capture()
    except KeyboardInterrupt:
        print("Camera test stopped")
