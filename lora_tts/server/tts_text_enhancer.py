import re


def _normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", "", text)
    text = text.replace(";", "，").replace("；", "，")
    text = text.replace(":", "，").replace("：", "，")
    return text


def _insert_pauses(text: str) -> str:
    if not text:
        return text

    # If there is no punctuation and sentence is long, insert pauses every ~12 chars.
    if not re.search(r"[，。！？,.!?]", text) and len(text) > 16:
        parts = []
        i = 0
        while i < len(text):
            parts.append(text[i : i + 12])
            i += 12
        text = "，".join(parts)

    # Ensure sentence has final punctuation for more stable cadence.
    if text[-1] not in "。！？!?":
        text = text + "。"
    return text


def _shape_by_emotion(text: str, emotion: str, intensity: float) -> str:
    intensity = max(0.6, min(1.4, float(intensity)))

    if emotion == "excited":
        # Excited style prefers shorter chunks and stronger punctuation.
        text = re.sub(r"，", "！", text) if intensity >= 1.15 else text
        if len(text) > 18 and "，" not in text and "！" not in text:
            text = "，".join([text[i : i + 8] for i in range(0, len(text), 8)])
    elif emotion == "serious":
        # Serious style uses steadier cadence with fewer exclamations.
        text = text.replace("！", "。")
    elif emotion == "inquisitive":
        # Inquisitive style ends with a question mark for clearer intent.
        if text and text[-1] in "。！":
            text = text[:-1] + "？"
        elif text and text[-1] not in "？?":
            text = text + "？"

    return text


def build_tts_text(
    text: str,
    emotion: str = "soothing",
    style: str = "empathetic",
    speed: str = "slow",
    enhance_prosody: bool = True,
    use_style_tags: bool = True,
    emotion_intensity: float = 1.0,
) -> str:
    raw = _normalize_text(text)
    if enhance_prosody:
        raw = _insert_pauses(raw)
        raw = _shape_by_emotion(raw, emotion=emotion, intensity=emotion_intensity)

    if not use_style_tags:
        return raw

    if raw.startswith("[Emotion:"):
        return raw

    return f"[Emotion: {emotion}][Style: {style}][Speed: {speed}]\\n{raw}"
