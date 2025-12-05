from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class SensorData:
    """
    Data structure for sensor data with timestamp
    """
    timestamp: float
    data: Dict[Any, Any]
    source: str  #'audio' ou 'video'