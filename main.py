import argparse
import threading
import time
from micro.micro import start_audio_capture
from camera.camera import start_video_capture
from raspberry.raspberry import start_processing

def main(no_audio, no_video, debug, simulate):
    '''
    Main entry point for the Raspberry Pi system.
    This function starts separate threads for audio capture, video capture and processing.

    Parameters
    ----------
    no_audio : bool
        If True, audio capture is disabled.
    no_video : bool
        If True, video capture is disabled.
    debug : bool
        If True, enables debug mode with verbose logging.

    Notes
    -----
    - Each producer (video/audio) runs in its own thread and pushes data to its respective queue.
    - A separate processing thread consumes data from both queues and processes them.
    '''

    print("Starting Raspberry Pi system with separate queues...")
    
    audio_thread = None
    video_thread = None
    
    # Producer thread audio
    if not no_audio:
        print("Starting audio producer...")
        audio_thread = threading.Thread(target=start_audio_capture, args=(debug,), daemon=True)
    
    # Producer thread video  
    if not no_video:
        print("Starting video producer...")
        video_thread = threading.Thread(target=start_video_capture, args=(debug,), daemon=True)
    
    # Consumer thread (processing)
    print("Starting processing threads...")
    processing_thread = threading.Thread(target=start_processing, args=(no_audio, no_video, debug, simulate), daemon=True)
    
    print("Starting all threads...")
    
    if not no_audio:
        audio_thread.start()
        print("     Audio producer started")
    
    if not no_video:
        video_thread.start()
        print("     Video producer started")
    
    processing_thread.start()
    print("     Processing threads started")
    
    print("All systems started. Press Ctrl+C to stop.")
    
    # Inspect thread status after a short delay
    time.sleep(2)
    print(f"\nThread status:")
    print(f"   Audio: {'alive' if audio_thread and audio_thread.is_alive() else 'DISABLED' if audio_thread is None else 'DEAD'}")
    print(f"   Video: {'alive' if video_thread and video_thread.is_alive() else 'DISABLED' if video_thread is None else 'DEAD'}")
    print(f"   Processing: {'alive' if processing_thread.is_alive() else 'DEAD'}")
    
    try:
        start_time = time.time()
        while True:
            time.sleep(10)
            from queue_manager import queue_manager
            stats = queue_manager.get_queue_stats()
            uptime = time.time() - start_time
            print(f"\n{time.strftime('%H:%M:%S')} - System overview (uptime: {uptime:.1f}s):")
            print(f"   Micro: {stats['micro_total']} total, queue: {stats['micro_queue_size']}, frequency: {stats['micro_total'] / (uptime + 1e-6):.2f} items/s")
            print(f"   Video: {stats['video_total']} total, queue: {stats['video_queue_size']}, frequency: {stats['video_total'] / (uptime + 1e-6):.2f} items/s")
            print(f"   Arduino: {stats['arduino_total']} total, queue: {stats['arduino_queue_size']}, frequency: {stats['arduino_total'] / (uptime + 1e-6):.2f} items/s")
            
    except KeyboardInterrupt:
        print("\nShutting down system...")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Raspberry Pi system for audio, video, and processing.")
    parser.add_argument('--no-audio', action='store_true', help="Disable audio capture")
    parser.add_argument('--no-video', action='store_true', help="Disable video capture")

    parser.add_argument('--debug', action='store_true', help="Enable debug mode with verbose logging")
    parser.add_argument('--simulate', action='store_true', help="Simulate inputs for testing purposes")

    args = parser.parse_args()

    main(args.no_audio, args.no_video, args.debug, args.simulate)
