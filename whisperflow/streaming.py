""" test scenario module """

import time
import uuid
import asyncio
from queue import Queue
from typing import Callable


def get_all(queue: Queue) -> list:
    """get_all from queue"""
    res = []
    while queue and not queue.empty():
        res.append(queue.get())
    return res


async def transcribe(
    should_stop: list,
    queue: Queue,
    transcriber: Callable[[list], str],
    segment_closed: Callable[[dict], None],
    buffer_duration_seconds: float = 5.0,
):
    """the transcription loop"""
    window = []
    buffer_start_time = time.time()
    bytes_per_second = 32000  # 16000 Hz * 2 bytes per sample

    while not should_stop[0]:
        await asyncio.sleep(0.01)
        window.extend(get_all(queue))

        if not window:
            continue

        # Calculate buffered duration in seconds
        buffered_bytes = sum(len(chunk) for chunk in window)
        buffered_duration = buffered_bytes / bytes_per_second
        elapsed_time = time.time() - buffer_start_time

        # Process when buffer duration reached
        if buffered_duration >= buffer_duration_seconds:
            start = time.time()
            result = {
                "is_partial": False,
                "data": await transcriber(window),
                "time": (time.time() - start) * 1000,
            }

            if result["data"]["text"]:
                await segment_closed(result)

            # Reset for next segment
            window = []
            buffer_start_time = time.time()
        else:
            # Send partial results for user feedback
            start = time.time()
            result = {
                "is_partial": True,
                "data": await transcriber(window),
                "time": (time.time() - start) * 1000,
            }

            if result["data"]["text"]:
                await segment_closed(result)


def should_close_segment(result: dict, prev_result: dict, cycles, buffered_duration=0, buffer_duration_seconds=10.0, max_cycles=1):
    """return if segment should be closed"""
    # Close if buffer duration has been reached (with 0.5s tolerance for processing)
    if buffered_duration >= (buffer_duration_seconds - 0.5):
        return True
    # Or close if result is stable (same result for max_cycles)
    return cycles >= max_cycles and result["data"]["text"] == prev_result.get(
        "data", {}
    ).get("text", "")


class TranscribeSession:  # pylint: disable=too-few-public-methods
    """transcription state"""

    def __init__(self, transcribe_async, send_back_async) -> None:
        """ctor"""
        self.id = uuid.uuid4()  # pylint: disable=invalid-name
        self.queue = Queue()
        self.should_stop = [False]
        self.task = asyncio.create_task(
            transcribe(self.should_stop, self.queue, transcribe_async, send_back_async)
        )

    def add_chunk(self, chunk: bytes):
        """add new chunk"""
        self.queue.put_nowait(chunk)

    async def stop(self):
        """stop session"""
        self.should_stop[0] = True
        await self.task
