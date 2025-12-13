# https://huggingface.co/openai/whisper-large-v3

# pip install --upgrade pip
# pip install --upgrade transformers datasets[audio] accelerate
# sudo apt update && sudo apt install -y ffmpeg
# pip install flash-attn --no-build-isolation (선택)

# 30초가 넘는 파일은 chunk_length_s=30 설정 필수 및 batch_size 조정

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    chunk_length_s=30,
    batch_size=16,
)

# 공식 샘플
# dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
# sample = dataset[0]["audio"]
# result = pipe(sample, return_timestamps=True)
# print(result["text"])

# 한국어 받아쓰기 (STT)
# result = pipe("audio.mp3", generate_kwargs={"language": "korean"})
result = pipe("audio.wav", generate_kwargs={"language": "korean"})
print(result["text"])

# 한국어 음성을 영어로 번역
# result = pipe("audio.mp3", generate_kwargs={"language": "korean", "task": "translate"})
# print(result["text"])