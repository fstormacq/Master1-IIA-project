import threading
import time
from micro.micro import start_audio_capture
from raspberry.raspberry import start_processing

def main():
    print("Starting Raspberry Pi system...")
    
    # Start Producer audio thread
    audio_thread = threading.Thread(target=start_audio_capture, daemon=True)
    audio_thread_2 = threading.Thread(target=start_audio_capture, daemon=True)
    # Start Producer video thread (if any)
    # video_thread = threading.Thread(target=start_video_capture, daemon=True)
    
    # Start Consumer processing thread
    processing_thread = threading.Thread(target=start_processing, daemon=True)
    
    audio_thread.start()
    audio_thread_2.start()
    processing_thread.start()
    
    print("All systems started. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down system...")

if __name__ == "__main__":
    main()
