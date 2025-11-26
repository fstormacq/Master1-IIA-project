import threading
import time
from micro.micro import start_audio_capture
from raspberry.raspberry import start_processing

def main():
    print("Starting Raspberry Pi system...")
    
    # Start Producer audio thread
    audio_thread = threading.Thread(target=start_audio_capture, daemon=True)
    
    # Start Producer video thread (if any)
    # video_thread = threading.Thread(target=start_video_capture, daemon=True)
    
    # Start Consumer processing thread
    processing_thread = threading.Thread(target=start_processing, daemon=True)
    
    audio_thread.start()
    processing_thread.start()
    
    print("All systems started. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down system...")

        if join_with_result(audio_thread, timeout=1):
            print("Audio thread stopped.")
        if join_with_result(processing_thread, timeout=1):
            print("Processing thread stopped.")


def join_with_result(thread, timeout=None):
    """Join and return True if thread terminated, False if timeout occurred."""
    thread.join(timeout)
    return not thread.is_alive()

if __name__ == "__main__":
    main()
