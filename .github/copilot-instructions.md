## Purpose

This file gives focused, actionable guidance for AI coding agents working on the Whisper Flow repository so they can be productive immediately.

## Big picture (what to know first)
- Repository provides a lightweight real-time transcription service built on OpenAI Whisper models. Core responsibilities:
  - Loading Whisper models and running transcription (`whisperflow/transcriber.py`).
  - Streaming/windowing logic that batches incoming PCM chunks and emits partial/closed segments (`whisperflow/streaming.py`).
  - Web/API glue and sample server endpoints (see `whisperflow/fast_server.py` and `run.sh`).
  - Microphone I/O and chat-style loops for interactive demos (`whisperflow/audio/microphone.py`, `whisperflow/chat_room.py`).

## Key files to consult (quick map)
- `whisperflow/transcriber.py` — model loading (from `whisperflow/models/*`), sync transcribe and async wrapper (`transcribe_pcm_chunks`, `transcribe_pcm_chunks_async`). Chunks are lists of PCM16 bytes joined and decoded with numpy.frombuffer.
- `whisperflow/streaming.py` — windowing logic, `TranscribeSession` class, `transcribe` loop, and segment close heuristics. Important for real-time behavior and partial-result handling.
- `whisperflow/chat_room.py` — example of integrating listener/processor/speaker; useful for I/O and audio hardware patterns (tests skip real audio).
- `whisperflow/fast_server.py` — HTTP routes used by tests (health check and `/transcribe_pcm_chunk`). Use this for API examples and test clients.
- `tests/` — unit tests show expected behavior and sample resource usage (see `tests/test_transcriber.py`). Use tests as executable documentation.
- `whisperflow/models/` — local model files (e.g. `tiny.en.pt`) are expected; be careful modifying or replacing them.

## Project-specific patterns & constraints
- Model loading: `get_model(file_name)` caches loaded models in a module-level dict and chooses `cuda` if available. Avoid reloading models repeatedly.
- Data shape: streaming expects a list of PCM16 byte chunks. The transcriber concatenates via `b"".join(chunks)` then converts to float32 array scaled by 32768. Use the same shape when creating tests or callers.
- Async vs sync: heavy CPU/GPU transcribe runs are kept off the event loop via `asyncio.get_running_loop().run_in_executor` in `transcribe_pcm_chunks_async`. Preserve this pattern when adding async endpoints.
- Windowing/closures: `streaming.should_close_segment` uses the `cycles` heuristic to decide when a segment is final — changing it affects how many partial results appear and when final transcripts are emitted.
- Tests use `tests/utils` resources (pre-recorded PCM) and `jiwer.wer` to assert low error rates. Audio hardware tests are decorated with `pytest.mark.skip`.

## How to run, test, debug (concrete commands)
- Dev setup (macOS / zsh):
  - python -m venv .venv
  - source .venv/bin/activate
  - pip install -r requirements.txt
- Start a local server (README shows a helper):
  - ./run.sh -local
  - The server exposes endpoints used in tests (health, `/transcribe_pcm_chunk`).
- Run tests:
  - pytest -q
  - Or run a focused test: `pytest tests/test_transcriber.py::test_transcribe_chunk -q`

## Small examples agents should use (copy-paste safe)
- Load model and sync transcribe:
  - model = whisperflow.transcriber.get_model('tiny.en.pt')
  - result = whisperflow.transcriber.transcribe_pcm_chunks(model, [pcm_bytes])

- Async transcription (used by streaming/session):
  - result = await whisperflow.transcriber.transcribe_pcm_chunks_async(model, [pcm_bytes])

- WebSocket integration pattern (from README): create a `TrancribeSession` and call `session.add_chunk(byte_chunk)` for each received WebSocket binary frame.

## Notes & gotchas for agents
- Model files are large and sensitive: don't replace or re-commit model binaries. Tests and CI expect the `models/` layout.
- GPU detection: code uses `torch.cuda.is_available()`; CI or dev machines without CUDA still work, but performance differs and tests may be slower.
- Avoid changing the chunk encoding/decoding logic unless you update all callers and tests: transcriber expects signed 16-bit PCM.
- If you modify streaming heuristics, run `tests/test_transcriber.py` to confirm results and WER thresholds.

## Merge guidance
- If a pre-existing `.github/copilot-instructions.md` is present, merge key sections instead of replacing. Preserve any custom rules or project owner's notes.

If anything here is unclear or you'd like more examples (e.g., typical PR edits, or a focused walkthrough for adding a new API route), tell me what to add and I will iterate.
