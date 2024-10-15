import os
import torch
from transformers import pipeline

if not torch.cuda.is_available():
    raise EnvironmentError("GPU가 필요합니다. 현재 시스템에서 GPU를 사용할 수 없습니다.")

os.environ["HUGGINGFACE_HUB_TOKEN"] = "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"

model_id = "meta-llama/Llama-3.2-3B-Instruct"

pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# conversation = input('입력하세요>> ')

messages = [
    {"role": "system", "content": "Translate Korean to English."},
    {"role": "user", "content": f"안녕하세요, 반갑습니다."},
]

outputs = pipe(
    messages,
    max_new_tokens=256,
)

print(outputs[0]["generated_text"][-1])

# 세부사항, 추론능력, 창의력, 응용력이 모델 파라미터 크기에 따라 차이가 난다.