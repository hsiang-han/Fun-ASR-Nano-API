# Fun-ASR-Nano-API

[中文文档](README_zh.md)

OpenAI-compatible Speech-to-Text API powered by [Fun-ASR-Nano](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512) (Alibaba FunAudioLLM).

800M parameters. 31 languages. Chinese dialects. Hotwords. VAD. Punctuation. Speaker diarization. One container.

## Features

- OpenAI-compatible `/v1/audio/transcriptions` endpoint
- 31 languages (Chinese, English, Japanese, Korean, Vietnamese, Arabic, and more)
- Chinese dialects: Wu, Cantonese, Min, Hakka, Gan, Xiang, Jin + 26 regional accents
- Hotword boosting (improve recognition of domain-specific terms)
- VAD (Voice Activity Detection) — auto-segments long audio
- Automatic punctuation restoration
- Speaker diarization (who said what)
- Switchable models via `MODEL_ID`:
  - `Fun-ASR-Nano-2512` (default) — full features, dialects, hotwords
  - `Fun-ASR-MLT-Nano-2512` — 31 languages including European

## Quick Start

```bash
# Default: Fun-ASR-Nano (Chinese dialects, hotwords, full features)
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/fun-asr-nano-api/models:/root/.cache/huggingface \
  -e MODEL_ID=FunAudioLLM/Fun-ASR-Nano-2512 \
  --shm-size=4g \
  --name fun-asr-nano-api \
  ghcr.io/hsiang-han/fun-asr-nano-api:latest

# With speaker diarization enabled
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/fun-asr-nano-api/models:/root/.cache/huggingface \
  -e MODEL_ID=FunAudioLLM/Fun-ASR-Nano-2512 \
  -e ENABLE_SPK=true \
  --shm-size=4g \
  --name fun-asr-nano-api \
  ghcr.io/hsiang-han/fun-asr-nano-api:latest

# Alternative: Fun-ASR-MLT (31 languages including European)
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/fun-asr-nano-api/models:/root/.cache/huggingface \
  -e MODEL_ID=FunAudioLLM/Fun-ASR-MLT-Nano-2512 \
  --shm-size=4g \
  --name fun-asr-nano-api \
  ghcr.io/hsiang-han/fun-asr-nano-api:latest
```

China users: add `-e HF_ENDPOINT=https://hf-mirror.com`.

## Usage Examples

```bash
# Basic transcription (OpenAI-compatible)
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav"

# Specify language
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "language=中文"

# With hotwords (boost domain-specific terms)
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "hotwords=人工智能,大语言模型,通义千问"

# Verbose output (timestamps + speaker info if enabled)
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "response_format=verbose_json"
```

### Response Examples

**Standard (json):**
```json
{"text": "今天天气真好，我们出去玩吧。"}
```

**Verbose (verbose_json, with speaker diarization):**
```json
{
  "text": "今天天气真好，我们出去玩吧。",
  "language": "中文",
  "segments": [
    {"start": 0.0, "end": 2.5, "text": "今天天气真好，", "speaker": 0},
    {"start": 2.5, "end": 4.8, "text": "我们出去玩吧。", "speaker": 1}
  ]
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/audio/transcriptions` | POST | Speech-to-text (OpenAI-compatible) |
| `/v1/models` | GET | List models |
| `/health` | GET | Health check (shows enabled features) |
| `/docs` | GET | Swagger documentation |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| MODEL_ID | FunAudioLLM/Fun-ASR-Nano-2512 | Model to load |
| DEVICE | cuda:0 | Compute device (cuda:0, cpu) |
| LANGUAGE | auto | Default language (auto, 中文, English, 日文, etc.) |
| ENABLE_VAD | true | Voice Activity Detection (segments long audio) |
| ENABLE_PUNC | true | Auto punctuation restoration |
| ENABLE_SPK | false | Speaker diarization (who said what) |
| PORT | 8080 | API server port |
| HF_ENDPOINT | https://huggingface.co | HuggingFace mirror |

## Available Models

| Model ID | Languages | Features |
|----------|-----------|----------|
| FunAudioLLM/Fun-ASR-Nano-2512 | Chinese+dialects, English, Japanese, Korean, + more | Hotwords, dialects, accents, lyrics |
| FunAudioLLM/Fun-ASR-MLT-Nano-2512 | 31 languages (including European) | Broader language coverage |

## Pipeline Components

| Component | Model | Size | Enabled by |
|-----------|-------|------|-----------|
| ASR | Fun-ASR-Nano-2512 | 800M | always |
| VAD | fsmn-vad | 0.4M | ENABLE_VAD=true |
| Punctuation | ct-punc | 290M | ENABLE_PUNC=true |
| Speaker | cam++ | 7.2M | ENABLE_SPK=true |

## Hardware Requirements

- NVIDIA GPU with 2GB+ VRAM (ASR only) or 3GB+ (with all components)
- NVIDIA driver 550+
- Docker with NVIDIA Container Toolkit

## Credits

- [Fun-ASR-Nano](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512) by Alibaba FunAudioLLM / Tongyi Lab
- [FunASR](https://github.com/modelscope/FunASR) toolkit

## License

Apache-2.0
