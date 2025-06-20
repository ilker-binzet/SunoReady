# SunoReady - Audio Processing Tool

Ses dosyalarını işlemek için geliştirilmiş Python GUI uygulaması.

## 🎯 Özellikler

- **Gelişmiş Ses İşleme**: 
  - Pitch shifting ve tempo değişimi
  - **🎛️ Tempo Stretch**: Perdeyi bozmadan hız değişimi (0.5x - 2.0x)
  - **🎚️ Fade In/Out**: Başlangıç ve bitiş geçişleri (ayarlanabilir süre)
  - **🧹 Metadata Cleaner**: Ses dosyalarından metadata temizleme
  - Ses kırpma ve normalizasyon
  - **⏱️ Süre Garantisi**: Trim ayarı kesinlikle korunur (tempo efektlerine rağmen)
- **🧠 Smart Controls**: 
  - **Otomatik süre algılama**: Dosya seçildiğinde orijinal süre otomatik tespit edilir
  - **Akıllı tempo önerisi**: Hedef süreye göre optimal tempo hesaplanır ve önerilir
  - **Süre tahmin sistemi**: Tempo değişikliği sonrası beklenen süre gösterilir
  - **Çift yönlü bağlantı**: Tempo↔Süre ayarları birbirine bağlı çalışır
  - **Hata önleme**: Kritik hatalar önceden tespit edilir ve uyarı verilir
- **YouTube İndirme**: YouTube'dan ses indirme ve arama
- **Modern GUI**: CustomTkinter kullanılarak Windows 11 tarzı karanlık tema
- **Toplu İşleme**: Birden fazla dosyayı aynı anda işleme

## 🛠️ Son Güncelleme: Duration Bug Fix

**Problem**: Tempo değişimi efektleri kullanıldığında ses süresi beklenenin dışında çıkıyordu
- Kullanıcı 90s ayarlıyor → Tempo %50 → Çıktı 180s oluyordu

**Çözüm**: Final trim sistemi eklendi
- Artık hangi efekt kullanılırsa kullanılsın, ayarlanan süre **kesinlikle** korunuyor
- 90s ayarlarsanız → Her zaman 90s çıktı alırsınız

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

1. **Gelişmiş Ses Dosyası İşleme:**
   - "Dosya Seç" butonuna tıklayın
   - İstediğiniz ses dosyalarını seçin
   - **Yeni İşleme Parametrelerini Ayarlayın:**
     - **Tempo Stretch**: Slider ile 0.5x-2.0x hız ayarlayın (perde korunur)
     - **Fade In**: Başlangıçta yumuşak giriş için işaretleyin + süre ayarlayın
     - **Fade Out**: Bitişte yumuşak çıkış için işaretleyin + süre ayarlayın
     - **Clean Metadata**: Tüm metadata'yı temizlemek için işaretleyin
   - "🎵 Process Audio Files" butonuna tıklayın

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
   - "Clean Metadata" seçeneğini işaretleyin
   - İşlemi başlatın

## 🔧 Yapılandırma

### 📁 Çıktı Klasör Yapısı

Artık işlenmiş dosyalar ve indirilen dosyalar ayrı klasörlerde saklanır:

```
output/
├── processed/     # İşlenmiş ses dosyaları
│   ├── song1_processed.mp3
│   └── song2_processed.mp3
└── downloads/     # YouTube'dan indirilen dosyalar  
    ├── video1.mp3
    └── video2.mp3
```

**Klasör Ayarları (config.json):**
- `processed_output_folder`: İşlenmiş dosyalar klasörü (varsayılan: "output/processed")
- `downloaded_output_folder`: İndirilen dosyalar klasörü (varsayılan: "output/downloads")

### ⚙️ Genel Ayarlar

`config.json` dosyasında aşağıdaki ayarları düzenleyebilirsiniz:

**Temel İşleme:**
- `pitch_shift`: Pitch kaydırma miktarı
- `tempo_change`: Tempo değişimi yüzdesi
- `trim_duration`: Kırpma süresi (saniye)
- `normalize_volume`: Ses normalleştirme
- `output_format`: Çıktı format (mp3, wav, etc.)

**Yeni Özellikler:**
- `tempo_stretch`: Tempo uzatma/sıkıştırma (0.5-2.0x)
- `fade_in`: Fade-in efekti aktif/pasif
- `fade_out`: Fade-out efekti aktif/pasif
- `fade_in_duration`: Fade-in süresi (saniye)
- `fade_out_duration`: Fade-out süresi (saniye)
- `clean_metadata`: Metadata temizleme aktif/pasif

**Diğer:**
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
