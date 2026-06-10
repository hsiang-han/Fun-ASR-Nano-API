FROM pytorch/pytorch:2.9.1-cuda12.8-cudnn9-devel

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git ffmpeg curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    funasr \
    fastapi \
    uvicorn[standard] \
    python-multipart \
    soundfile

COPY api/ ./api/
COPY docker/scripts/entrypoint.sh .
RUN chmod +x entrypoint.sh

ENV MODEL_ID=FunAudioLLM/Fun-ASR-Nano-2512-hf \
    DEVICE=cuda:0 \
    LANGUAGE=auto \
    PORT=8080 \
    HF_HOME=/root/.cache/huggingface \
    HF_ENDPOINT=https://huggingface.co \
    PYTHONUNBUFFERED=1

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -sf http://localhost:${PORT}/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
