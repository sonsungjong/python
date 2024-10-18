import torch
from transformers import pipeline

model_id = "meta-llama/Llama-3.2-1B-Instruct"
pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]
outputs = pipe(
    messages,
    max_new_tokens=256,
)
print(outputs[0]["generated_text"][-1])


# https://lonaru-burnout.tistory.com/16    (CUDA와 cuDNN 설치)
# pip install transformers torch accelerate>=0.26.0
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124