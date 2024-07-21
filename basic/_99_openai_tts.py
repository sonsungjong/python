from pathlib import Path
from openai import OpenAI
client = OpenAI(api_key='key')

speech_file_path = Path(__file__).parent / "myfile3.mp3"

with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input="""
    안녕하세요
    TTS 샘플입니다
    """,
) as response:
    response.stream_to_file(speech_file_path)