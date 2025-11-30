import threading
import time
from micro.micro import start_audio_capture
from camera.camera import start_video_capture
from raspberry.raspberry import start_processing

def main():
    '''
    Main entry point for the Raspberry Pi system.
    This function starts separate threads for audio capture, video capture and processing.

    Notes
    -----
    - Each producer (video/audio) runs in its own thread and pushes data to its respective queue.
    - A separate processing thread consumes data from both queues and processes them.
    '''

    print("Starting Raspberry Pi system with separate queues...")
    
    # Thread producteur audio
    print("Starting audio producer...")
    audio_thread = threading.Thread(target=start_audio_capture, daemon=True)
    
    # Thread producteur vidéo  
    print("Starting video producer...")
    video_thread = threading.Thread(target=start_video_capture, daemon=True)
    
    # Thread consommateur (traitement)
    print("Starting processing threads...")
    processing_thread = threading.Thread(target=start_processing, daemon=True)
    
    print("Starting all threads...")
    
    audio_thread.start()
    print("     Audio producer started")
    
    video_thread.start()
    print("     Video producer started")
    
    processing_thread.start()
    print("     Processing threads started")
    
    print("All systems started. Press Ctrl+C to stop.")
    
    # Debug initial
    time.sleep(2)
    print(f"\nThread status:")
    print(f"   Audio: {'alive' if audio_thread.is_alive() else 'DEAD'}")
    print(f"   Video: {'alive' if video_thread.is_alive() else 'DEAD'}")
    print(f"   Processing: {'alive' if processing_thread.is_alive() else 'DEAD'}")
    
    try:
        while True:
            time.sleep(10)
            from queue_manager import queue_manager
            stats = queue_manager.get_queue_stats()
            print(f"\n{time.strftime('%H:%M:%S')} - System overview:")
            print(f"   Micro: {stats['micro_total']} total, queue: {stats['micro_queue_size']}")
            print(f"   Video: {stats['video_total']} total, queue: {stats['video_queue_size']}")
            print(f"   Arduino: {stats['arduino_total']} total, queue: {stats['arduino_queue_size']}")
            
    except KeyboardInterrupt:
        print("\nShutting down system...")

if __name__ == "__main__":
    main()
