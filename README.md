# Video Subtitle Generator

A Python tool that automatically generates and embeds word-level subtitles into videos using OpenAI's Whisper model for speech recognition.

## Features

- Extracts audio from video files
- Generates word-level transcription using Whisper
- Creates SRT subtitle files
- Embeds subtitles directly into videos
- Supports multiple video formats
- Handles timestamps with millisecond precision

## Prerequisites

```bash
pip install openai-whisper ffmpeg-python
```

You'll also need FFmpeg installed on your system:

- **Linux**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)

## Usage

1. Place your video file in the project directory
2. Run the script:

```bash
python main.py
```

By default, the script processes a file named `test.mp4` and generates:
- `output.mp3` (extracted audio)
- `output.srt` (subtitle file)
- `output_with_subs.mp4` (video with embedded subtitles)

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
