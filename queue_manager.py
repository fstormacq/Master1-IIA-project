from queue import Queue
from typing import Any
from enum import IntEnum

class DataType(IntEnum):
    """Index to identify data types in the queue"""
    MICRO_DATA = 0
    CAMERA_DATA = 1
    # Add other types as needed

class QueueManager:
    """Centralized manager for shared queues"""
    
    def __init__(self):
        # Main queue for raw sensor data
        self.sensor_queue = Queue(maxsize=50)
        
        # Queue for processed data to send to Arduino
        self.arduino_queue = Queue(maxsize=30)
        
    def put_sensor_data(self, data_type: int, data: Any):
        """Add sensor data with its type"""
        try:
            self.sensor_queue.put_nowait((data_type, data))
        except:
            # Drop half of the oldest data if queue is full
            print("Queue full, dropping oldest sensor data")
            for i in range(5):
                self.sensor_queue.get_nowait()
            self.sensor_queue.put_nowait((data_type, data))
    
    def get_sensor_data(self, timeout=1.0):
        """Retrieve sensor data"""
        return self.sensor_queue.get(timeout=timeout)
    
    def put_arduino_data(self, command: Any):
        """Add commands for Arduino"""
        try:
            self.arduino_queue.put_nowait(command)
        except:
            # Drop half of the oldest commands if queue is full
            for i in range(5):
                self.arduino_queue.get_nowait()
            self.arduino_queue.put_nowait(command)
    
    def get_arduino_data(self, timeout=1.0):
        """Retrieve commands for Arduino"""
        return self.arduino_queue.get(timeout=timeout)

# Global shared instance
queue_manager = QueueManager()