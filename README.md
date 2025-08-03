# Plaicube Video Pipeline API

Multi-step video processing pipeline with Runway ML integration.

## 🏗️ Architecture

```
plaicube-py/
├── services/           # Service layer
│   ├── runway_service.py    # Runway ML video processing (ACTIVE)
│   ├── ffmpeg_service.py    # FFmpeg video processing (DISABLED)
│   ├── whisper_service.py   # WhisperAI transcription (DISABLED)
│   └── gpt4_service.py      # GPT-4 analysis (DISABLED)
├── middleware/         # Middleware layer
│   ├── logging_middleware.py    # Request logging
│   └── error_middleware.py      # Error handling
├── utils/             # Utilities
│   ├── validators.py      # Input validation
│   └── logger.py          # Custom logging
├── tests/             # Test suite
│   └── test_services.py   # Service tests
├── models.py          # Data models
├── pipeline_manager.py # Pipeline orchestration
├── config.py          # Configuration management
├── exceptions.py      # Custom exceptions
├── main.py           # FastAPI application
├── run.py            # Alternative entry point
└── .gitignore        # Git ignore rules
```

## Özellikler

- **Service Layer**: Her servis ayrı sınıfta, modüler yapı
- **Pipeline Yönetimi**: Çok adımlı video işleme süreçleri
- **Runway ML Gen4**: Video-to-video dönüşümü (AKTİF)
- **FFmpeg**: Video işleme ve format dönüşümü (DEVRE DIŞI)
- **WhisperAI**: Ses transkripsiyonu (DEVRE DIŞI)
- **GPT-4**: İçerik analizi (DEVRE DIŞI)
- **Task Management**: Asenkron işlem takibi
- **Progress Tracking**: Her adım için ilerleme takibi
- **Input Validation**: Kapsamlı giriş doğrulama
- **Error Handling**: Merkezi hata yönetimi
- **Logging**: Detaylı loglama sistemi
- **Testing**: Unit testler
- **Middleware**: Request/response middleware'leri

## Kurulum

1. Python 3.12.4 64-bit kullanın
2. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

3. Environment variables ayarlayın:
```bash
# .env dosyası oluşturun (env.txt'yi kopyalayın)
cp env.txt .env

# .env dosyasında API key'i güncelleyin
RUNWAY_ML_API_KEY=your_actual_runway_ml_api_key_here
```

## Çalıştırma

### Seçenek 1: main.py ile
```bash
python main.py
```

### Seçenek 2: run.py ile (önerilen)
```bash
python run.py
```

### Seçenek 3: uvicorn ile
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API http://localhost:8000 adresinde çalışacak.

## Testing

```bash
# Tüm testleri çalıştır
pytest

# Belirli test dosyasını çalıştır
pytest tests/test_services.py

# Verbose output ile
pytest -v

# Coverage ile
pytest --cov=.
```

## Service Layer

### RunwayService (AKTİF)
```python
from services.runway_service import runway_service

# Video-to-video processing
result = await runway_service.process_video(
    video_url="https://example.com/video.mp4",
    prompt="Transform to sci-fi style",
    pipeline_id="pipeline-123"
)
```

### FFmpegService (DEVRE DIŞI)
```python
from services.ffmpeg_service import ffmpeg_service

# Video processing (currently disabled)
result = await ffmpeg_service.process_video(
    input_url="https://example.com/video.mp4",
    pipeline_id="pipeline-123",
    options={"format": "mp4", "resolution": "1920x1080"}
)
```

### WhisperService (DEVRE DIŞI)
```python
from services.whisper_service import whisper_service

# Video transcription (currently disabled)
result = await whisper_service.transcribe_video(
    video_url="https://example.com/video.mp4",
    pipeline_id="pipeline-123"
)
```

### GPT4Service (DEVRE DIŞI)
```python
from services.gpt4_service import gpt4_service

# Content analysis (currently disabled)
result = await gpt4_service.analyze_content(
    content="Video transcript content...",
    pipeline_id="pipeline-123",
    analysis_type="sentiment"
)
```

## API Endpoints

### 1. Pipeline Başlat
**POST** `/api/video/transform`

**Request Body:**
```json
{
  "videoId": "uuid-string",
  "videoUrl": "https://supabase-storage-url.com/video.mp4",
  "prompt": "Transform this video to look like a sci-fi movie",
  "pipelineConfig": {
    "enableRunwayVideo": true,
    "enableFfmpeg": false,
    "enableWhisper": false,
    "enableGpt4": false,
    "customSteps": []
  }
}
```

