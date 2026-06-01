from __future__ import annotations

import queue
import shutil
import signal
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk

from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from _agent.agents.intake_parser import IntakeParser
from _agent.agents.solution_architect import SolutionArchitect
from _agent.tools.audio_capture import AudioCapture
from _agent.tools.transcriber import transcribe_chunk
from modes.manual_mode import run_pipeline


console = Console()


class TranscriptBuffer:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.parts: list[str] = []

    def append(self, text: str) -> None:
        with self.lock:
            self.parts.append(text)

    def read(self) -> str:
        with self.lock:
            return "\n".join(self.parts)


def run_live_mode() -> None:
    session_type = _choose_session_type()
    original_device = None
    if session_type in {"Discovery Call", "Entrevista"}:
        original_device = _get_current_input_device()
        _switch_to_blackhole()

    chunk_queue: queue.Queue = queue.Queue()
    buffer = TranscriptBuffer()
    stop_event = threading.Event()
    capture = AudioCapture(chunk_queue)

    audio_thread = threading.Thread(target=capture.run, name="audio_thread", daemon=True)
    transcription_thread = threading.Thread(target=_transcription_worker, args=(chunk_queue, buffer, stop_event), daemon=True)
    analysis_thread = threading.Thread(target=_analysis_worker, args=(buffer, stop_event), daemon=True)

    console.print("[bold green]Live capture started. Press CTRL+C to finish.[/bold green]")
    try:
        audio_thread.start()
        transcription_thread.start()
        analysis_thread.start()
        signal.pause()
    except KeyboardInterrupt:
        console.print("[yellow]Stopping capture and draining transcription queue...[/yellow]")
    finally:
        capture.stop()
        stop_event.set()
        audio_thread.join(timeout=5)
        chunk_queue.join()
        if original_device:
            _restore_input_device(original_device)

    transcript = buffer.read()
    if transcript.strip():
        result = run_pipeline(transcript)
        console.print(Panel(f"Client proposal: {result['pdf_path']}\nEngineering spec: {result['md_path']}\nPM call review: {result['pm_review_path']}\nGitHub URL: {result['repo_url'] or 'not available'}", title="Live Mode Complete"))
    else:
        console.print("[red]No transcript was captured.[/red]")


def _transcription_worker(chunk_queue: queue.Queue, buffer: TranscriptBuffer, stop_event: threading.Event) -> None:
    while not stop_event.is_set() or not chunk_queue.empty():
        try:
            path = chunk_queue.get(timeout=1)
        except queue.Empty:
            continue
        try:
            text = transcribe_chunk(path)
            buffer.append(text)
            console.print(f"[dim]{time.strftime('%H:%M:%S')}[/dim] {text}")
        except Exception as exc:
            console.print(f"[yellow]Whisper failed for {path}: {exc}[/yellow]")
        finally:
            chunk_queue.task_done()


def _analysis_worker(buffer: TranscriptBuffer, stop_event: threading.Event) -> None:
    while not stop_event.wait(120):
        transcript = buffer.read()
        if not transcript.strip():
            continue
        intake = IntakeParser().run(transcript)
        architecture = SolutionArchitect().run(transcript, intake)
        with Live(Panel(f"{intake}\n\n{architecture['architecture_summary']}", title="Partial Insights"), refresh_per_second=1, transient=True):
            time.sleep(3)


def _choose_session_type() -> str:
    selected = {"value": "Discovery Call"}

    root = tk.Tk()
    root.title("Session Type")
    ttk.Label(root, text="Que tipo de sessão é essa?").grid(row=0, column=0, columnspan=2, padx=16, pady=12)
    options = ["Discovery Call", "Entrevista", "Reunião interna", "Outro"]
    for idx, option in enumerate(options):
        ttk.Button(root, text=option, command=lambda value=option: _select(root, selected, value)).grid(
            row=1 + idx // 2, column=idx % 2, padx=8, pady=8, sticky="ew"
        )
    root.mainloop()
    return selected["value"]


def _select(root: tk.Tk, selected: dict, value: str) -> None:
    selected["value"] = value
    root.destroy()


def _get_current_input_device() -> str | None:
    if not shutil.which("SwitchAudioSource"):
        return None
    result = subprocess.run(["SwitchAudioSource", "-t", "input", "-c"], capture_output=True, text=True)
    return result.stdout.strip() or None


def _switch_to_blackhole() -> None:
    if not shutil.which("SwitchAudioSource"):
        console.print("[yellow]switchaudio-osx not installed. Run: brew install switchaudio-osx[/yellow]")
        return
    devices = subprocess.run(["SwitchAudioSource", "-t", "input", "-a"], capture_output=True, text=True).stdout.splitlines()
    if "BlackHole 2ch" in devices:
        subprocess.run(["SwitchAudioSource", "-t", "input", "-s", "BlackHole 2ch"], check=False)
    elif "BlackHole 16ch" in devices:
        subprocess.run(["SwitchAudioSource", "-t", "input", "-u", "BlackHole16ch_UID"], check=False)
    else:
        console.print("[yellow]BlackHole input device not found. Install BlackHole or use the current microphone input.[/yellow]")


def _restore_input_device(device: str) -> None:
    if shutil.which("SwitchAudioSource"):
        subprocess.run(["SwitchAudioSource", "-t", "input", "-s", device], check=False)
