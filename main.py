import os
import subprocess
import json
import datetime
import tempfile
from dotenv import load_dotenv
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv('DEEPGRAM_API_KEY')
MAX_CHARS_PER_LINE = 60

def extract_audio(video_path: str, audio_output_path: str):
    """Extracts the audio from a video file and saves it as an AAC file."""
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vn',
        '-acodec', 'aac',
        '-b:a', '192k',
        audio_output_path
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Audio extracted successfully to {audio_output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while extracting audio: {e}")

def format_time(seconds: float) -> str:
    """Converts seconds into SRT time format."""
    td = datetime.timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def generate_srt(words: list) -> str:
    """Generates SRT content from a list of word objects."""
    srt_content = []
    entry_number = 1
    start_time = None
    end_time = None
    text_line = ""

    for word in words:
        if start_time is None:
            start_time = word['start']

        proposed_line = f"{text_line} {word['punctuated_word']}".strip()
        if len(proposed_line) <= MAX_CHARS_PER_LINE:
            text_line = proposed_line
            end_time = word['end']
        else:
            srt_content.append(
                f"{entry_number}\n{format_time(start_time)} --> {format_time(end_time)}\n{text_line}\n"
            )
            entry_number += 1
            start_time = word['start']
            end_time = word['end']
            text_line = word['punctuated_word']

    if text_line:
        srt_content.append(
            f"{entry_number}\n{format_time(start_time)} --> {format_time(end_time)}\n{text_line}\n"
        )

    return "\n".join(srt_content)

def transcribe_audio(audio_file: str) -> list:
    """Transcribes audio to text using the Deepgram API."""
    try:
        deepgram = DeepgramClient(API_KEY)
        with open(audio_file, "rb") as file:
            payload = {"buffer": file.read()}

        options = PrerecordedOptions(model="nova-2", smart_format=True, diarize=True)
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        result = json.loads(response.to_json(indent=4))

        words = []
        for channel in result['results']['channels']:
            for paragraph in channel['alternatives']:
                for word_info in paragraph['words']:
                    words.append(word_info)

        return words
    except Exception as e:
        print(f"Exception: {e}")

def main(video_path: str):
    """Main function to process video file and add subtitles."""
    output_video_path = video_path.replace('.mp4', '_subtitled.mp4')
    with tempfile.NamedTemporaryFile(suffix='.aac', delete=False) as audio_tmp, \
         tempfile.NamedTemporaryFile(suffix='.srt', delete=False) as subtitle_tmp:
        
        audio_path = audio_tmp.name
        subtitle_path = subtitle_tmp.name

        extract_audio(video_path, audio_path)
        transcripts = transcribe_audio(audio_path)
        if transcripts:
            srt_text = generate_srt(transcripts)
            with open(subtitle_path, 'w') as f:
                f.write(srt_text)
            print("SRT file created successfully.")
            
            command = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"subtitles={subtitle_path}",
                '-c:v', 'libx264',
                '-crf', '23',
                '-preset', 'fast',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-strict', 'experimental',
                output_video_path
            ]
            try:
                subprocess.run(command, check=True)
                print("Subtitles added successfully and saved to " + output_video_path)
            except subprocess.CalledProcessError as e:
                print(f"Failed to add subtitles: {e}")

    os.unlink(audio_path)
    os.unlink(subtitle_path)

if __name__ == "__main__":
    # Example usage:
    main('path/to/video.mp4')
