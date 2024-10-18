import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

if not torch.cuda.is_available():
    raise EnvironmentError("GPU가 필요합니다. 현재 시스템에서 GPU를 사용할 수 없습니다.")

model_id = 'Bllossom/llama-3.2-Korean-Bllossom-3B'

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
).to('cuda')  # 모델을 GPU로 이동

instruction = input('입력하세요>> ')

messages = [
    {"role": "system", "content": "Translate Korean to English."},
    {"role": "user", "content": f"{instruction}"}
]

input_ids = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt"
).to('cuda')  # 입력 데이터를 GPU로 이동

terminators = [
    tokenizer.convert_tokens_to_ids("<|end_of_text|>"),
    tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

outputs = model.generate(
    input_ids,
    max_new_tokens=1024,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9
)

print(tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True))

# https://lonaru-burnout.tistory.com/16    (CUDA와 cuDNN 설치)
# pip install transformers torch accelerate>=0.26.0
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124