**Not**: Şu anda sadece `enableRunwayVideo: true` aktif, diğerleri otomatik olarak `false` yapılır.

### 2. Pipeline Durumu Kontrol Et
**GET** `/api/pipeline/{pipeline_id}/status`

### 3. Tüm Pipeline'ları Listele
**GET** `/api/pipelines`

### 4. Pipeline İptal Et
**POST** `/api/pipeline/{pipeline_id}/cancel`

### 5. Pipeline Sil
**DELETE** `/api/pipeline/{pipeline_id}`

### 6. Pipeline Adımlarını Getir
**GET** `/api/pipeline/{pipeline_id}/steps`

## Pipeline Adımları

### Runway Video (AKTİF)
- **Tip**: `runway_video`
- **Servis**: `RunwayService`
- **Açıklama**: Runway ML Gen4 ile video-to-video dönüşümü
- **Giriş**: Video URL + Prompt
- **Çıkış**: Dönüştürülmüş video URL

### FFmpeg Process (DEVRE DIŞI)
- **Tip**: `ffmpeg_process`
- **Servis**: `FFmpegService`
- **Açıklama**: Video format dönüşümü ve işleme
- **Durum**: Şu anda devre dışı, placeholder olarak çalışır

### Whisper Transcribe (DEVRE DIŞI)
- **Tip**: `whisper_transcribe`
- **Servis**: `WhisperService`
- **Açıklama**: Ses transkripsiyonu
- **Durum**: Şu anda devre dışı, placeholder olarak çalışır

### GPT-4 Analysis (DEVRE DIŞI)
- **Tip**: `gpt4_analysis`
- **Servis**: `GPT4Service`
- **Açıklama**: İçerik analizi
- **Durum**: Şu anda devre dışı, placeholder olarak çalışır

## Error Handling

API aşağıdaki hata türlerini destekler:

- **ValidationException**: Giriş doğrulama hataları (400)
- **PipelineException**: Pipeline işlem hataları (500)
- **ServiceException**: Servis hataları (503)
- **PlaicubeException**: Genel uygulama hataları (500)

## Logging

Sistem aşağıdaki log seviyelerini destekler:

- **INFO**: Genel bilgiler
- **ERROR**: Hata mesajları
- **WARNING**: Uyarı mesajları
- **DEBUG**: Debug bilgileri

## NestJS Entegrasyonu

Pipeline yapısı NestJS'den gelen istekleri destekler:

```typescript
// NestJS'den pipeline başlat
const response = await this.httpService.post('/api/video/transform', {
  videoId: 'uuid',
  videoUrl: 'https://supabase-url.com/video.mp4',
  prompt: 'Transform video',
  pipelineConfig: {
    enableRunwayVideo: true,
    enableFfmpeg: false,  // Şu anda devre dışı
    enableWhisper: false, // Şu anda devre dışı
    enableGpt4: false     // Şu anda devre dışı
  }
});

// Pipeline durumunu takip et
const status = await this.httpService.get(`/api/pipeline/${response.data.pipelineId}/status`);
```

## Gelecek Özellikler

- **FFmpeg Integration**: Video processing aktif hale getirilecek
- **WhisperAI Integration**: Audio transcription aktif hale getirilecek
- **GPT-4 Integration**: Content analysis aktif hale getirilecek
- **RunPod Deployment**: GPU-powered deployment
- **Database Integration**: PostgreSQL/MongoDB
- **Redis Caching**: Performance optimization
- **WebSocket**: Real-time progress updates
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **Rate Limiting**: API rate limiting
- **Authentication**: JWT authentication
- **Monitoring**: Prometheus/Grafana
- **CI/CD**: GitHub Actions

## Notlar

- Video URL'leri Supabase Storage'dan gelen public URL'ler olmalı
- Şu anda sadece Runway ML servisi aktif
- Diğer servisler (FFmpeg, Whisper, GPT-4) devre dışı ve placeholder olarak çalışır
- Service layer sayesinde yeni servisler kolayca eklenebilir
- Her servis bağımsız olarak test edilebilir
- Pipeline yapısı NestJS'den detaylı durum takibi yapılabilir
- Production'da database kullanılmalı (şu an in-memory)
- Input validation tüm girişleri doğrular
- Error handling merkezi hata yönetimi sağlar
- Logging sistemi detaylı izleme imkanı sunar 