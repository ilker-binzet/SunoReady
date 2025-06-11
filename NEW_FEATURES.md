# 🎵 SunoReady - Yeni Özellikler

## 🎛️ 1. Tempo Stretch (Perde Korunarak Hız Değişimi)

### Özellik Açıklaması:
- **Range**: 0.5x - 2.0x hız değişimi
- **Teknoloji**: FFmpeg'in `atempo` filtresini kullanır
- **Önemli**: Ses perdesini bozmadan sadece hızı değiştirir
- **Otomatik Çoklu Filtre**: 2.0x'den fazla veya 0.5x'den az değerler için otomatik olarak birden fazla atempo filtresi uygulanır

### GUI Kullanımı:
1. **Audio Processing** sekmesine gidin
2. **"Tempo Stretch"** slider'ını görün
3. **0.5x - 2.0x** arası değer seçin
4. Anlık değer **label'da** görünür (örn: "1.5x")
5. Dosyalarınızı seçip işlem başlatın

### Teknik Detaylar:
- `ffmpeg -i input.wav -filter:a "atempo=1.5" output.wav`
- Extreme değerler için: `atempo=2.0,atempo=1.25` (2.5x için)

---

## 🎚️ 2. Fade In / Fade Out

### Özellik Açıklaması:
- **Fade In**: Ses başında yumuşak giriş efekti
- **Fade Out**: Ses sonunda yumuşak çıkış efekti
- **Ayarlanabilir Süre**: Her biri için ayrı süre ayarı (varsayılan: 3 saniye)
- **Otomatik Hesaplama**: Fade Out, dosyanın toplam süresine göre otomatik hesaplanır

### GUI Kullanımı:
1. **"Fade In"** checkbox'ını işaretleyin
2. Süresi için **yanındaki kutuya** saniye girin (örn: 3.0)
3. **"Fade Out"** checkbox'ını işaretleyin
4. Süresini ayarlayın
5. ✅ **Checkbox açıkken** süre kutusunun **aktif** olduğuna dikkat edin

### Teknik Detaylar:
- **Fade In**: `afade=t=in:st=0:d=3`
- **Fade Out**: `afade=t=out:st=87:d=3` (90 sn'lik dosya için)
- Hem birlikte hem de ayrı ayrı kullanılabilir

---

## 🧹 3. Metadata Cleaner

### Özellik Açıklaması:
- **Mutagen Kütüphanesi**: Python'un mutagen library'si kullanılır
- **Tüm Metadata**: ID3 tags, album, artist, cover art vb. tümü temizlenir
- **Alternatif FFmpeg**: Gerekirse `ffmpeg -map_metadata -1` komutu da kullanılabilir
- **Batch Compatible**: Toplu işlemde tüm dosyalara uygulanır

### GUI Kullanımı:
1. **"Clean Metadata"** checkbox'ını işaretleyin
2. Dosyalarınızı seçin
3. İşlem başlatın
4. Çıktı dosyalarında metadata temizlenmiş olacak

### Teknik Detaylar:
```python
# Mutagen ile
audio.delete()  # Tüm tagları sil
audio.save()    # Kaydet

# FFmpeg alternatifi
ffmpeg -i input.mp3 -map_metadata -1 -c copy output.mp3
```

---

## 🛠️ Entegrasyon ve Yapılandırma

### Config.json Yeni Anahtarlar:
```json
{
  "tempo_stretch": 1.0,        // Tempo stretch multiplier
  "fade_in": false,            // Fade in aktif/pasif
  "fade_out": false,           // Fade out aktif/pasif  
  "fade_in_duration": 3.0,     // Fade in süresi (saniye)
  "fade_out_duration": 3.0,    // Fade out süresi (saniye)
  "clean_metadata": false      // Metadata temizleme
}
```

### Batch Processing:
- ✅ **Tüm özellikler** toplu işleme destekler
- ✅ **Aynı ayarlar** seçilen tüm dosyalara uygulanır
- ✅ **Hata toleransı** - bir dosya hata verirse diğerleri devam eder

### Error Handling:
- **Tempo Stretch**: Geçersiz değerler için uyarı
- **Fade Duration**: Negatif veya çok büyük değerler kontrol edilir
- **FFmpeg Errors**: FFmpeg hatalarında alternatif yöntemler denenir

---

## 🧪 Test Senaryoları

### Test 1: Tempo Stretch
1. `test_tone_new.wav` dosyasını seçin
2. Tempo Stretch: **1.5x** ayarlayın
3. Diğer seçenekleri kapatın
4. İşleyin ve çıktıyı dinleyin - %50 daha hızlı ama aynı perde

### Test 2: Fade Effects
1. Herhangi bir müzik dosyası seçin
2. **Fade In**: ✅ - 2 saniye
3. **Fade Out**: ✅ - 4 saniye
4. İşleyin - başında 2sn, sonunda 4sn yumuşak geçiş

### Test 3: Metadata Cleaning
1. Metadata'sı olan bir MP3 seçin
2. **Clean Metadata**: ✅
3. İşleyin - çıktı dosyasında metadata kalmamış olmalı

### Test 4: Kombine
1. Tüm yeni özellikleri birlikte aktif edin
2. **Tempo**: 0.8x (yavaş)
3. **Fade In/Out**: 3'er saniye
4. **Clean Metadata**: ✅
5. İşleyin - tüm efektler uygulanmış olmalı

---

## 📊 Performans ve Limitler

### Desteklenen Formatlar:
- **Input**: MP3, WAV, FLAC, M4A, OGG
- **Output**: MP3, WAV, FLAC (config'e göre)

### Performans:
- **Tempo Stretch**: CPU yoğun işlem
- **Fade Effects**: Çok hızlı
- **Metadata Clean**: Anında

### Limitler:
- **Tempo Range**: 0.5x - 2.0x (daha extreme değerler için multiple filter)
- **Fade Duration**: Max dosya süresinin %50'si önerilir
- **File Size**: Memory kullanımı dosya boyutuna bağlı

---

## 🐛 Debugging ve Log

### Terminal Log Mesajları:
```
🎵 Processing with tempo stretch: 1.5x
🎚️ Applying fade in (3.0s) and fade out (3.0s)
🧹 Cleaning metadata from output file
✅ Successfully processed: example.mp3
```

### Hata Mesajları:
```
❌ Tempo stretch failed, falling back to librosa
⚠️  Fade duration too long, adjusting to max
🚫 Metadata cleaning failed, skipping
```

### Debug İpuçları:
- Config dosyasında değerler korunuyor mu?
- FFmpeg PATH'de mevcut mu?
- Dosya yazma izinleri var mı?
- Input file corrupt değil mi?

Bu özellikler SunoReady'yi çok daha güçlü bir audio processing aracı haline getiriyor! 🎵✨
