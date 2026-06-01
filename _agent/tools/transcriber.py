from __future__ import annotations

from pathlib import Path

from openai import OpenAI


def transcribe_chunk(path: str | Path, model: str = "whisper-1") -> str:
    client = OpenAI()
    with Path(path).open("rb") as audio:
        transcript = client.audio.transcriptions.create(model=model, file=audio)
    return transcript.text
