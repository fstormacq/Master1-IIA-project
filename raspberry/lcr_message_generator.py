
from raspberry.intensity_calculator import IntensityCalculator
from typing import Optional, Dict, Any

class LCRMessageGenerator:
    """
    Generates LCR messages for Arduino based on audio and video data
    """
    
    def __init__(self):
        self.last_message = "L000C000R000"
        self.message_count = 0
        
    def generate_synchronized_message(self, audio_data=None, video_data=None) -> str:
        """
        Generates an LCR message based on audio and video data
        
        Parameters
        ----------
        audio_data : Optional[Dict]
            Processed audio data containing 'db_level'
            
        video_data : Optional[Dict]
            Processed video data containing 'distances' and 'obstacles'
            
        Returns
        -------
        str
            Formatted LCR message
        """
        left_intensity = 0
        center_intensity = 0
        right_intensity = 0
        
        #Audio processing (global influence)
        audio_intensity = 0
        if audio_data:
            audio_intensity = IntensityCalculator.audio_to_intensity(
                audio_data['db_level']
            )
        
        #Video processing (zonal influence)
        vision_intensities = {'gauche': 0, 'centre': 0, 'droite': 0}
        if video_data:
            vision_intensities = IntensityCalculator.vision_to_intensity_by_zone(
                video_data['distances'],
                video_data.get('obstacles', [])
            )
        
        # Use weighted average: 80% vision, 20% audio (reduced for lateral zones)
        left_intensity = (4 * vision_intensities['gauche'] + int(audio_intensity * 0.7)) / 5
        
        center_intensity = (4 * vision_intensities['centre'] + int(audio_intensity)) / 5
        
        right_intensity = (4 * vision_intensities['droite'] + int(audio_intensity * 0.7)) / 5
        
        message = f"L{left_intensity:03d}C{center_intensity:03d}R{right_intensity:03d}"
        
        self.last_message = message
        self.message_count += 1
        
        return message
    
    def generate_fallback_message(self, audio_only=None, video_only=None) -> str:
        """
        Generate fallback LCR message when only one modality is available
        
        Parameters
        ----------
        audio_only : Optional[Dict]
            Processed audio data containing 'db_level'
            
        video_only : Optional[Dict]
            Processed video data containing 'distances' and 'obstacles'
            
        Returns
        -------
        str
            Formatted LCR message
        """
        if audio_only:
            intensity = IntensityCalculator.audio_to_intensity(audio_only['db_level'])
            return f"L{intensity:03d}C{intensity:03d}R{intensity:03d}"
            
        if video_only:
            intensities = IntensityCalculator.vision_to_intensity_by_zone(
                video_only['distances'],
                video_only.get('obstacles', [])
            )
            return f"L{intensities['gauche']:03d}C{intensities['centre']:03d}R{intensities['droite']:03d}"
            
        return "L000C000R000"  