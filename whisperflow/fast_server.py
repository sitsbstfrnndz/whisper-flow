""" fast api declaration """

import logging
import sys
from typing import List
from fastapi import FastAPI, WebSocket, Form, File, UploadFile
from starlette.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from whisperflow import __version__
import whisperflow.streaming as st
import whisperflow.transcriber as ts
import whisperflow.notion_integration as ni

# Configure logging to print to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)


app = FastAPI()

# Add CORS middleware to allow cross-origin requests from the web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sessions = {}


@app.get("/health", response_model=str)
def health():
    """health function on API"""
    return f"Whisper Flow V{__version__}"


@app.post("/save-to-notion", response_model=dict)
def save_to_notion(
    api_key: str = Form(...),
    database_id: str = Form(...),
    transcription_text: str = Form(...),
    duration_seconds: float = Form(...),
    model: str = Form(default="small"),
):
    """Save transcription to Notion database"""
    logging.info(f"💾 Saving to Notion - {len(transcription_text)} chars")
    result = ni.save_to_notion(
        api_key=api_key,
        database_id=database_id,
        transcription_text=transcription_text,
        duration_seconds=duration_seconds,
        model=model,
    )
    if result["status"] == "success":
        logging.info(f"✅ Saved to Notion: {result['page_id']}")
    else:
        logging.error(f"❌ Notion save failed: {result['message']}")
    return result


@app.post("/transcribe_pcm_chunk", response_model=dict)
def transcribe_pcm_chunk(
    model_name: str = Form(...), files: List[UploadFile] = File(...)
):
    """transcribe chunk"""
    file_size = len(files[0].file.read())
    files[0].file.seek(0)  # Reset file pointer
    logging.info(f"📤 POST /transcribe_pcm_chunk - Model: {model_name}, File size: {file_size} bytes")
    model = ts.get_model(model_name)
    content = files[0].file.read()
    result = ts.transcribe_pcm_chunks(model, [content])
    text = result.get("text", "")[:50]
    logging.info(f"✅ Transcription result: {text}...")
    return result


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """webscoket implementation"""
    model = ts.get_model()
    logging.info("🔌 WebSocket connection accepted")

    async def transcribe_async(chunks: list):
        return await ts.transcribe_pcm_chunks_async(model, chunks)

    async def send_back_async(data: dict):
        text = data.get("text", "")[:50]
        logging.info(f"📤 Sending transcription: {text}...")
        await websocket.send_json(data)

    try:
        await websocket.accept()
        session = st.TranscribeSession(transcribe_async, send_back_async)
        sessions[session.id] = session
        logging.info(f"✅ Session started: {session.id}")

        chunk_count = 0
        while True:
            data = await websocket.receive_bytes()
            chunk_count += 1
            logging.info(f"📥 Received audio chunk #{chunk_count} ({len(data)} bytes)")
            session.add_chunk(data)
    except WebSocketDisconnect:
        logging.info(f"✅ WebSocket disconnected (session: {session.id})")
        await session.stop()
    except Exception as exception:  # pylint: disable=broad-except
        logging.error(f"❌ WebSocket error: {exception}")
        await session.stop()
