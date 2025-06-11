#!/usr/bin/env python3
"""
SunoReady - Basit Hız Testi
Gerçek kullanım senaryosunu test eder
"""

import os
import time
import subprocess
import sys

def simple_speed_test():
    """Ultra basit hız testi - sadece FFmpeg"""
    print("🚀 SunoReady - Basit Hız Testi")
    print("=" * 40)
    
    # Test dosyası bul
    test_files = [
        "simple_test.wav",
        "test_audio.wav"
    ]
    
    # Output klasöründeki dosyaları da kontrol et
    if os.path.exists("output"):
        for file in os.listdir("output"):
            if file.endswith(('.mp3', '.wav')):
                test_files.append(f"output/{file}")
    
    test_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("❌ Test dosyası bulunamadı!")
        return
        
    print(f"📁 Test dosyası: {test_file}")
    
    # Sadece tempo değişimi - en basit işlem
    output_file = "hiz_test_output.mp3"
    
    # Ultra basit FFmpeg komutu
    cmd = [
        "ffmpeg", "-y", "-i", test_file,
        "-filter:a", "atempo=1.05",  # %105 tempo 
        "-c:a", "libmp3lame", "-b:a", "320k",
        output_file
    ]
    
    print(f"\n🏃‍♂️ Komut: ffmpeg ... atempo=1.05")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ BAŞARILI! İşlem süresi: {processing_time:.2f} saniye")
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"📊 Çıktı dosya boyutu: {file_size/1024/1024:.2f} MB")
                os.remove(output_file)  # Temizle
            
            # Hız değerlendirmesi
            if processing_time < 2:
                print("🏆 MÜKEMMEL - Çok hızlı!")
            elif processing_time < 5:
                print("👍 İYİ - Kabul edilebilir hız")
            elif processing_time < 10:
                print("⚠️ ORTA - Biraz yavaş")
            else:
                print("❌ YAVAŞ - Optimizasyon gerekli!")
                
        else:
            print(f"❌ HATA: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ ZAMAN AŞIMI - İşlem çok uzun sürdü!")
    except Exception as e:
        print(f"❌ HATA: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 SONUÇ:")
    if processing_time < 3:
        print("   ✅ Uygulama yeterince hızlı")
    else:
        print("   ⚠️ Optimizasyon önerileri:")
        print("   - Sadece gerekli efektleri kullan")
        print("   - FFmpeg'i doğrudan kullan")
        print("   - Librosa gibi yavaş kütüphanelerden kaçın")

if __name__ == "__main__":
    simple_speed_test()
