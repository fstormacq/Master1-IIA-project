from collections import deque
from typing import Optional, Dict, Any
from raspberry.sensor_data import SensorData
import time

class SyncBuffer:
    """
    Temporal synchronization buffer for audio and video data
    """
    
    def __init__(self, max_age_ms=150):
        self.audio_buffer = deque(maxlen=5)
        self.video_buffer = deque(maxlen=5)
        self.max_age = max_age_ms / 1000.0
        
    def add_audio(self, audio_result):
        """
        Add audio data with timestamp
        
        Parameters
        ----------
        audio_result : Dict
            Processed audio data
        """
        sensor_data = SensorData(
            timestamp=time.time(),
            data=audio_result,
            source='audio'
        )
        self.audio_buffer.append(sensor_data)
        
    def add_video(self, video_result):
        """
        Add video data with timestamp
        
        Parameters
        ----------
        video_result : Dict
            Processed video data
        """
        sensor_data = SensorData(
            timestamp=time.time(),
            data=video_result,
            source='video'
        )
        self.video_buffer.append(sensor_data)
        
    def cleanup_old_data(self, current_time):
        """
        Clean up data older than max_age
        
        Parameters
        ----------
        current_time : float
            Current timestamp
        """
        while self.audio_buffer and (current_time - self.audio_buffer[0].timestamp) > self.max_age:
            self.audio_buffer.popleft()
            
        while self.video_buffer and (current_time - self.video_buffer[0].timestamp) > self.max_age:
            self.video_buffer.popleft()
        
    def get_synchronized_pair(self):
        """
        Find the best synchronized audio-video pair
        
        Returns
        -------
        Optional[Tuple[SensorData, SensorData]]
            The best synchronized audio and video data pair, or None if not found
        """
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
                    
        #Acceptable synchronization threshold (50ms)
        if best_pair and min_time_diff < 0.05:
            return best_pair
            
        return None
    
    def get_latest_audio(self):
        """
        Retrieve the most recent audio data
        
        Returns
        -------
        Optional[SensorData]
            The most recent audio data, or None if buffer is empty
        """
        return self.audio_buffer[-1] if self.audio_buffer else None
    
    def get_latest_video(self):
        """
        Retrieve the most recent video data
        
        Returns
        -------
        Optional[SensorData]
            The most recent video data, or None if buffer is empty
        """
        return self.video_buffer[-1] if self.video_buffer else None