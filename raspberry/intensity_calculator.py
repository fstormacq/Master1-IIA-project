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
            return max(0, int((db_level + 60) * 20 / 15))  #-60 à -45 → 0 à 20
        elif db_level < -30:
            return int(20 + (db_level + 45) * 30 / 15)      #-45 à -30 → 20 à 50
        elif db_level < -15:
            return int(50 + (db_level + 30) * 30 / 15)      #-30 à -15 → 50 à 80
        else:
            return min(100, int(80 + (db_level + 15) * 20 / 10))  #-15+ → 80-100
    
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
            distance = distances.get(zone, 5.0)  #5m by default
            
            # Handle NaN
            if not isinstance(distance, (int, float)) or distance != distance: # Check for NaN
                distance = 5.0

            #Intensity based on distance
            # Nouvelle logique demandée : plus sensible et portée étendue
            if distance <= 1.2:
                base_intensity = 100  # Max danger immédiat
            elif distance <= 2.5:
                # De 1.2m à 2.5m : on passe de 100 à 60
                # Formule linéaire : 100 - (dist - 1.2) * (40/1.3)
                base_intensity = int(100 - (distance - 1.2) * 30)
            elif distance <= 4.0:
                # De 2.5m à 4.0m : on passe de 60 à 20
                # Formule linéaire : 60 - (dist - 2.5) * (40/1.5)
                base_intensity = int(60 - (distance - 2.5) * 26)
            else:
                # Au delà de 4m jusqu'à 5m : faible intensité
                base_intensity = max(0, int((5.0 - distance) * 20))

            #For obstacles
            zone_mapping = {'gauche': 'Gauche', 'centre': 'Centre', 'droite': 'Droite'}
            if zone_mapping[zone] in obstacles:
                base_intensity += 20
                
            zones[zone] = max(0, min(100, base_intensity))
            
        return zones