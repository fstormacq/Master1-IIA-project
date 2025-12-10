from typing import Optional, Dict, Any

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
            return max(0, int((db_level + 60) * 20 / 15))  # -60 to -45 → 0 to 20
        elif db_level < -30:
            return int(20 + (db_level + 45) * 30 / 15)      # -45 to -30 → 20 to 50
        elif db_level < -15:
            return int(50 + (db_level + 30) * 30 / 15)      # -30 to -15 → 50 to 80
        else:
            return min(100, int(80 + (db_level + 15) * 20 / 10))  # -15+ → 80-100
    
    @staticmethod
    def vision_to_intensity_by_zone(distances: Dict[str, float], obstacles: list) -> Dict[str, int]:
        """
        Convert distances and obstacles to intensities for left, center, right zones
        
        Parameters
        ----------
        distances : Dict[str, float]
            Distances for 'gauche', 'centre', 'droite' zones
        obstacles : list
            List of detected obstacles (e.g., ['Gauche', 'Centre'])
        
        Returns
        -------
        Dict[str, int]
            Intensities for 'gauche', 'centre', 'droite' zones (0-100)
        """
        zones = {'gauche': 0, 'centre': 0, 'droite': 0}
        
        for zone in zones.keys():
            distance = distances.get(zone, 5.0)  # 5m by default
            
            # Intensity based on distance
            if distance > 2.0:
                base_intensity = max(0, int((3.0 - distance) * 15))  # 0-15 for >2m
            elif distance > 1.0:
                base_intensity = int(15 + (2.0 - distance) * 55)     # 15-70 for 1-2m
            else:
                base_intensity = int(70 + (1.0 - distance) * 30)     # 70-100 for <1m
            
            # Boost intensity for obstacles
            zone_mapping = {'gauche': 'Gauche', 'centre': 'Centre', 'droite': 'Droite'}
            if zone_mapping[zone] in obstacles:
                base_intensity += 20
                
            zones[zone] = max(0, min(100, base_intensity))
            
        return zones