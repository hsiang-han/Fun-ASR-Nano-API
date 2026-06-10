# Fun-ASR-Nano-API

[中文文档](README_zh.md)

OpenAI-compatible Speech-to-Text API powered by [Fun-ASR-Nano](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512) (Alibaba FunAudioLLM).

800M parameters. 31 languages. Chinese dialects. Hotwords. Timestamps. One model does it all.

## Features

- OpenAI-compatible `/v1/audio/transcriptions` endpoint
- 31 languages (Chinese, English, Japanese, Korean, Vietnamese, Arabic, and more)
- Chinese dialects: Wu, Cantonese, Min, Hakka, Gan, Xiang, Jin + 26 regional accents
- Hotword support (improve recognition of domain-specific terms)
- Switchable models via `MODEL_ID`:
  - `Fun-ASR-Nano-2512-hf` — full features, dialects, hotwords
  - `Fun-ASR-MLT-Nano-2512` — 31 languages including European languages

## Quick Start

```bash
# Default: Fun-ASR-Nano (Chinese dialects, hotwords, full features)
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/fun-asr-nano-api/models:/root/.cache/huggingface \
  -e MODEL_ID=FunAudioLLM/Fun-ASR-Nano-2512-hf \
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

China users: set `-e HF_ENDPOINT=https://hf-mirror.com`.

## Usage Examples

```bash
# Transcribe audio file
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "language=中文"

# With hotwords
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "hotwords=人工智能,大语言模型"

# Auto language detection
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav"

# Verbose output (with timestamps)
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "response_format=verbose_json"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/audio/transcriptions` | POST | Speech-to-text (OpenAI-compatible) |
| `/v1/models` | GET | List models |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger documentation |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| MODEL_ID | FunAudioLLM/Fun-ASR-Nano-2512-hf | Model to load (see Available Models) |
| DEVICE | cuda:0 | Compute device (cuda:0, cpu) |
| LANGUAGE | auto | Default language (auto, 中文, English, 日文, etc.) |
| PORT | 8080 | API server port |
| HF_ENDPOINT | https://huggingface.co | HuggingFace mirror |

## Available Models

| Model ID | Languages | Features |
|----------|-----------|----------|
| FunAudioLLM/Fun-ASR-Nano-2512-hf | Chinese+dialects, English, Japanese, Korean, + more | Hotwords, timestamps, dialects, accents |
| FunAudioLLM/Fun-ASR-MLT-Nano-2512 | 31 languages (including European) | Broader language coverage |

## Hardware Requirements

- NVIDIA GPU with 2GB+ VRAM
- NVIDIA driver 550+
- Docker with NVIDIA Container Toolkit

## Credits

- [Fun-ASR-Nano](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512) by Alibaba FunAudioLLM / Tongyi Lab

## License

Apache-2.0
