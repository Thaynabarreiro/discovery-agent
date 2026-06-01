from __future__ import annotations

import queue
import threading
import time
from pathlib import Path

import sounddevice as sd
import soundfile as sf


class AudioCapture:
    def __init__(self, chunk_queue: queue.Queue, sample_rate: int = 16000, chunk_seconds: int = 30) -> None:
        self.chunk_queue = chunk_queue
        self.sample_rate = sample_rate
        self.chunk_seconds = chunk_seconds
        self.stop_event = threading.Event()
        self.chunk_index = 0

    def stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        while not self.stop_event.is_set():
            frames = int(self.sample_rate * self.chunk_seconds)
            data = sd.rec(frames, samplerate=self.sample_rate, channels=1, dtype="float32")
            sd.wait()
            path = Path(f"/tmp/chunk_{self.chunk_index:03d}.wav")
            sf.write(path, data, self.sample_rate)
            self.chunk_queue.put(path)
            self.chunk_index += 1
            time.sleep(0.01)
