# Simple Whisper Flow Dashboard

A clean, minimalist real-time transcription dashboard for Whisper Flow.

## Features

- **Real-time Transcription**: Stream audio from your microphone and see transcriptions appear instantly
- **Visual Status Indicators**: Clear connection and recording status with animated indicators
- **Partial & Final Results**: Distinguish between partial (in-progress) and final transcriptions
- **Live Statistics**: Track word count, segments, average latency, and recording duration
- **Clean UI**: Modern, gradient-based design with smooth animations
- **Auto-scroll**: Automatically scrolls to show the latest transcription

## How to Use

### 1. Start the Whisper Flow Server

First, make sure the Whisper Flow server is running:

```bash
cd /path/to/whisper-flow
./run.sh -local
source .venv/bin/activate
python -m whisperflow.fast_server
```

The server should start on port 8181.

### 2. Open the Dashboard

Open `simple_dashboard.html` in your web browser:

```bash
# Option 1: Direct file open
open simple_dashboard.html  # macOS
xdg-open simple_dashboard.html  # Linux
start simple_dashboard.html  # Windows

# Option 2: Or just drag and drop the file into your browser
```

### 3. Start Recording

1. Click the **"Start Recording"** button
2. Allow microphone access when prompted by your browser
3. Start speaking - you'll see transcriptions appear in real-time
4. Click **"Stop Recording"** when done
5. Use **"Clear"** to reset the transcription history

## Technical Details

### WebSocket Connection

The dashboard connects to the Whisper Flow WebSocket endpoint at `ws://localhost:8181/ws`

### Audio Format

- Sample Rate: 16000 Hz
- Channels: Mono (1 channel)
- Format: PCM 16-bit signed integer
- Chunk Size: 1024 samples

### Transcription Display

- **Yellow (Partial)**: Transcription is still being processed and may change
- **Green (Final)**: Transcription is complete and finalized

### Statistics Tracked

- **Words**: Total number of words transcribed
- **Segments**: Number of complete transcription segments
- **Avg Latency**: Average time between transcription updates
- **Duration**: Total recording time

## Browser Compatibility

This dashboard works best in modern browsers with WebRTC support:

- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Edge
- ✅ Safari (macOS/iOS)

## Troubleshooting

### "Error: Failed to connect"

Make sure the Whisper Flow server is running on port 8181:

```bash
# Check if server is running
curl http://localhost:8181/health
```

### "Microphone access denied"

Check your browser's microphone permissions and allow access for this page.

### "No transcription appearing"

1. Check that your microphone is working
2. Verify the server logs for any errors
3. Try speaking louder or closer to the microphone

## Comparison with Original UI

This simple dashboard focuses on:

- **Minimalism**: Clean, distraction-free interface
- **Real-time feedback**: Immediate visual feedback for all actions
- **Statistics**: Built-in metrics tracking
- **Ease of use**: Single-file HTML with no external dependencies

The original `index.html` offers more features like file upload, Notion integration, and advanced settings. Use this simple dashboard when you just need quick, real-time transcription.

## Customization

The dashboard is a single HTML file with embedded CSS and JavaScript. You can easily customize:

- **Colors**: Edit the gradient in the `body` style
- **Layout**: Modify the CSS grid and flexbox properties
- **WebSocket URL**: Change the `wsUrl` in the JavaScript
- **Audio settings**: Adjust `sampleRate`, `channelCount`, etc.

## License

Same as the parent Whisper Flow project.
