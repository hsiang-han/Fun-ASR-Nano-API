import io
import os
import tempfile
import threading
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

MODEL_ID = os.getenv("MODEL_ID", "FunAudioLLM/Fun-ASR-Nano-2512-hf")
DEVICE = os.getenv("DEVICE", "cuda:0")
LANGUAGE = os.getenv("LANGUAGE", "auto")

_model = None
_model_lock = threading.Lock()

# Model choices
AVAILABLE_MODELS = {
    "fun-asr-nano": "FunAudioLLM/Fun-ASR-Nano-2512-hf",
    "fun-asr-mlt": "FunAudioLLM/Fun-ASR-MLT-Nano-2512",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model
    from funasr import AutoModel

    _model = AutoModel(
        model=MODEL_ID,
        hub="hf",
        trust_remote_code=True,
        device=DEVICE,
    )
    yield
    _model = None


app = FastAPI(title="Fun-ASR-Nano-API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "status": "ok" if _model else "loading",
        "model": MODEL_ID,
        "device": DEVICE,
    }


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_ID,
                "object": "model",
                "owned_by": "FunAudioLLM",
            }
        ],
    }


@app.post("/v1/audio/transcriptions")
async def transcribe(
    file: UploadFile = File(...),
    model: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default=None),
    response_format: Optional[str] = Form(default="json"),
    hotwords: Optional[str] = Form(default=None),
):
    """OpenAI-compatible audio transcription endpoint."""
    if not _model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    audio_bytes = await file.read()

    with tempfile.NamedTemporaryFile(suffix=_get_suffix(file.filename), delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        lang = language if language and language != "auto" else LANGUAGE
        if lang == "auto":
            lang = None

        kwargs = {
            "input": [tmp_path],
            "cache": {},
            "batch_size": 1,
        }
        if lang:
            kwargs["language"] = lang
        if hotwords:
            kwargs["hotwords"] = hotwords.split(",")
        kwargs["itn"] = True

        with _model_lock:
            results = _model.generate(**kwargs)

        if not results:
            raise HTTPException(status_code=500, detail="No transcription result")

        result = results[0]
        text = result.get("text", "")

        if response_format == "verbose_json":
            return JSONResponse(content={
                "text": text,
                "language": lang or "auto",
                "segments": _extract_segments(result),
            })

        return JSONResponse(content={"text": text})

    finally:
        os.unlink(tmp_path)


def _get_suffix(filename: Optional[str]) -> str:
    if filename:
        if "." in filename:
            return "." + filename.rsplit(".", 1)[-1]
    return ".wav"


def _extract_segments(result: dict) -> list:
    """Extract timestamp segments if available."""
    timestamps = result.get("timestamp", [])
    text = result.get("text", "")
    if not timestamps:
        return [{"start": 0, "end": 0, "text": text}]
    segments = []
    for ts in timestamps:
        if isinstance(ts, (list, tuple)) and len(ts) >= 3:
            segments.append({
                "start": ts[0] / 1000.0,
                "end": ts[1] / 1000.0,
                "text": ts[2] if len(ts) > 2 else "",
            })
    return segments if segments else [{"start": 0, "end": 0, "text": text}]
