import pyrealsense2 as rs
import numpy as np 
import cv2
from collections import deque


Distance_Area_Attention = 1.0
Distance_Area_Alert = 2.0
Nbr_frames_max_history = 5     
Rectangle_Margin_Y = 0.10
Rectangle_Margin_X = 0.10
W = 640
H = 480
FPS = 30 

pipeline = rs.pipeline() 
config = rs.config() 
config.enable_stream(rs.stream.depth, W, H, rs.format.z16, FPS) 
camera = pipeline.start(config) 
depth_scale = camera.get_device().first_depth_sensor().get_depth_scale() 

history_center = deque(maxlen=Nbr_frames_max_history)  
history_left   = deque(maxlen=Nbr_frames_max_history) 
history_right  = deque(maxlen=Nbr_frames_max_history)

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
    if distance < Distance_Area_Attention:
        return "attention"
    if distance < Distance_Area_Alert:
        return "alerte"
    return "paisible"

# Main loop that captures frames and process them and display the results of the mode and the direction of the obstacle
try:
    print("Starting the system, press Ctrl+C to stop.")
    while True:
        frame = pipeline.wait_for_frames() 
        depth_frame = frame.get_depth_frame() 
        if not depth_frame:
            continue
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
        history_left.append(distance_left)
        history_center.append(distance_center)
        history_right.append(distance_right)
        distance_left_smooth   = np.nanmedian(history_left) 
        distance_center_smooth = np.nanmedian(history_center)
        distance_right_smooth  = np.nanmedian(history_right)

        mode = Danger_zone(distance_center_smooth)
        distance = {'Gauche': distance_left_smooth, 'Centre': distance_center_smooth, 'Droite': distance_right_smooth}
        #obstacle = min(distance, key=lambda k: np.nan_to_num(distance[k], nan=-1.0))
        obstacle = []
        if distance_left_smooth <= Distance_Area_Alert:
            obstacle.append('Gauche')
        if distance_center_smooth <= Distance_Area_Alert:
            obstacle.append('Centre')
        if distance_right_smooth <= Distance_Area_Alert:
            obstacle.append('Droite')
       
        if len(obstacle) == 0:
            obstacle_info = "Aucun"
        if len(obstacle) == 1:
            obstacle_info = obstacle[0]
        else:
            obstacle_info = ' et '.join(obstacle)

        avoid_danger = max(distance, key=lambda k: np.nan_to_num(distance[k], nan=-1.0)) 
        
        #depth_vis = cv2.convertScaleAbs(depth, alpha=0.03) 
        #depth_vis = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET) 
        #cv2.rectangle(depth_vis, (x1, y1), (x2, y2), (255,255,255), 2) 
        #cv2.putText(depth_vis, f"Devant toi {mode} Obstacle: {obstacle} Eviter: {avoid_danger}", (10,30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2) 
        #cv2.putText(depth_vis,f"Devant toi {mode}   Obstacles: {obstacle_info}   Eviter: {avoid_danger}",(10,30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        #cv2.imshow("Depth (D435)", depth_vis) 

        #if cv2.waitKey(1) & 0xFF == ord('q'):  
            #break

        print(f"Au centre: {mode}, Obstacle: {obstacle_info}, Aller: {avoid_danger}, Distances: G={distance_left_smooth:.2f}m C={distance_center_smooth:.2f}m D={distance_right_smooth:.2f}m")

except KeyboardInterrupt:
    print("Stop da system")

finally:
    pipeline.stop()  
    #cv2.destroyAllWindows()
