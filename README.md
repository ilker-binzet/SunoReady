# SunoReady - Audio Processing Tool

Ses dosyalarını işlemek için geliştirilmiş Python GUI uygulaması.

## 🎯 Özellikler

- **Ses İşleme**: Pitch shifting, tempo değişimi, ses kırpma, normalizasyon
- **YouTube İndirme**: YouTube'dan ses indirme ve arama
- **Metadata Temizleme**: Ses dosyalarından metadata temizleme  
- **Modern GUI**: CustomTkinter kullanılarak Windows 11 tarzı karanlık tema
- **Toplu İşleme**: Birden fazla dosyayı aynı anda işleme

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.11+
- FFmpeg (kurulu)

### Adımlar

1. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Uygulamayı başlatın:**

   **Kolay başlatma (önerilen):**
   ```bash
   launch.bat  # Gelişmiş başlatıcı (bağımlılık kontrolü ile)
   ```
   
   **Veya basit başlatma:**
   ```bash
   start.bat   # Basit başlatıcı
   ```
   
   **Veya terminal'den:**
   ```bash
   python app.py
   ```

## 🖥️ Yeni Özellikler: Sekmeli Terminal & Gelişmiş UI

### Sekmeli Terminal Konsolu
- **YouTube sekmesinde iki alt sekme**: "İndirme" ve "Terminal"
- **İndirme sekmesi**: YouTube arama ve indirme işlemleri
- **Terminal sekmesi**: yt-dlp işlemlerini canlı izleme
- **Otomatik sekme geçişi**: Önemli mesajlarda Terminal sekmesine otomatik geçiş

### Gelişmiş İndirme Arayüzü
- **📋 Panodan Yapıştır Butonu**: Kopyalanan YouTube linklerini tek tıkla yapıştırın
- **Ses Kalitesi Seçenekleri**: 64, 128, 192, 256, 320 kbps kalite seçenekleri
- **Basitleştirilmiş Arayüz**: Gereksiz arama özelliği kaldırıldı, sadece URL ile direkt indirme
- **Anlık Durum Takibi**: İndirme durumu ve ilerleme canlı gösterilir
- **Modern Buton Tasarımı**: Büyük ve belirgin indirme butonu

### Terminal Özellikleri
- **Dracula teması** ile modern ve güzel terminal görünümü  
- **Renkli log sistemi** ile farklı mesaj türlerini ayırt edin:
  - 🔵 Bilgi (Mavi)
  - 🟡 Uyarı (Sarı) 
  - 🔴 Hata (Kırmızı)
  - 🟢 Başarı (Yeşil)
  - 🟣 YouTube İşlemleri (Mor)
  - 🟣 İndirme Durumu (Mor)

## 📂 Dosya Yapısı

- `app.py` - Ana uygulama dosyası (GUI)
- `audio_utils.py` - Ses işleme fonksiyonları
- `yt_downloader.py` - YouTube indirme fonksiyonları (terminal log desteği)
- `metadata_utils.py` - Metadata temizleme fonksiyonları (terminal log desteği)
- `config.json` - Uygulama ayarları
- `requirements.txt` - Python bağımlılıkları
- `launch.bat` - Gelişmiş başlatıcı (önerilen)
- `start.bat` - Basit başlatıcı
- `output/` - İşlenen dosyaların kaydedileceği klasör

## ⚙️ Kullanım

1. **Ses Dosyası İşleme:**
   - "Dosya Seç" butonuna tıklayın
   - İstediğiniz ses dosyalarını seçin
   - İşleme parametrelerini ayarlayın
   - "İşle" butonuna tıklayın

2. **YouTube'dan İndirme:**
   - "YouTube" sekmesine geçin
   - "İndirme" alt sekmesinde:
     - YouTube URL'sini yapıştırın
     - 📋 **"Paste" butonu** ile panodaki URL'yi otomatik yapıştırın
     - **Ses kalitesi** seçin (64, 128, 192, 256, 320 kbps)
     - "⬇️ Download Audio" butonuna tıklayın
   - İşlem durumunu "Terminal" alt sekmesinde canlı izleyin

3. **Metadata Temizleme:**
   - Dosyalarınızı seçin
   - "Metadata Temizle" seçeneğini işaretleyin
   - İşlemi başlatın

## 🔧 Yapılandırma

`config.json` dosyasında aşağıdaki ayarları düzenleyebilirsiniz:

- `pitch_shift`: Pitch kaydırma miktarı
- `tempo_change`: Tempo değişimi yüzdesi
- `trim_duration`: Kırpma süresi (saniye)
- `normalize_volume`: Ses normalleştirme
- `output_format`: Çıktı format (mp3, wav, etc.)
- `youtube_quality`: YouTube indirme kalitesi

## 🎵 Desteklenen Formatlar

**Giriş:** MP3, WAV, FLAC, M4A, OGG
**Çıkış:** MP3, WAV, FLAC

## 🛠️ Sorun Giderme

- FFmpeg kurulu değilse, [buradan](https://ffmpeg.org/download.html) indirip kurun
- Python 3.11+ kullandığınızdan emin olun
- Tüm bağımlılıklar yüklü olmalı

## 📝 Lisans

Bu proje eğitim amaçlıdır.
