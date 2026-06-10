# Fun-ASR-Nano-API

[English](README.md)

基于 [Fun-ASR-Nano](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512)（阿里 FunAudioLLM）的 OpenAI 兼容语音识别 API。

800M 参数。31 种语言。中文方言。热词。VAD。标点。说话人分离。一个容器搞定。

## 功能特性

- OpenAI 兼容的 `/v1/audio/transcriptions` 接口
- 31 种语言（中文、英文、日语、韩语、越南语、阿拉伯语等）
- 中文方言：吴语、粤语、闽语、客家话、赣语、湘语、晋语 + 26 种地方口音
- 热词增强（提升专业术语识别率）
- VAD 语音活动检测（自动分段长音频）
- 自动标点恢复
- 说话人分离（谁说了什么）
- 通过 `MODEL_ID` 切换模型：
  - `Fun-ASR-Nano-2512`（默认）— 全功能，方言，热词
  - `Fun-ASR-MLT-Nano-2512` — 31 种语言含欧洲语言

## 快速开始

```bash
# 默认：Fun-ASR-Nano（中文方言、热词、全功能）
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/fun-asr-nano-api/models:/root/.cache/huggingface \
  -e MODEL_ID=FunAudioLLM/Fun-ASR-Nano-2512 \
  --shm-size=4g \
  --name fun-asr-nano-api \
  ghcr.io/hsiang-han/fun-asr-nano-api:latest

# 启用说话人分离
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/fun-asr-nano-api/models:/root/.cache/huggingface \
  -e MODEL_ID=FunAudioLLM/Fun-ASR-Nano-2512 \
  -e ENABLE_SPK=true \
  --shm-size=4g \
  --name fun-asr-nano-api \
  ghcr.io/hsiang-han/fun-asr-nano-api:latest

# 备选：Fun-ASR-MLT（31 种语言含欧洲语言）
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/fun-asr-nano-api/models:/root/.cache/huggingface \
  -e MODEL_ID=FunAudioLLM/Fun-ASR-MLT-Nano-2512 \
  --shm-size=4g \
  --name fun-asr-nano-api \
  ghcr.io/hsiang-han/fun-asr-nano-api:latest
```

国内用户加 `-e HF_ENDPOINT=https://hf-mirror.com` 加速下载。

## 使用示例

```bash
# 基础转写（OpenAI 兼容）
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav"

# 指定语言
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "language=中文"

# 使用热词（提升专业术语识别）
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "hotwords=人工智能,大语言模型,通义千问"

# 详细输出（时间戳 + 说话人信息）
curl -X POST http://localhost:8080/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "response_format=verbose_json"
```

### 响应示例

**标准格式 (json)：**
```json
{"text": "今天天气真好，我们出去玩吧。"}
```

**详细格式 (verbose_json，启用说话人分离)：**
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

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/v1/audio/transcriptions` | POST | 语音转文字（OpenAI 兼容） |
| `/v1/models` | GET | 列出模型 |
| `/health` | GET | 健康检查（显示启用的功能） |
| `/docs` | GET | Swagger 文档 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| MODEL_ID | FunAudioLLM/Fun-ASR-Nano-2512 | 加载的模型 |
| DEVICE | cuda:0 | 计算设备 |
| LANGUAGE | auto | 默认语言（auto、中文、English、日文等） |
| ENABLE_VAD | true | VAD 语音活动检测（长音频自动分段） |
| ENABLE_PUNC | true | 自动标点恢复 |
| ENABLE_SPK | false | 说话人分离（谁说了什么） |
| PORT | 8080 | API 端口 |
| HF_ENDPOINT | https://huggingface.co | HuggingFace 镜像地址 |

## 可用模型

| 模型 ID | 语言 | 特点 |
|---------|------|------|
| FunAudioLLM/Fun-ASR-Nano-2512 | 中文+方言、英文、日语、韩语等 | 热词、方言、口音、歌词识别 |
| FunAudioLLM/Fun-ASR-MLT-Nano-2512 | 31 种语言（含欧洲语言） | 更广的语言覆盖 |

## Pipeline 组件

| 组件 | 模型 | 大小 | 启用方式 |
|------|------|------|---------|
| ASR | Fun-ASR-Nano-2512 | 800M | 始终启用 |
| VAD | fsmn-vad | 0.4M | ENABLE_VAD=true |
| 标点 | ct-punc | 290M | ENABLE_PUNC=true |
| 说话人 | cam++ | 7.2M | ENABLE_SPK=true |

## 硬件要求

- NVIDIA 显卡，2GB+ 显存（仅 ASR）或 3GB+（全组件）
- 驱动版本 550+
- 安装 NVIDIA Container Toolkit 的 Docker 环境

## 致谢

- [Fun-ASR-Nano](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512) — 阿里 FunAudioLLM / 通义实验室
- [FunASR](https://github.com/modelscope/FunASR) 语音识别工具包

## 许可证

Apache-2.0
