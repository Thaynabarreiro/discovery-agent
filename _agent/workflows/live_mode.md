# Live Mode SOP

## Objective

Capture live call audio, transcribe it continuously, run partial background analysis, then generate the final documents when the call ends.

## Thread Architecture

### Audio Thread

- Captures audio continuously in 30-second chunks.
- Saves each chunk to `/tmp/chunk_NNN.wav`.
- Places each chunk path into a `queue.Queue`.
- Never waits for transcription before capturing the next chunk.

### Transcription Thread

- Consumes chunk paths from the queue.
- Sends each chunk to Whisper API.
- Appends transcript text to `transcript_buffer` with `threading.Lock`.
- Prints every transcribed chunk with a timestamp.

### Analysis Thread

- Every 2 minutes, reads the transcript buffer.
- Runs partial intake and architecture analysis in the background.
- Updates terminal panels with partial insights.
- Never blocks capture or transcription.

## Session Type

Before capture, show a tkinter choice window:

- Discovery Call
- Entrevista
- Reunião interna
- Outro

For Discovery Call or Entrevista:

1. Save the current macOS input device.
2. Switch input to BlackHole using `SwitchAudioSource -t input -s "BlackHole 2ch"` when available, or `SwitchAudioSource -t input -u "BlackHole16ch_UID"` for BlackHole 16ch.
3. If `switchaudio-osx` is unavailable, show `brew install switchaudio-osx`.
4. Restore the original device after `CTRL+C`.

## Shutdown

On `CTRL+C`:

1. Stop audio capture.
2. Wait until the transcription queue is empty.
3. Run the full pipeline with the complete transcript.
4. Generate both documents.
5. Restore the original audio input device.
6. Attempt GitHub upload.

## Whisper Failures

- Log the failed chunk path and error.
- Continue processing later chunks.
- Keep the original `.wav` chunk in `/tmp` for manual retry.
- Add a watch point in the final engineering spec if meaningful transcript gaps remain.
