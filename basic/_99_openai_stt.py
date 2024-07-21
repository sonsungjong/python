from openai import OpenAI
client = OpenAI(api_key='key')

audio_file= open("D:\\너에게난.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file,
  response_format="text"
)

print(transcription)

# pip install openai