import os
import tempfile
import threading
import uuid
from pathlib import Path
from typing import Optional

import soundfile as sf
import torch
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from peft import PeftModel
from qwen_tts import Qwen3TTSModel

from tts_text_enhancer import build_tts_text


BASE_MODEL = os.getenv("BASE_MODEL", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
ADAPTER_PATH = os.getenv(
    "ADAPTER_PATH",
    "/root/autodl-tmp/qwen3_tts_lora/output_lora_mixed_clean_e1/checkpoint-epoch-0/adapter",
)
REF_AUDIO_DEFAULT = os.getenv(
    "REF_AUDIO_DEFAULT",
    "/root/autodl-tmp/dataset/Emotion Speech Dataset/0006/Neutral/0006_000001.wav",
)
ATTN_IMPL = os.getenv("ATTN_IMPL", "sdpa")
API_KEY = os.getenv("API_KEY", "")
TMP_DIR = Path(os.getenv("TTS_TMP_DIR", "/tmp/qwen3_tts_api"))
TMP_DIR.mkdir(parents=True, exist_ok=True)


class TTSRequest(BaseModel):
    text: str
    ref_audio: Optional[str] = None
    language: str = "Auto"
    x_vector_only_mode: bool = True
    do_sample: bool = True
    top_p: float = 0.95
    temperature: float = 0.82
    emotion: str = "soothing"
    style: str = "empathetic"
    speed: str = "slow"
    emotion_intensity: float = 1.0
    enhance_prosody: bool = True
    use_style_tags: bool = True
    adapter_path: Optional[str] = None


app = FastAPI(title="Qwen3-TTS LoRA API", version="1.0.0")
_lock = threading.Lock()
_tts = None
_base_talker = None
_active_adapter = None


def _load_model() -> Qwen3TTSModel:
    global _tts, _base_talker, _active_adapter
    if _tts is not None:
        return _tts

    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    device_map = "cuda:0" if torch.cuda.is_available() else "cpu"

    tts = Qwen3TTSModel.from_pretrained(
        BASE_MODEL,
        device_map=device_map,
        dtype=dtype,
        attn_implementation=ATTN_IMPL,
    )
    _base_talker = tts.model.talker
    tts.model.talker = PeftModel.from_pretrained(_base_talker, ADAPTER_PATH)
    _active_adapter = ADAPTER_PATH
    _tts = tts
    return _tts


def _apply_adapter_if_needed(model: Qwen3TTSModel, adapter_path: str) -> None:
    global _base_talker, _active_adapter
    if adapter_path == _active_adapter:
        return
    if not Path(adapter_path).exists():
        raise HTTPException(status_code=400, detail=f"adapter_path not found: {adapter_path}")
    model.model.talker = PeftModel.from_pretrained(_base_talker, adapter_path)
    _active_adapter = adapter_path


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "base_model": BASE_MODEL,
        "default_adapter_path": ADAPTER_PATH,
        "active_adapter_path": _active_adapter or ADAPTER_PATH,
        "cuda": torch.cuda.is_available(),
    }


@app.post("/v1/tts")
def tts(req: TTSRequest, x_api_key: Optional[str] = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text cannot be empty")

    ref_audio = req.ref_audio or REF_AUDIO_DEFAULT
    if not Path(ref_audio).exists():
        raise HTTPException(status_code=400, detail=f"ref_audio not found: {ref_audio}")

    final_text = build_tts_text(
        text=text,
        emotion=req.emotion,
        style=req.style,
        speed=req.speed,
        emotion_intensity=req.emotion_intensity,
        enhance_prosody=req.enhance_prosody,
        use_style_tags=req.use_style_tags,
    )

    with _lock:
        model = _load_model()
        req_adapter = req.adapter_path.strip() if req.adapter_path else ""
        _apply_adapter_if_needed(model, req_adapter or ADAPTER_PATH)
        wavs, sr = model.generate_voice_clone(
            text=final_text,
            language=req.language,
            ref_audio=ref_audio,
            x_vector_only_mode=req.x_vector_only_mode,
            do_sample=req.do_sample,
            top_p=req.top_p,
            temperature=req.temperature,
        )

    out_path = TMP_DIR / f"tts_{uuid.uuid4().hex}.wav"
    sf.write(str(out_path), wavs[0], sr)
    return FileResponse(
        path=str(out_path),
        media_type="audio/wav",
        filename=out_path.name,
    )
