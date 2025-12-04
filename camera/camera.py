#note a faire changer les noms des variables en francais pour etre cohérent avec le reste du code (??? => l'inverse nan ?)
#note changer le gauhe droite devant car le gauche est devant le milieu est guche et droite est droite 
#prendre en compte que seul la zone au milieu est prise en compte pour le mode si il y'a du dangerq

import pyrealsense2 as rs #type: ignore
import numpy as np 
import cv2 # ?
import time
from collections import deque
from queue_manager import queue_manager
import traceback


# Camera parameters
DISTANCE_AREA_ATTENTION = 2.0
DISTANCE_AREA_ALERT = 1.0

FRAMES_HISTORY = 5     

RECT_MARGIN_Y = 0.10
RECT_MARGIN_X = 0.10

W = 640
H = 480

FPS = 15

#Global Variables
CAMERA_RUNNING = False #Flag to indicate if the camera is running

PIPELINE = None
DEPTH_SCALE = None

USE_SIMULATION = True  #Flag to simulate RealSense data when camera is not available

def check_realsense_available(pyrealsense=True):
    """Check if RealSense camera is available
    
    Returns
    -------
    bool
        True if Pyrealsense2 is imported, False otherwise.
        
    Notes
    -----
    This function attempts to initialize a RealSense pipeline and configure it to stream depth data.
    """
    if not pyrealsense:
        return False
    
    try:
        test_pipeline = rs.pipeline()
        test_config = rs.config()
        test_config.enable_stream(rs.stream.depth, W, H, rs.format.z16, FPS)
        
        camera = test_pipeline.start(test_config)

        test_depth_scale = camera.get_device().first_depth_sensor().get_depth_scale()
        test_pipeline.stop()
        return True
        
    except Exception as e:
        print(f"RealSense detection error: {e}")
        return False

def simulate_realsense_data():
    """
    Simulate RealSense depth data for testing purposes.

    Returns
    -------
    dict
        Simulated depth data including distances for left, center, and right zones, and a timestamp.

    Notes
    -----
    This function generates random distances to mimic the behavior of a RealSense camera. 
    Usage of this function is intended for testing when the actual camera hardware is not available, or on macOS systems.
    """
    #Generate random distances between 0.5m and 4.0m
    center_dist = np.random.uniform(1.5, 4.0) 
    left_dist = np.random.uniform(1.0, 3.5)
    right_dist = np.random.uniform(1.2, 4.2)
    
    #Generate occasional obstacles
    if np.random.random() < 0.1: 
        center_dist = np.random.uniform(0.3, 0.9)
    
    return {
        'distances': {
            'gauche': left_dist,
            'centre': center_dist,
            'droite': right_dist
        },
        'timestamp': time.time()
    }

def median_calculator(zone_pixels): 
    """
    Compute the median distance from depth pixels in a specified zone.

    Parameters
    ----------
    zone_pixels : np.ndarray
        Array of depth pixel values for the zone.

    Returns
    -------
    float
        The median distance in meters for the zone. Returns NaN if no valid pixels are found.
    """
    if USE_SIMULATION:
        return np.random.uniform(1.0, 4.0)  #Simulated distance 
        
    array = zone_pixels.astype(np.float32) * DEPTH_SCALE 
    valid_array = array[array > 0] 
    if valid_array.size == 0: 
        return np.nan 
    
    return float(np.median(valid_array))

def Danger_zone(distance):
    """
    Determine the danger zone based on the given distance.
    """
    if np.isnan(distance):
        return "paisible"
    if distance < DISTANCE_AREA_ALERT:
        return "alerte y a un truc a moins d 1 metre"
    if distance <= DISTANCE_AREA_ATTENTION:
        return "attention y a un truc a moins d 2 metre"
    
    return "paisible"

def process_frame(depth_frame):
    """
    Process a single depth frame from the RealSense camera or simulate data.

    Parameters
    ----------
    depth_frame : rs.depth_frame or None
        The depth frame from the RealSense camera. If None, simulation mode is used.

    Returns
    -------
    dict
        Processed frame data including raw depth array, distances for left, center, and right zones, 
        zone pixel data, and a timestamp.
    """
    if USE_SIMULATION:
        sim_data = simulate_realsense_data()
        return {
            'raw_depth': None,
            'distances': sim_data['distances'],
            'zones': None,
            'timestamp': sim_data['timestamp']
        }
    
    #Standard RealSense mode
    depth = np.asanyarray(depth_frame.get_data()) 
    h, w = depth.shape 
    y1, y2 = int(RECT_MARGIN_Y*h), int((1-RECT_MARGIN_Y)*h)        
    x1, x2 = int(RECT_MARGIN_X*w), int((1-RECT_MARGIN_X)*w)

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

