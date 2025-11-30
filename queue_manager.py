from queue import Queue, Full, Empty
from typing import Any
import time

class QueueManager:
    """
    QueueManager handle separate queues for audio (microphone) data,
    video (camera) data, and commands to be sent to the Arduino.
    """
    
    def __init__(self):
        # Separate queue for microphone audio data
        self.micro_queue = Queue(maxsize=10)
        
        # Separate queue for camera video data
        self.video_queue = Queue(maxsize=10)
        
        # Separate queue for processed data to be sent to the Arduino
        self.arduino_queue = Queue(maxsize=5)
        
        # Monitoring
        self.dropped_micro_count = 0
        self.dropped_video_count = 0
        self.dropped_arduino_count = 0
        self.total_micro_count = 0
        self.total_video_count = 0
        self.total_arduino_count = 0
        
    def put_micro_data(self, data: Any):
        '''
        Add audio data to the microphone queue

        Parameters
        ----------
        data : Any
            The audio data chunk to be added to the queue
        '''
        self.total_micro_count += 1
        
        try:
            self.micro_queue.put_nowait((data, time.time()))
        except Full:
            self.dropped_micro_count += 1
            print(f"MICRO Queue full! Dropped: {self.dropped_micro_count}/{self.total_micro_count}")
            
            # Drop oldest data
            for i in range(min(3, self.micro_queue.qsize())):
                try:
                    self.micro_queue.get_nowait()
                except Empty:
                    break
            
            try:
                self.micro_queue.put_nowait((data, time.time()))
            except Full:
                print("Micro queue still full!")
    
    def get_micro_data(self, timeout=1.0):
        '''
        Get the next audio data chunk from the microphone queue

        Parameters
        ----------
        timeout : float, optional
            Time to wait for data before raising Empty exception, by default 1.0 seconds

        Returns
        -------
        Any
            The next audio data chunk from the queue
        '''
        result = self.micro_queue.get(timeout=timeout)
        return result[0] if isinstance(result, tuple) else result
    
    def put_video_data(self, data: Any):
        '''
        Add video data to the video queue

        Parameters
        ----------
        data : Any
            The video data chunk to be added to the queue
        '''
        self.total_video_count += 1
        
        try:
            self.video_queue.put_nowait((data, time.time()))
        except Full:
            self.dropped_video_count += 1
            print(f"VIDEO Queue full! Dropped: {self.dropped_video_count}/{self.total_video_count}")
            
            # Drop oldest data
            for i in range(min(3, self.video_queue.qsize())):
                try:
                    self.video_queue.get_nowait()
                except Empty:
                    break
            
            try:
                self.video_queue.put_nowait((data, time.time()))
            except Full:
                print("Video queue still full!")
    
    def get_video_data(self, timeout=1.0):
        '''
        Get the next video data chunk from the video queue

        Parameters
        ----------
        timeout : float, optional
            Time to wait for data before raising Empty exception, by default 1.0 seconds

        Returns
        -------
        Any
            The next video data chunk from the queue
        '''
        result = self.video_queue.get(timeout=timeout)
        return result[0] if isinstance(result, tuple) else result
    
    def put_arduino_data(self, command: Any):
        '''
        Add commands for the Arduino

        Parameters
        ----------
        command : Any
            The command to be added to the Arduino queue
        '''
        self.total_arduino_count += 1
        
        try:
            self.arduino_queue.put_nowait((command, time.time()))
        except Full:
            self.dropped_arduino_count += 1
            print(f"ARDUINO Queue full! Dropped: {self.dropped_arduino_count}/{self.total_arduino_count}")
            
            for i in range(min(2, self.arduino_queue.qsize())):
                try:
                    self.arduino_queue.get_nowait()
                except Empty:
                    break
            
            try:
                self.arduino_queue.put_nowait((command, time.time()))
            except Full:
                print("Arduino queue still full!")
    
    def get_arduino_data(self, timeout=1.0):
        '''
        Get the next command for the Arduino

        Parameters
        ----------
        timeout : float, optional
            Time to wait for data before raising Empty exception, by default 1.0 seconds

        Returns
        -------
        Any
            The next command from the Arduino queue
        '''
        result = self.arduino_queue.get(timeout=timeout)
        return result[0] if isinstance(result, tuple) else result
    
    def get_queue_stats(self):
        '''
        Get current statistics of the queues

        Returns
        -------
        dict
            A dictionary containing queue sizes, dropped counts, total counts, and drop rates
        '''
        return {
            'micro_queue_size': self.micro_queue.qsize(),
            'video_queue_size': self.video_queue.qsize(),
            'arduino_queue_size': self.arduino_queue.qsize(),
            'micro_dropped': self.dropped_micro_count,
            'video_dropped': self.dropped_video_count,
            'arduino_dropped': self.dropped_arduino_count,
            'micro_total': self.total_micro_count,
            'video_total': self.total_video_count,
            'arduino_total': self.total_arduino_count,
            'micro_drop_rate': self.dropped_micro_count / max(1, self.total_micro_count) * 100,
            'video_drop_rate': self.dropped_video_count / max(1, self.total_video_count) * 100,
            'arduino_drop_rate': self.dropped_arduino_count / max(1, self.total_arduino_count) * 100
        }
    
    def print_stats(self):
        '''
        Print current queue statistics

        Note
        ----
        This function is mainly for debugging purposes.
        '''
        stats = self.get_queue_stats()
        print(f"\n📊 Queue Stats:")
        print(f"  Micro: {stats['micro_queue_size']}/10 items, {stats['micro_drop_rate']:.1f}% dropped")
        print(f"  Video: {stats['video_queue_size']}/10 items, {stats['video_drop_rate']:.1f}% dropped")
        print(f"  Arduino: {stats['arduino_queue_size']}/5 items, {stats['arduino_drop_rate']:.1f}% dropped")

# Shared global instance
queue_manager = QueueManager()