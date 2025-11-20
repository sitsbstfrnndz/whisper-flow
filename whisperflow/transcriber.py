""" transcriber """

import os
import asyncio

import torch
import numpy as np

import whisper
from whisper import Whisper


models = {}


def get_model(file_name="small") -> Whisper:
    """load models from disk"""
    if file_name not in models:
        # Check if file_name is a model name (e.g., "base", "tiny.en") or a path
        if os.path.exists(os.path.join(os.path.dirname(__file__), f"./models/{file_name}")):
            path = os.path.join(os.path.dirname(__file__), f"./models/{file_name}")
            models[file_name] = whisper.load_model(path).to(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        else:
            # Assume it's a model name and let whisper download/load it
            models[file_name] = whisper.load_model(file_name).to(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
    return models[file_name]


def transcribe_pcm_chunks(
    model: Whisper, chunks: list, lang="en", temperature=0.1, log_prob=-0.5
) -> dict:
    """transcribes pcm chunks list"""
    arr = (
        np.frombuffer(b"".join(chunks), np.int16).flatten().astype(np.float32) / 32768.0
    )
    return model.transcribe(
        arr,
        fp16=False,
        language=lang,
        logprob_threshold=log_prob,
        temperature=temperature,
    )


async def transcribe_pcm_chunks_async(
    model: Whisper, chunks: list, lang="en", temperature=0.1, log_prob=-0.5
) -> dict:
    """transcribes pcm chunks async"""
    return await asyncio.get_running_loop().run_in_executor(
        None, transcribe_pcm_chunks, model, chunks, lang, temperature, log_prob
    )