def start_video_capture(debug=False):
    """
    Start capturing video from the RealSense camera or simulate data if not available.

    Parameters
    ----------
    debug : bool
        If True, enables debug mode with verbose logging.

    Notes
    -----
    This function initializes the RealSense camera and continuously captures depth frames. If the camera is not available, it switches to simulation mode, generating random depth data.
    The captured or simulated data is processed and sent to the video queue for further handling.
    """
    global CAMERA_RUNNING, PIPELINE, DEPTH_SCALE, USE_SIMULATION
    
    if CAMERA_RUNNING:
        if debug:
            print("Camera already running, skipping.")
        return
    
    CAMERA_RUNNING = True
    
    realsense_available = check_realsense_available()
    
    if realsense_available:
        print("Starting RealSense camera capture...")
        USE_SIMULATION = False
    else:
        print("[WARNING] RealSense not available - using simulation mode")
        USE_SIMULATION = True
    
    print(f"   Resolution: {W}x{H}")
    print(f"   FPS: {FPS}")
    print(f"   Using simulation: {USE_SIMULATION}")

    try:
        if not USE_SIMULATION:

            PIPELINE = rs.pipeline() 
            config = rs.config() 
            config.enable_stream(rs.stream.depth, W, H, rs.format.z16, FPS) 
            
            camera = PIPELINE.start(config) 
            DEPTH_SCALE = camera.get_device().first_depth_sensor().get_depth_scale()

            print(f"   Depth scale: {DEPTH_SCALE}")
        else:
            #Simulation mode
            DEPTH_SCALE = 0.001
            print("   Using simulated depth data")
        
        history_center = deque(maxlen=FRAMES_HISTORY)  
        history_left   = deque(maxlen=FRAMES_HISTORY) 
        history_right  = deque(maxlen=FRAMES_HISTORY)
        
        frame_count = 0
        start_time = time.time()
        
        if debug:
            print("Camera capture started...")
        
        while CAMERA_RUNNING:
            if USE_SIMULATION:
                frame_data = process_frame(None)
                time.sleep(1.0/FPS)  #Respect the framerate
            else:
                frame = PIPELINE.wait_for_frames() 
                depth_frame = frame.get_depth_frame() 
                if not depth_frame:
                    if debug:
                        print('[DEBUG] No depth frame received, skipping...')
                    continue
                frame_data = process_frame(depth_frame)
                
            frame_count += 1
            
            history_left.append(frame_data['distances']['gauche'])
            history_center.append(frame_data['distances']['centre'])
            history_right.append(frame_data['distances']['droite'])
            
            distance_left_smooth   = np.nanmedian(history_left) 
            distance_center_smooth = np.nanmedian(history_center)
            distance_right_smooth  = np.nanmedian(history_right)
            
            mode = Danger_zone(distance_center_smooth)
            distance = {'Gauche': distance_left_smooth, 'Centre': distance_center_smooth, 'Droite': distance_right_smooth}
            
            obstacle = []
            if distance_left_smooth <= DISTANCE_AREA_ALERT:
                obstacle.append('Gauche')
            if distance_center_smooth <= DISTANCE_AREA_ALERT:
                obstacle.append('Centre')
            if distance_right_smooth <= DISTANCE_AREA_ALERT:
                obstacle.append('Droite')
           
            if len(obstacle) == 0:
                obstacle_info = "Aucun"
            elif len(obstacle) == 1:
                obstacle_info = obstacle[0]
            else:
                obstacle_info = ' et '.join(obstacle)

            avoid_danger = max(distance, key=lambda k: np.nan_to_num(distance[k], nan=-1.0))
            
            #Need to minimize data sent to queue 
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
                'timestamp': frame_data['timestamp'],
                'simulation_mode': USE_SIMULATION
            }

            queue_manager.put_video_data(video_data)
            
            if debug:
                sim_tag = "[SIM] " if USE_SIMULATION else ""
                print(f"{sim_tag}Video frame #{frame_count}: {mode}, Obstacles: {obstacle_info}")
            
            #Periodic stats - made with github copilot
            if debug:
                elapsed = time.time() - start_time
                if elapsed > 0 and frame_count % 100 == 0:
                    fps = frame_count / elapsed
                    sim_tag = "[SIMULATION] " if USE_SIMULATION else ""
                    print(f"{sim_tag}Video: {frame_count} frames in {elapsed:.1f}s ({fps:.1f} FPS)")
                    print(f"     Current: {mode}, Distances: G={distance_left_smooth:.2f}m C={distance_center_smooth:.2f}m D={distance_right_smooth:.2f}m")
        
    except KeyboardInterrupt:
        print("\nCamera capture stopped by user")
    except Exception as e:
        print(f"Camera capture error: {e}")
        traceback.print_exc()
    finally:
        if PIPELINE and not USE_SIMULATION:
            try:
                PIPELINE.stop()
            except Exception as e:
                print(f"Warning: Error stopping pipeline: {e}")
        CAMERA_RUNNING = False
        if debug:
            sim_tag = "[SIMULATION] " if USE_SIMULATION else ""
            print(f"{sim_tag}Camera stopped. Total frames: {frame_count}")

if __name__ == "__main__":
    try:
        start_video_capture()
    except KeyboardInterrupt:
        print("Camera stopped")
