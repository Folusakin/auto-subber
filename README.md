# Auto-Subber
Automatic subtitle generation and embedding tool for videos using Deepgram's speech recognition.

## Description
Auto-Subber is a tool designed to automate the process of extracting audio from video files, transcribing the audio using Deepgram's speech recognition technology, generating subtitles in SRT format, and embedding these subtitles back into the video.

## Features
- Extract audio from video files.
- Transcribe audio to text using Deepgram's SDK.
- Generate subtitles in SRT format.
- Embed subtitles back into the video.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
python auto_subber.py 'path/to/your/video.mp4'
```

## Dependencies
- Python 3.10+
- FFmpeg must be installed and available in the system's PATH.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
