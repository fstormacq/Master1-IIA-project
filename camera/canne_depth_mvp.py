# . .\.venv\Scripts\Activate.ps1
# python canne_depth_mvp.py
# q pour sortir 

#import pour la caméra , numpy pour les valeur de tableaux et calculs , 
#cv2 pour affichage et conversion image et deque pour effacer historique et tjrs garder la derniere image
import pyrealsense2 as rs # type: ignore
import numpy as np
import cv2
from collections import deque

# parametre de base pour la taille de la fenetre et la distance 
W, H, FPS = 640, 480, 30
D_ALERTE = 1.0     
D_ATTENTION = 2.0  
SMOOTH_N = 5       # (nb de frames)
# pour la taille du rectangle par rapport à la fenetre 
ROI_TOP = 0.10     
ROI_BOTTOM = 0.95
ROI_MARGIN_X = 0.10

# initialisation de la configuration de la caméra lors de son lancement 
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, W, H, rs.format.z16, FPS)
profile = pipeline.start(config)
depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()

#different historique pour le cote gauche centre et droit
history_center = deque(maxlen=SMOOTH_N)
history_left   = deque(maxlen=SMOOTH_N)
history_right  = deque(maxlen=SMOOTH_N)

#Prendre le rectangle et renvoye une distance moyenne en mètres.
def median_meters(arr_u16):
    arr = arr_u16.astype(np.float32) * depth_scale
    valid = arr[arr > 0]
    if valid.size == 0:
        return np.nan
    return float(np.median(valid))

#creation des mode en fonction de la distance 
def decide_mode(dist):
    if np.isnan(dist):
        return "PAISIBLE"
    if dist < D_ALERTE:
        return "ALERTE"
    if dist < D_ATTENTION:
        return "ATTENTION"
    return "PAISIBLE"
#lancement du programme si on veut quitter q
try:
    print("Initialisation caméra si tu veux sortir appuie sur q pour quitter)")
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            continue
        #Convertit la frame brute en tableau NumPy
        depth = np.asanyarray(depth_frame.get_data())
        #Calcul des zones (ROI)
        h, w = depth.shape
        y1, y2 = int(ROI_TOP*h), int(ROI_BOTTOM*h)
        x1, x2 = int(ROI_MARGIN_X*w), int((1-ROI_MARGIN_X)*w)
        #division du tableaux roi en 3 zones 
        third = (x2 - x1) // 3
        left  = depth[y1:y2, x1 : x1+third]
        center= depth[y1:y2, x1+third : x1+2*third]
        right = depth[y1:y2, x1+2*third : x2]
        #calcul les distance
        dL = median_meters(left)
        dC = median_meters(center)
        dR = median_meters(right)
        #on ajoutes les distances 
        history_left.append(dL)
        history_center.append(dC)
        history_right.append(dR)

        dL_s = np.nanmedian(history_left)
        dC_s = np.nanmedian(history_center)
        dR_s = np.nanmedian(history_right)

        mode = decide_mode(dC_s)
        distances = {'DROITE': dL_s, 'DEVANT': dC_s, 'GAUCHE': dR_s}
        best_dir = max(distances, key=lambda k: np.nan_to_num(distances[k], nan=-1.0))

        depth_vis = cv2.convertScaleAbs(depth, alpha=0.03)
        depth_vis = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)
        cv2.rectangle(depth_vis, (x1, y1), (x2, y2), (255,255,255), 2)
        cv2.putText(depth_vis, f"{mode} - Dir: {best_dir}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        # quitter = q 
        cv2.imshow("Depth (D435)", depth_vis)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
#arret de la caméra et fermeture de la fenetre
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
