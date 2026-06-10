import io
import os
import tempfile
import threading
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

MODEL_ID = os.getenv("MODEL_ID", "FunAudioLLM/Fun-ASR-Nano-2512")
DEVICE = os.getenv("DEVICE", "cuda:0")
LANGUAGE = os.getenv("LANGUAGE", "auto")
ENABLE_VAD = os.getenv("ENABLE_VAD", "true").lower() == "true"
ENABLE_PUNC = os.getenv("ENABLE_PUNC", "true").lower() == "true"
ENABLE_SPK = os.getenv("ENABLE_SPK", "false").lower() == "true"

_model = None
_model_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model
    from funasr import AutoModel

    kwargs = {
        "model": MODEL_ID,
        "hub": "hf",
        "trust_remote_code": True,
        "device": DEVICE,
        "disable_update": True,
    }

    if ENABLE_VAD:
        kwargs["vad_model"] = "funasr/fsmn-vad"
        kwargs["vad_kwargs"] = {"max_single_segment_time": 30000}

    if ENABLE_PUNC:
        kwargs["punc_model"] = "funasr/ct-punc"

    if ENABLE_SPK:
        kwargs["spk_model"] = "funasr/cam++"

    _model = AutoModel(**kwargs)
    yield
    _model = None


app = FastAPI(title="Fun-ASR-Nano-API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "status": "ok" if _model else "loading",
        "model": MODEL_ID,
        "device": DEVICE,
        "vad": ENABLE_VAD,
        "punc": ENABLE_PUNC,
        "spk": ENABLE_SPK,
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
    """OpenAI-compatible audio transcription endpoint.

    Extra parameters beyond OpenAI spec:
    - hotwords: comma-separated list of domain-specific terms to boost recognition
    """
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
            "itn": True,
        }
        if lang:
            kwargs["language"] = lang
        if hotwords:
            kwargs["hotwords"] = [h.strip() for h in hotwords.split(",")]

        with _model_lock:
            results = _model.generate(**kwargs)

        if not results:
            raise HTTPException(status_code=500, detail="No transcription result")

        result = results[0]
        text = result.get("text", "")

        # OpenAI verbose_json format
        if response_format == "verbose_json":
            response = {
                "text": text,
                "language": lang or "auto",
            }
            # Timestamps if available
            timestamps = result.get("timestamp", [])
            if timestamps:
                response["segments"] = _format_timestamps(timestamps)
            # Speaker info if available
            sentence_info = result.get("sentence_info", [])
            if sentence_info:
                response["segments"] = _format_speaker_segments(sentence_info)
            return JSONResponse(content=response)

        # OpenAI standard json format
        return JSONResponse(content={"text": text})

    finally:
        os.unlink(tmp_path)


def _get_suffix(filename: Optional[str]) -> str:
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[-1]
    return ".wav"


def _format_timestamps(timestamps: list) -> list:
    """Format funasr timestamps to OpenAI-like segments."""
    segments = []
    for ts in timestamps:
        if isinstance(ts, (list, tuple)) and len(ts) >= 2:
            segments.append({
                "start": ts[0] / 1000.0 if ts[0] > 100 else ts[0],
                "end": ts[1] / 1000.0 if ts[1] > 100 else ts[1],
                "text": ts[2] if len(ts) > 2 else "",
            })
    return segments


def _format_speaker_segments(sentence_info: list) -> list:
    """Format funasr speaker diarization to segments."""
    segments = []
    for info in sentence_info:
        if isinstance(info, dict):
            segments.append({
                "start": info.get("start", 0) / 1000.0,
                "end": info.get("end", 0) / 1000.0,
                "text": info.get("text", ""),
                "speaker": info.get("spk", None),
            })
        elif isinstance(info, (list, tuple)) and len(info) >= 3:
            segments.append({
                "start": info[0] / 1000.0 if info[0] > 100 else info[0],
                "end": info[1] / 1000.0 if info[1] > 100 else info[1],
                "text": info[2] if len(info) > 2 else "",
                "speaker": info[3] if len(info) > 3 else None,
            })
    return segments
