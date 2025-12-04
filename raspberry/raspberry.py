"""
Main module for Raspberry Pi specific functionality.

The raspberry pi will act as a central hub for various sensors and sensorial outputs.

It will consume data from connected sensors and process it accordingly.
"""

import threading, time, numpy as np
#import serial
from raspberry.fake_serial import FakeSerial
from queue import Empty
from queue_manager import queue_manager
from raspberry.sensor_data import SensorData
from raspberry.intensity_calculator import IntensityCalculator
from raspberry.lcr_message_generator import LCRMessageGenerator
from raspberry.sync_buffer import SyncBuffer

def heavy_audio_processing(chunk, debug=False):
    '''
    Heavy processing for audio data.

    Parameters
    ----------
    chunk : np.ndarray
        The audio data chunk to be processed
    debug : bool
        If True, enables debug mode with verbose logging.

    Returns
    -------
    dict
        The processing results including RMS, dB level, classification, dominant frequency, and timestamp
    '''

    rms = np.sqrt(np.mean(chunk**2))
    
    #Computing dB level
    ref = 1.0      #Reference for dBFS (normalized float audio)
    eps = 1e-12    #Avoid log10(0)
    level = max(rms / ref, eps)
    niveau_db = 20.0 * np.log10(level)
    
    if not np.isfinite(niveau_db):
        niveau_db = -np.inf
    
    #Sound level classification
    if niveau_db < -45:
        sound_label = "Chillax"
    elif niveau_db < -30:
        sound_label = "Some noise"
    elif niveau_db < -15:
        sound_label = "Be Careful"
    else:
        sound_label = "Danger"
    
    #Main frequency detection
    fft_result = np.fft.fft(chunk)
    dominant_freq = np.argmax(np.abs(fft_result[:len(fft_result)//2]))
    if debug:
        print(f"Audio Processing - RMS: {rms:.5f}, dB: {niveau_db:.2f}, Class: {sound_label}, Freq: {dominant_freq} Hz")
    
    return {
        'rms': rms,
        'db_level': niveau_db,
        'sound_classification': sound_label,
        'dominant_frequency': dominant_freq,
        'timestamp': time.time()
    }

def heavy_video_processing(video_data, debug=False):
    """
    Heavy processing for video data.

    Parameters
    ----------
    video_data : dict
        The video data to be processed
    debug : bool
        If True, enables debug mode with verbose logging.

    Returns
    -------
    dict
        The processing results including mode, obstacle info, avoid direction, danger level, risk classification,
        distances, obstacles count, frame number, and timestamp

    Notes
    -----
    The video data needs to arrive pre-processed with obstacle detection and distance estimation.
    """
    
    mode = video_data['mode']
    obstacles = video_data['obstacles']
    distances = video_data['distances_smooth']
    
    #Severity level determination
    danger_level = 0
    if 'Centre' in obstacles:
        danger_level = 3  #Critique
    elif len(obstacles) > 1:
        danger_level = 2  #High
    elif len(obstacles) == 1:
        danger_level = 1  #Warning
    
    #Risk classification
    risk_classification = "safe"
    if danger_level == 3:
        risk_classification = "critical"
    elif danger_level == 2:
        risk_classification = "high"
    elif danger_level == 1:
        risk_classification = "medium"
    
    #Need to minimize the data sent to Arduino
    return {
        'mode': mode,
        'obstacle_info': video_data['obstacle_info'],
        'avoid_direction': video_data['avoid_direction'],
        'danger_level': danger_level,
        'risk_classification': risk_classification,
        'distances': distances,
        'obstacles_count': len(obstacles),
        'frame_number': video_data['frame_number'],
        'timestamp': video_data['timestamp']
    }

def micro_processing_thread(debug=False):
    """
    Processing thread dedicated to microphone audio data

    Parameters
    ----------
    debug : bool
        If True, enables debug mode with verbose logging.

    Notes
    -----
    This thread continuously fetches audio data from the queue, processes it, and sends commands to the Arduino based on the results.
    """
    processing_count = 0
    
    while True:
        try:
            chunk = queue_manager.get_micro_data()
            processing_count += 1
            
            result = heavy_audio_processing(chunk, debug)
            """
            # Commande Arduino pour l'audio
            arduino_command = {
                'type': 'audio_alert',
                'db_level': result['db_level'],
                'classification': result['sound_classification'],
                'rms': result['rms'],
                'frequency': result['dominant_frequency']
            }
            queue_manager.put_arduino_data(arduino_command)"""
            
            queue_manager.put_audio_processed_data(result)
            
            if debug:
                print(f"Audio #{processing_count}: {result['db_level']:.1f}dB - {result['sound_classification']}")
                
        except Empty:
            continue
        except Exception as e:
            print(f"Micro processing error: {e}")

def video_processing_thread(debug=False):
    """
    Processing thread dedicated to video data

    Parameters
    ----------
    debug : bool
        If True, enables debug mode with verbose logging.

    Notes
    -----
    This thread continuously fetches video data from the queue, processes it, and sends commands to the Arduino based on the results.
    """
    processing_count = 0
    
    while True:
        try:
            video_data = queue_manager.get_video_data(timeout=1.0)
            processing_count += 1
            
            result = heavy_video_processing(video_data, debug)

            """arduino_command = {
                'type': 'vision_alert',
                'mode': result['mode'],
                'danger_level': result['danger_level'],
                'risk_classification': result['risk_classification'],
                'obstacle_info': result['obstacle_info'],
                'avoid_direction': result['avoid_direction'],
                'distances': result['distances']
            }
            
            queue_manager.put_arduino_data(arduino_command)"""
            
            queue_manager.put_video_processed_data(result)
            
            if debug:
                distances = result['distances']
                print(f"📹 Video #{processing_count}: {result['mode']} | Obstacles: {result['obstacle_info']} | "
                        f"G={distances['gauche']:.2f}m C={distances['centre']:.2f}m D={distances['droite']:.2f}m")
                
        except Empty:
            continue
        except Exception as e:
            print(f"Video processing error: {e}")

"""def arduino_communication_thread(debug=False):
    
    Processing thread dedicated to Arduino communication

    Parameters
    ----------
    debug : bool
        If True, enables debug mode with verbose logging.

    Notes
    -----
    This thread continuously fetches commands from the queue and sends them to the Arduino.
    
    while True:
        try:
            command = queue_manager.get_arduino_data(timeout=1.0)
            # print(f"Sending to Arduino: {command}")
            # Here: real serial communication
            
        except Empty:
            continue
        except Exception as e:
            print(f"Arduino communication error: {e}")"""
            
def arduino_communication_thread(debug=False, simulate=True):
    """
    Centralized thread for Arduino synchronization and communication
    
    Parameters
    ----------
    debug : bool
        If True, enables debug mode with verbose logging.
        
    Notes
    -----   
    1. Collects processed audio/video data
    2. Synchronizes them in time
    3. Generates LCR messages
    4. Sends them to the Arduino
    """
    if simulate:
        serial_port = FakeSerial(log_file="lcr_log.txt", plot=True)
    """else:
        # --- Open Arduino serial port ---
        try:
            serial_port = serial.Serial(
                port='/dev/ttyACM0',   #Adjust as necessary
                baudrate=115200,
                timeout=0.05
            )
            print("🔌 Serial port opened successfully")
        except Exception as e:
            print(f"[ERROR] Failed to open serial port: {e}")
            serial_port = None"""
    sync_buffer = SyncBuffer(max_age_ms=150)
    message_generator = LCRMessageGenerator()
    last_send_time = 0
    send_interval = 1.0 / 25.0  #Max 25Hz sending rate
    
    print("🤖 Arduino communication thread started with synchronization")
    
    while True:
        try:
            current_time = time.time()
            
            #Collect new audio data
            try:
                audio_result = queue_manager.get_audio_processed_data(timeout=0.01)
                sync_buffer.add_audio(audio_result)
            except Empty:
                pass
            
            #Collect new video data
            try:
                video_result = queue_manager.get_video_processed_data(timeout=0.01)
                sync_buffer.add_video(video_result)
            except Empty:
                pass
            
            #Limit Arduino send frequency (max 25Hz)
            if (current_time - last_send_time) < send_interval:
                time.sleep(0.001) 
                continue
                
            #Attempt to get synchronized data
            sync_pair = sync_buffer.get_synchronized_pair()
            
            if sync_pair:
                audio_data, video_data = sync_pair
                message = message_generator.generate_synchronized_message(
                    audio_data.data, video_data.data
                )
                
                sync_quality = 'synced'
                if debug:
                    time_diff = abs(audio_data.timestamp - video_data.timestamp)
                    print(f"🔄 SYNC {message} (Δt={time_diff*1000:.1f}ms)")
                    
            else:
                #Fallback to latest available data
                latest_audio_sensor = sync_buffer.get_latest_audio()
                latest_video_sensor = sync_buffer.get_latest_video()
                
                latest_audio = latest_audio_sensor.data if latest_audio_sensor else None
                latest_video = latest_video_sensor.data if latest_video_sensor else None
                
                message = message_generator.generate_fallback_message(
                    audio_only=latest_audio,
                    video_only=latest_video
                )
                
                sync_quality = 'fallback'
                if debug and (latest_audio or latest_video):
                    source = "audio" if latest_audio and not latest_video else \
                            "video" if latest_video and not latest_audio else "both_unsync"
                    print(f"[WARNING] FALLBACK {message} (source: {source})")
            
            """
            arduino_command = {
                'type': 'LCR_command',
                'message': message,
                'timestamp': current_time,
                'sync_quality': sync_quality
            }"""
            
            if serial_port:
                serial_port.write((message + "\n").encode())
            
            if debug:
                print(f"➡️  Arduino: {message}")
            
            last_send_time = current_time
            
        except Exception as e:
            print(f"Arduino communication error: {e}")
            time.sleep(0.01)

def start_processing(no_audio=False, no_video=False, debug=False):
    """
    Function to start all processing threads

    Parameters
    ----------
    no_audio : bool
        If True, audio processing is disabled.
    no_video : bool
        If True, video processing is disabled.
    debug : bool
        If True, enables debug mode with verbose logging.
    """
    print("Starting processing threads...")
    
    #Initialize thread variables
    micro_thread = None
    video_thread = None
    
    if not no_audio:
        micro_thread = threading.Thread(target=micro_processing_thread, args=(debug,), daemon=True)
    
    if not no_video:
        video_thread = threading.Thread(target=video_processing_thread, args=(debug,), daemon=True)
    
    arduino_thread = threading.Thread(target=arduino_communication_thread, args=(debug,), daemon=True)
    
    if not no_audio and micro_thread:
        micro_thread.start()
        print("Micro processing thread started")
    
    if not no_video and video_thread:
        video_thread.start()
        print("Video processing thread started")
    
    arduino_thread.start()
    print("Arduino communication thread started")
    
    try:
        while True:
            time.sleep(5)
            queue_manager.print_stats()
    except Exception as e:
        print(f"Processing error: {e}")

if __name__ == "__main__":
    start_processing()