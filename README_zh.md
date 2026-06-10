# Fun-ASR-Nano-API

[English](README.md)

基于 [Fun-ASR-Nano](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512)（阿里 FunAudioLLM）的 OpenAI 兼容语音识别 API。

800M 参数。31 种语言。中文方言。热词。时间戳。一个模型搞定所有。

## 功能特性

- OpenAI 兼容的 `/v1/audio/transcriptions` 接口
- 31 种语言（中文、英文、日语、韩语、越南语、阿拉伯语等）
- 中文方言：吴语、粤语、闽语、客家话、赣语、湘语、晋语 + 26 种地方口音
- 热词支持（提升专业术语识别率）
- 通过 `MODEL_ID` 切换模型：
  - `Fun-ASR-Nano-2512-hf` — 全功能，方言，热词
  - `Fun-ASR-MLT-Nano-2512` — 31 种语言含欧洲语言

## 快速开始

```bash
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/fun-asr-nano-api/models:/root/.cache/huggingface \
  --shm-size=4g \
  --name fun-asr-nano-api \
  ghcr.io/hsiang-han/fun-asr-nano-api:latest
```

国内用户设置 `HF_ENDPOINT=https://hf-mirror.com` 加速下载。

## 使用示例

```bash
# 转写音频
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "language=中文"

# 使用热词
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "hotwords=人工智能,大语言模型"

# 自动语言检测
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav"

# 详细输出（含时间戳）
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "response_format=verbose_json"
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/v1/audio/transcriptions` | POST | 语音转文字（OpenAI 兼容） |
| `/v1/models` | GET | 列出模型 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger 文档 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| MODEL_ID | FunAudioLLM/Fun-ASR-Nano-2512-hf | 加载的模型 |
| DEVICE | cuda:0 | 计算设备 |
| LANGUAGE | auto | 默认语言（auto、中文、English、日文等） |
| PORT | 8080 | API 端口 |
| HF_ENDPOINT | https://huggingface.co | HuggingFace 镜像地址 |

## 可用模型

| 模型 ID | 语言 | 特点 |
|---------|------|------|
| FunAudioLLM/Fun-ASR-Nano-2512-hf | 中文+方言、英文、日语、韩语等 | 热词、时间戳、方言、口音 |
| FunAudioLLM/Fun-ASR-MLT-Nano-2512 | 31 种语言（含欧洲语言） | 更广的语言覆盖 |

## 硬件要求

- NVIDIA 显卡，2GB+ 显存
- 驱动版本 550+
- 安装 NVIDIA Container Toolkit 的 Docker 环境

## 致谢

- [Fun-ASR-Nano](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512) — 阿里 FunAudioLLM / 通义实验室

## 许可证

Apache-2.0
