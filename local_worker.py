from __future__ import annotations

import queue
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from _agent.tools.audio_capture import AudioCapture
from _agent.tools.transcriber import transcribe_chunk
from modes.manual_mode import run_pipeline


load_dotenv(".env")
os.environ["ENABLE_CREWAI"] = os.getenv("LOCAL_WORKER_ENABLE_CREWAI", "false")

app = FastAPI(title="Discovery Agent Local Worker")
sessions: dict[str, "LiveSession"] = {}


class StartCallRequest(BaseModel):
    client_name: str | None = None
    session_type: str = "Discovery Call"
    mode: str = "live"
    transcript: str | None = None
    push_to_github: bool = False


class StopCallRequest(BaseModel):
    session_id: str
    push_to_github: bool = False


class LiveSession:
    def __init__(self, session_id: str, metadata: dict[str, Any]) -> None:
        self.session_id = session_id
        self.metadata = metadata
        self.chunk_queue: queue.Queue = queue.Queue()
        self.lock = threading.Lock()
        self.transcript_parts: list[str] = []
        self.stop_event = threading.Event()
        self.capture = AudioCapture(self.chunk_queue)
        self.audio_thread = threading.Thread(target=self.capture.run, daemon=True)
        self.transcription_thread = threading.Thread(target=self._transcribe_loop, daemon=True)
        self.started_at = time.time()

    def start(self) -> None:
        self.audio_thread.start()
        self.transcription_thread.start()

    def stop_and_generate(self, push_to_github: bool = False) -> dict:
        self.capture.stop()
        self.stop_event.set()
        self.audio_thread.join(timeout=10)
        self.chunk_queue.join()
        transcript = self.transcript
        result = run_pipeline(transcript, push_to_github=push_to_github)
        return _serialize_result(result, transcript)

    @property
    def transcript(self) -> str:
        with self.lock:
            return "\n".join(self.transcript_parts)

    def _transcribe_loop(self) -> None:
        while not self.stop_event.is_set() or not self.chunk_queue.empty():
            try:
                path = self.chunk_queue.get(timeout=1)
            except queue.Empty:
                continue
            try:
                text = transcribe_chunk(path)
                with self.lock:
                    self.transcript_parts.append(text)
            finally:
                self.chunk_queue.task_done()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "active_sessions": list(sessions.keys())}


@app.post("/start-call")
def start_call(raw_payload: dict) -> dict:
    request = StartCallRequest.model_validate(raw_payload.get("body", raw_payload))
    if request.mode == "manual":
        if not request.transcript:
            raise HTTPException(status_code=400, detail="Manual mode requires transcript.")
        result = run_pipeline(request.transcript, push_to_github=request.push_to_github)
        return _serialize_result(result, request.transcript)

    session_id = str(uuid.uuid4())
    session = LiveSession(session_id, request.model_dump())
    sessions[session_id] = session
    session.start()
    return {
        "status": "recording",
        "session_id": session_id,
        "message": "Live call capture started on the local Mac.",
    }


@app.post("/stop-call")
def stop_call(raw_payload: dict) -> dict:
    request = StopCallRequest.model_validate(raw_payload.get("body", raw_payload))
    session = sessions.pop(request.session_id, None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session.stop_and_generate(push_to_github=request.push_to_github)


@app.get("/status/{session_id}")
def session_status(session_id: str) -> dict:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "session_id": session_id,
        "seconds_elapsed": int(time.time() - session.started_at),
        "transcript_chars": len(session.transcript),
    }


def _serialize_result(result: dict, transcript: str) -> dict:
    transcript_path = Path("output") / "latest_transcript.txt"
    transcript_path.parent.mkdir(exist_ok=True)
    transcript_path.write_text(transcript, encoding="utf-8")
    return {
        "status": "complete",
        "transcript_path": str(transcript_path),
        "client_proposal": str(result["pdf_path"]),
        "engineering_spec": str(result["md_path"]),
        "pm_call_review": str(result["pm_review_path"]),
        "github_url": result.get("repo_url"),
    }
