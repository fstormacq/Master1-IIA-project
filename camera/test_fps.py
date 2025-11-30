#!/usr/bin/env python3
"""Test script pour tester différents FPS avec RealSense"""

import pyrealsense2 as rs # type: ignore
import time

def test_fps(fps_value, test_duration=5):
    """Test un FPS spécifique pendant une durée donnée"""
    print(f"\n🎬 Test FPS = {fps_value}")
    print("=" * 40)
    
    try:
        # Configuration identique à camera_initial.py
        pipeline = rs.pipeline()
        config = rs.config()
        
        # Tester avec les mêmes paramètres que le code qui fonctionne
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, fps_value)
        
        print(f"   Tentative de démarrage avec FPS={fps_value}...")
        
        # Essayer de démarrer le pipeline
        camera = pipeline.start(config)
        depth_scale = camera.get_device().first_depth_sensor().get_depth_scale()
        
        print(f"   ✅ Succès ! Depth scale: {depth_scale}")
        print(f"   📊 Test pendant {test_duration} secondes...")
        
        # Compter les frames reçues
        frame_count = 0
        start_time = time.time()
        max_test_time = start_time + test_duration
        
        while time.time() < max_test_time:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            if depth_frame:
                frame_count += 1
                
        elapsed_time = time.time() - start_time
        actual_fps = frame_count / elapsed_time
        
        print(f"   📈 Frames reçues: {frame_count}")
        print(f"   ⏱️  Temps écoulé: {elapsed_time:.2f}s")
        print(f"   🎯 FPS réel: {actual_fps:.1f}")
        print(f"   📊 FPS demandé: {fps_value}")
        
        # Arrêter le pipeline
        pipeline.stop()
        
        return True, actual_fps
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        print(f"   🔍 Type d'erreur: {type(e).__name__}")
        return False, 0

def main():
    """Tester différents FPS"""
    print("🧪 Test de différents FPS avec RealSense D435")
    print("=" * 50)
    
    # Liste des FPS à tester
    fps_to_test = [10, 15, 20, 25, 30, 60, 90]
    
    results = {}
    
    for fps in fps_to_test:
        success, actual_fps = test_fps(fps, test_duration=3)
        results[fps] = {'success': success, 'actual_fps': actual_fps}
        
        # Pause entre les tests
        time.sleep(1)
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    for fps, result in results.items():
        status = "✅" if result['success'] else "❌"
        if result['success']:
            print(f"   FPS {fps:2d}: {status} (réel: {result['actual_fps']:.1f})")
        else:
            print(f"   FPS {fps:2d}: {status} ÉCHEC")
    
    # Analyser les résultats
    working_fps = [fps for fps, result in results.items() if result['success']]
    failed_fps = [fps for fps, result in results.items() if not result['success']]
    
    print(f"\n🎯 FPS qui fonctionnent: {working_fps}")
    print(f"💥 FPS qui échouent: {failed_fps}")
    
    if failed_fps:
        print(f"\n💡 Conclusion: La caméra RealSense ne supporte pas les FPS: {failed_fps}")
        print("   Cela peut être dû aux limitations matérielles de la caméra.")
    else:
        print("\n🎉 Tous les FPS testés fonctionnent !")

if __name__ == "__main__":
    main()